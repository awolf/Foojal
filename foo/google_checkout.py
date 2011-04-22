import base64
from datetime import timedelta, datetime

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError
from xml.dom import minidom

import models
import settings
import logging


def get_list_from_value(notification_value):
    "Checks to see if value in notification dict is a list or unicode. Returns list of value(s) as integers."
    if type(notification_value) == list:
        return [int(x) for x in notification_value]
    else: return [int(notification_value)]


def amount_notification(notification_dict):
    "Charge the purchase and give the user access to the files."

    # Get the purchase object built from the new order notification
    purchase = models.Purchase.all().filter("google_order_number =",
                                            int(notification_dict['google-order-number'])).get()

    cart = models.Cart.get(notification_dict['cart-key'])

    if purchase:
        if purchase.processed: # this is a duplicate notification
            return True

        purchase.total_charge_amount = float(notification_dict['total-charge-amount'])
        purchase.charge_date = datetime.utcnow()
        if cart:
            purchase.number_of_days = cart.number_of_days
        purchase.put()
    else: #orphan amount notification - just in case
        purchase_key = models.generate_purchase_key()
        purchase_id = int(purchase_key.split('-')[0])

        purchase = models.Purchase(
            key_name=purchase_key,
            errors='no previous notification for this order',
            purchase_id=purchase_id,
            google_order_number=int(notification_dict['google-order-number']),
            total_charge_amount=float(notification_dict['total-charge-amount']),
            charge_date=datetime.utcnow()
        )
        purchase.put()
        return True

    account = models.Account.all().filter("user", cart.user).get()
    if account:
        account.expiration_date = account.expiration_date + timedelta(days=+cart.number_of_days)
        account.put()
        purchase.processed = True
        purchase.put()

    if cart:
        cart.delete()

    return True


def new_order_notification(notification_dict):
    google_order_number = int(notification_dict['google-order-number'])
    purchase = models.Purchase.all().filter("google_order_number =", google_order_number).get()
    cart = models.Cart.get(notification_dict['cart-key'])
    email = notification_dict['email']
    if cart is not None:
        cart.status = 'Order Received'
        cart.put()
    if not purchase:
        purchase_key = models.generate_purchase_key()
        purchase_id = int(purchase_key.split('-')[0]) #get the id from the beginning of the key
        purchase = models.Purchase(
            key_name=purchase_key,
            purchase_email=email,
            purchase_id=purchase_id,
            user=cart.user,
            google_order_number=google_order_number,
            )
    if cart is None: #cart wasn't found - unlikely
        purchase.errors = 'cart not found'

    purchase.item = str(notification_dict['merchant-item-id'])
    purchase.quantity = int(notification_dict['quantity'])
    purchase.put()
    return True


def parse_google_response(notification):
    "All google notifications are parsed and categorized by type."
    dom = minidom.parseString(notification)
    notification_type = dom.childNodes[0].localName #get the notification type
    logging.info('NotificationType :=' + notification_type)
    #use this dictionary to determine which items will be taken from the notification
    notification_type_dict = {
        'new-order-notification': settings.NEW_ORDER_NOTIFICATION,
        'risk-information-notification': settings.RISK_INFORMATION_NOTIFICATION,
        'order-state-change-notification': settings.ORDER_STATE_CHANGE_NOTIFICATION,
        'charge-amount-notification': settings.AMOUNT_CHARGED_NOTIFICATION,
        'refund-amount-notification': settings.AMOUNT_NOTIFICATION,
        'authorization-amount-notification': settings.AMOUNT_NOTIFICATION
    }
    notification_dict = {'type': notification_type} #notification dict
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
            node = dom.getElementsByTagName(dict_name)
            notification_dict[dict_name] = node[0].firstChild.data
        except:
            pass
    dom.unlink()
    return notification_dict


