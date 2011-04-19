import base64

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError
from xml.dom import minidom

import models
import settings
#import emails

def amount_notification(notification_dict):
    "Charge the purchase and give the user access to the files."
    purchase = models.Purchase.all().filter("google_order_number =", int(notification_dict['google-order-number'])).get()
    errors = [purchase.errors]
    if purchase:#add charge amount and expiration date, charge date
        purchase.purchase_charged(notification_dict['total-charge-amount'])
    else: #orphan amount notification - just in case
        errors.append('no previous notification for this order')
        purchase_key = models.generate_purchase_key()
        purchase_id = int(purchase_key.split('-')[0])
        purchase = models.Purchase(key_name = purchase_key, errors = errors, purchase_id = purchase_id, google_order_number = int(notification_dict['google-order-number']))
        purchase.purchase_charged(notification_dict['total-charge-amount'])
    user = purchase.user #change user purchase access attribute
    session = None
    if user: #Google user associated with purchase
        user.purchase_access = True
        user.put()
        session = models.Session.all().filter('user =', user).get() #check if user is logged in
        if session is not None: session.delete()
    if session is None: #no Google user or user Google is not logged in
        google_order_number = int(notification_dict['google-order-number'])
        session = models.Session.all().filter('google_order_number =', google_order_number).get()
        if session is not None:
            session.load_values() #need to load values in order to update them
            session.add_purchase(purchase)
            session.put()
    emails.mail_user_purchase(purchase.purchase_email, str(purchase.key().name()))
    if errors:
        purchase.errors = models.build_string_from_list(errors, '\n')
        purchase.put()
    return True

def check_auth(merchant_id, merchant_key):
    "Check to ensure valid Google notification."
    if merchant_id == settings.MERCHANT_ID and merchant_key == settings.MERCHANT_KEY:
        return True
    else: return False

def get_list_from_value(notification_value):
    "Checks to see if value in notification dict is a list or unicode. Returns list of value(s) as integers."
    if type(notification_value) == list:
        return [ int(x) for x in notification_value ]
    else: return [int(notification_value)]

def manipulate_notification(notification_dict):
    "Only process new orders and amount notifications. Only handshake if notification is processed successfully."
    notification_processed = False
    if notification_dict['type'] == 'new-order-notification': #new order
        notification_processed = new_order_notification(notification_dict)
    elif notification_dict['type'] == 'risk-information-notification':
        notification_processed = True
    elif notification_dict['type'] == 'order-state-change-notification':
        notification_processed = True
    elif notification_dict['type'] == 'charge-amount-notification':
        notification_processed = amount_notification(notification_dict)
    #all other notifications are ignored
    else: pass
    if notification_processed: return True
    return False

def new_order_notification(notification_dict):
    "Create Purchase and PurchaseItems, but don't give access until the purchase is charged/amount notification received."
    #make sure this notification hasn't already been processed
    purchase = models.Purchase.all().filter("google_order_number =", int(notification_dict['google-order-number'])).get()
    session = models.Session.get_by_key_name(notification_dict['session-key-name'])
    email = notification_dict['email']
    if session is not None: #session dict will be empty, so we need this test
        session.load_values()
        if 'cart' in session:
            del session['cart'] #remove the purchased cart
            session['number_cart_items'] = 0
        if session.has_user(): user = session.user
        else: user = None
        session.google_order_number = int(notification_dict['google-order-number'])
        session.put()
    else: user = None
    errors = ''
    if not user: user = models.User().all().filter('email =', email).get()
    if not purchase:
        purchase_key = models.generate_purchase_key()
        purchase_id = int(purchase_key.split('-')[0]) #get the id from the beginning of the key
        purchase = models.Purchase(
                                   key_name = purchase_key,
                                   purchase_email = email, #give the purchase the shipping email address
                                   purchase_id = purchase_id,
                                   user = user,
                                   google_order_number = int(notification_dict['google-order-number']),
                                   )
    if session is None: #session wasn't found - unlikely
        errors = 'session not found'
    if errors:
        purchase.errors = errors
    purchase.put() #need to add purchase to the datastore before we can add purchase items
    #get all the items from the notification_dict and add to the purchase
    item_ids = get_list_from_value(notification_dict['merchant-item-id'])
    quantities = get_list_from_value(notification_dict['quantity'])
    item_dict = dict(zip(item_ids, quantities))
    purchase.add_purchase_items(item_dict, user)
    return True