def post_shopping_cart(cart):
    doc = minidom.Document() #minidom object creation

    #checkout-shopping-cart
    checkout_shopping_cart = doc.createElement("checkout-shopping-cart")
    checkout_shopping_cart.setAttribute("xmlns", "http://checkout.google.com/schema/2")
    doc.appendChild(checkout_shopping_cart)

    #shopping-cart
    shopping_cart = doc.createElement("shopping-cart")
    checkout_shopping_cart.appendChild(shopping_cart)

    #merchant-private-data
    merchant_private_data = doc.createElement("merchant-private-data")
    shopping_cart.appendChild(merchant_private_data)

    #session-key-name
    cart_key = doc.createElement("cart-key")
    merchant_private_data.appendChild(cart_key)
    cart_key_text = doc.createTextNode(str(cart.key()))
    cart_key.appendChild(cart_key_text)
    # todo should we add the number of days to extend the subscription
    #items
    items = doc.createElement("items")
    shopping_cart.appendChild(items)

    #item
    item = doc.createElement("item")
    items.appendChild(item)

    #merchant-item-id
    merchant_item_id = doc.createElement("merchant-item-id")
    item.appendChild(merchant_item_id)
    item_id = str(cart.key().id())
    merchant_item_id_text = doc.createTextNode(item_id)
    merchant_item_id.appendChild(merchant_item_id_text)

    #item-name
    item_name = doc.createElement("item-name")
    item.appendChild(item_name)
    item_name_text = doc.createTextNode(cart.title)
    item_name.appendChild(item_name_text)

    #item-description
    item_description = doc.createElement("item-description")
    item.appendChild(item_description)
    item_description_text = doc.createTextNode(str(cart.description))
    item_description.appendChild(item_description_text)

    #unit-price
    unit_price = doc.createElement("unit-price")
    unit_price.setAttribute("currency", "USD")
    item.appendChild(unit_price)
    unit_price_text = doc.createTextNode(str(cart.price))
    unit_price.appendChild(unit_price_text)

    #quantity
    quantity = doc.createElement("quantity")
    item.appendChild(quantity)
    quantity_text = doc.createTextNode('1')
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
    description_text = doc.createTextNode(cart.title + ': ' + settings.DOWNLOAD_INSTRUCTIONS)
    description.appendChild(description_text)

    #checkout-flow-support
    checkout_flow_support = doc.createElement("checkout-flow-support")
    checkout_shopping_cart.appendChild(checkout_flow_support)

    #merchant-checkout-flow-support
    merchant_checkout_flow_support = doc.createElement("merchant-checkout-flow-support")
    checkout_flow_support.appendChild(merchant_checkout_flow_support)

    #create xml file
    new_order = doc.toxml(encoding="utf-8")
    cart.request = new_order
    cart.put()
    logging.info('New order test :\n' + new_order)

    #create authorization string
    auth_string = 'Basic ' + base64.b64encode(settings.MERCHANT_ID + ':' + settings.MERCHANT_KEY)

    #urlfetch POST the shopping cart to Google; try twice before failing
    i = 2 #try to post the cart twice before returning an error message
    result = ''
    while i > 0:
        i -= 1
        try:
            result = urlfetch.fetch(settings.GOOGLE_URL, headers={'Content-Type': 'application/xml; charset=UTF-8',
                                                                  'Accept': 'application/xml; charset=UTF-8',
                                                                  'Authorization': auth_string}, payload=new_order,
                                    method=urlfetch.POST)
            i = 0
        except DownloadError:
            if i == 0: return False
    doc.unlink() #remove the doc from memory
    if result.status_code == 200: #make sure we get a 200 status code from Google
        #parse returned data from Google
        dom = minidom.parseString(result.content)
        cart.response = result.content
        cart.put()
        #check to see if we received the redirect
        try:
            redirect_url = dom.getElementsByTagName('redirect-url')[0].firstChild.data
            dom.unlink()
            return redirect_url
        except:
            dom.unlink()
            return False
    else:
        return False


class GoogleListener(webapp.RequestHandler):
    def handshake(self, serial_number):
        "Acknowledge receipt of notification."
        doc = minidom.Document() #minidom object creation
        notification_acknowledgment = doc.createElement("notification-acknowledgment")
        notification_acknowledgment.setAttribute("xmlns", "http://checkout.google.com/schema/2")
        notification_acknowledgment.setAttribute("serial-number", serial_number)
        doc.appendChild(notification_acknowledgment)

        acknowledgment = doc.toxml(encoding="utf-8")
        models.save_communication(acknowledgment)

        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(acknowledgment)

        return

    def post(self):
        models.save_communication(self.request.body)
        if self.request.headers.get('Authorization'):
            #get the Authorization string from the Google POST header
            auth_string = self.request.headers.get('Authorization')
            #decode the Authorization string and remove Basic portion
            plain_string = base64.b64decode(auth_string.lstrip('Basic '))
            #split the decoded string at the ':'
            split_string = plain_string.split(':')
            merchant_id = split_string[0]
            merchant_key = split_string[1]

            if merchant_id == settings.MERCHANT_ID and merchant_key == settings.MERCHANT_KEY and self.request.body:
                notification = self.request.body
                notification_dict = parse_google_response(notification)

                notification_processed = False
                if notification_dict['type'] == 'new-order-notification':
                    notification_processed = new_order_notification(notification_dict)
                elif notification_dict['type'] == 'risk-information-notification':
                    notification_processed = True
                elif notification_dict['type'] == 'order-state-change-notification':
                    notification_processed = True
                elif notification_dict['type'] == 'charge-amount-notification':
                    notification_processed = amount_notification(notification_dict)
                elif notification_dict['type'] == 'authorization-amount-notification':
                    notification_processed = True
                else: pass #all other notifications are ignored

                if notification_processed:
                    self.handshake(notification_dict['serial-number'])
            else: self.error(401)
        else: self.error(401)
        return