def parse_google_response(notification):
    "All google notifications are parsed and categorized by type."
    dom = minidom.parseString(notification)
    notification_type = dom.childNodes[0].localName #get the notification type
    #use this dictionary to determine which items will be taken from the notification
    notification_type_dict = {
                       'new-order-notification' : settings.NEW_ORDER_NOTIFICATION,
                       'risk-information-notification' : settings.RISK_INFORMATION_NOTIFICATION,
                       'order-state-change-notification' : settings.ORDER_STATE_CHANGE_NOTIFICATION,
                       'charge-amount-notification' : settings.AMOUNT_NOTIFICATION,
                       'refund-amount-notification' : settings.AMOUNT_NOTIFICATION,
                       }
    notification_dict = {} #notification dict
    notification_dict['type'] = notification_type
    #get the serial number
    serial_node = dom.childNodes[0].attributes["serial-number"]
    notification_dict['serial-number'] = serial_node.value
    #to get the shipping email ONLY (there may be other emails included as well)
    if notification_type == 'new-order-notification':
        try:
            node = dom.getElementsByTagName('buyer-shipping-address')
            email = node[0].getElementsByTagName('email')[0].firstChild.data
        except:
            email = dom.getElementsByTagName('email')[0].firstChild.data
        notification_dict['email'] = str(email)
    #pass the xml data to the dictionary
    for dict_name in notification_type_dict[notification_type]:
        try:
            node = dom.getElementsByTagName(dict_name) #[0].firstChild.data
            #add all nodes if there are multiple
            data_length = len(node)
            if data_length > 1:
                i = 0
                data_list = []
                while i < data_length:
                    data_list.append(node[i].firstChild.data)
                    i = i + 1
                notification_dict[dict_name] = data_list
            else:
                notification_dict[dict_name] = node[0].firstChild.data
        except:
            pass
    return notification_dict
    dom.unlink()
    return

def post_shopping_cart(session):
    doc = minidom.Document() #minidom object creation
    #checkout-shopping-cart
    checkout_shopping_cart = doc.createElement("checkout-shopping-cart")
    checkout_shopping_cart.setAttribute("xmlns","http://checkout.google.com/schema/2")
    doc.appendChild(checkout_shopping_cart)
    #shopping-cart
    shopping_cart = doc.createElement("shopping-cart")
    checkout_shopping_cart.appendChild(shopping_cart)
    #merchant-private-data
    merchant_private_data = doc.createElement("merchant-private-data")
    shopping_cart.appendChild(merchant_private_data)
    #session-key-name
    session_key_name = doc.createElement("session-key-name")
    merchant_private_data.appendChild(session_key_name)
    session_key_name_text = doc.createTextNode(str(session.key().name()))
    session_key_name.appendChild(session_key_name_text)
    #items
    items = doc.createElement("items")
    shopping_cart.appendChild(items)
    products = models.Product.get(session['cart'].keys())
    for product in products:
        #item
        item = doc.createElement("item")
        items.appendChild(item)
        #merchant-item-id
        merchant_item_id = doc.createElement("merchant-item-id")
        item.appendChild(merchant_item_id)
        item_id = str(product.key().id())
        merchant_item_id_text = doc.createTextNode(item_id)
        merchant_item_id.appendChild(merchant_item_id_text)
        #item-name
        item_name = doc.createElement("item-name")
        item.appendChild(item_name)
        item_name_text = doc.createTextNode(product.title)
        item_name.appendChild(item_name_text)
        #item-description
        item_description = doc.createElement("item-description")
        item.appendChild(item_description)
        item_description_text = doc.createTextNode(str(product.description))
        item_description.appendChild(item_description_text)
        #unit-price
        unit_price = doc.createElement("unit-price")
        unit_price.setAttribute("currency", "USD")
        item.appendChild(unit_price)
        unit_price_text = doc.createTextNode(str(product.price))
        unit_price.appendChild(unit_price_text)
        #quantity
        quantity = doc.createElement("quantity")
        item.appendChild(quantity)
        quantity_text = doc.createTextNode(str(session['cart'][str(product.key())]))
        quantity.appendChild(quantity_text)
        #digital content - child of item
        digital_content = doc.createElement("digital-content")
        item.appendChild(digital_content)
        #display disposition - child of above
        display_disposition = doc.createElement("display-disposition")
        digital_content.appendChild(display_disposition)
        display_disposition_text = doc.createTextNode("PESSIMISTIC")
        display_disposition.appendChild(display_disposition_text)

        #description - child of digital content
        description = doc.createElement("description")
        digital_content.appendChild(description)
        description_text = doc.createTextNode(product.title + ': ' + settings.DOWNLOAD_INSTRUCTIONS)
        description.appendChild(description_text)

    #checkout-flow-support
    checkout_flow_support = doc.createElement("checkout-flow-support")
    checkout_shopping_cart.appendChild(checkout_flow_support)
    #merchant-checkout-flow-support
    merchant_checkout_flow_support = doc.createElement("merchant-checkout-flow-support")
    checkout_flow_support.appendChild(merchant_checkout_flow_support)
    #create xml file
    new_order = doc.toxml(encoding="utf-8")
    #create authorization string
    auth_string = 'Basic ' + base64.b64encode(settings.MERCHANT_ID + ':' + settings.MERCHANT_KEY)
    #urlfetch POST the shopping cart to Google; try twice before failing
    i = 2 #try to post the cart twice before returning an error message
    while i > 0:
        i -= 1
        try:
            result = urlfetch.fetch(settings.GOOGLE_URL, headers={'Content-Type': 'application/xml; charset=UTF-8', 'Accept': 'application/xml; charset=UTF-8','Authorization' : auth_string}, payload=new_order, method=urlfetch.POST)
            i = 0
        except DownloadError:
            if i == 0: return False
    doc.unlink() #remove the doc from memory
    if result.status_code == 200: #make sure we get a 200 status code from Google
        #parse returned data from Google
        dom = minidom.parseString(result.content)
        #check to see if we received the redirect
        try:
            redirect_url = dom.getElementsByTagName('redirect-url')[0].firstChild.data
            return redirect_url
        except:
            return False
        #Remove from memory
        dom.unlink()
    else:
        return False

class GoogleListener(webapp.RequestHandler):
    def handshake(self, serial_number):
        "Acknowledge receipt of notification."
        doc = minidom.Document() #minidom object creation
        notification_acknowledgment = doc.createElement("notification-acknowledgment")
        notification_acknowledgment.setAttribute("xmlns","http://checkout.google.com/schema/2")
        notification_acknowledgment.setAttribute("serial-number", serial_number)
        doc.appendChild(notification_acknowledgment)
        acknowledgment = doc.toxml(encoding="utf-8")
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(acknowledgment)
        return

    def post(self):
        if self.request.headers.get('Authorization'):
            #get the Authorization string from the Google POST header
            auth_string = self.request.headers.get('Authorization')
            #decode the Authorization string and remove Basic portion
            plain_string = base64.b64decode(auth_string.lstrip('Basic '))
            #split the decoded string at the ':'
            split_string = plain_string.split(':')
            merchant_id = split_string[0]
            merchant_key = split_string[1]

            if check_auth(merchant_id, merchant_key) and self.request.body:
                notification = self.request.body
                notification_dict = parse_google_response(notification)
                if manipulate_notification(notification_dict): #handshake only if notification successfully processed
                    self.handshake(notification_dict['serial-number'])
            else: self.error(401)
        else: self.error(401)
        return

