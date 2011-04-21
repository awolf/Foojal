import unittest
import foo.google_checkout
from google.appengine.ext import testbed
from foo.models import *

class Test_Google_Amount_Charged_Notification(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.AddNotification()

    def tearDown(self):
        self.testbed.deactivate()

    def testProcessingAmountCharged(self):
        notification_dict = foo.google_checkout.parse_google_response(self.notification)
        
        cart = Cart(price = 24.00, number_of_days=365)
        cart.put()
        notification_dict['cart-key'] = cart.key()

        purchase_key = generate_purchase_key()
        purchase_id = int(purchase_key.split('-')[0])
        purchase = Purchase(
                           key_name = purchase_key,
                           purchase_email = notification_dict['email'],
                           purchase_id = purchase_id,
                           user = cart.user,
                           google_order_number = int(notification_dict['google-order-number']),
                           )
        purchase.item = str(notification_dict['merchant-item-id'])
        purchase.quantity = int(notification_dict['quantity'])
        purchase.put()

        purchase = Purchase.all().filter("google_order_number =", int(notification_dict['google-order-number'])).get()
        cart = Cart.get(notification_dict['cart-key'])
        self.assertTrue(purchase)
        self.assertTrue(purchase.google_order_number == int(notification_dict['google-order-number']))

        foo.google_checkout.amount_notification(notification_dict)

        self.assertTrue(cart.status == 'Order Received')


    def AddNotification(self):
        self.notification = """<?xml version="1.0" encoding="UTF-8"?>
<charge-amount-notification xmlns="http://checkout.google.com/schema/2" serial-number="755040043319808-00010-2">
  <timestamp>2011-04-20T23:51:10.001Z</timestamp>
  <latest-charge-amount currency="USD">24.0</latest-charge-amount>
  <latest-charge-fee>
    <total currency="USD">1.0</total>
    <percentage>2.9</percentage>
    <flat currency="USD">0.3</flat>
  </latest-charge-fee>
  <total-charge-amount currency="USD">24.0</total-charge-amount>
  <latest-promotion-charge-amount currency="USD">0.0</latest-promotion-charge-amount>
  <google-order-number>755040043319808</google-order-number>
  <order-summary>
    <total-chargeback-amount currency="USD">0.0</total-chargeback-amount>
    <google-order-number>755040043319808</google-order-number>
    <total-charge-amount currency="USD">24.0</total-charge-amount>
    <total-refund-amount currency="USD">0.0</total-refund-amount>
    <risk-information>
      <ip-address>70.176.244.226</ip-address>
      <billing-address>
        <email>awolf@foojal.com</email>
        <contact-name>Adam J Wolf</contact-name>
        <company-name></company-name>
        <phone>480 236-2455</phone>
        <fax></fax>
        <address1>4465 E KAchina Trail</address1>
        <address2></address2>
        <city>Phoenix</city>
        <region>AZ</region>
        <postal-code>85044</postal-code>
        <country-code>US</country-code>
      </billing-address>
      <avs-response>Y</avs-response>
      <cvn-response>M</cvn-response>
      <eligible-for-protection>true</eligible-for-protection>
      <partial-cc-number>1111</partial-cc-number>
      <buyer-account-age>0</buyer-account-age>
    </risk-information>
    <authorization>
      <authorization-amount currency="USD">24.0</authorization-amount>
      <authorization-expiration-date>2011-04-27T23:51:08.000Z</authorization-expiration-date>
    </authorization>
    <purchase-date>2011-04-20T23:51:07.000Z</purchase-date>
    <archived>false</archived>
    <shopping-cart>
      <items>
        <item>
          <digital-content>
            <description>One Year Subscription.: Your subscription to Foojal.com has been setup. Please check &lt;a href="http://FoojalWorld.appspot.com/account" target="_blank"&gt;http://FoojalWorld.appspot.&lt;WBR&gt;com/account&lt;/a&gt; to access your purchase.</description>
            <display-disposition>PESSIMISTIC</display-disposition>
          </digital-content>
          <item-name>One Year Subscription.</item-name>
          <item-description>Subscription to Foojal your photo food journal</item-description>
          <unit-price currency="USD">24.0</unit-price>
          <quantity>1</quantity>
          <merchant-item-id>65053</merchant-item-id>
        </item>
      </items>
      <merchant-private-data>
        <cart-key>agtmb29qYWx3b3JsZHIMCxIEQ2FydBid_AMM</cart-key>
      </merchant-private-data>
    </shopping-cart>
    <order-adjustment>
      <merchant-codes />
      <total-tax currency="USD">0.0</total-tax>
      <adjustment-total currency="USD">0.0</adjustment-total>
    </order-adjustment>
    <buyer-id>827169021848198</buyer-id>
    <buyer-shipping-address>
      <email>awolf@foojal.com</email>
      <contact-name>Adam J Wolf</contact-name>
      <company-name></company-name>
      <phone>480 236-2455</phone>
      <fax></fax>
      <address1>4465 E KAchina Trail</address1>
      <address2></address2>
      <structured-name>
        <first-name>Adam J</first-name>
        <last-name>Wolf</last-name>
      </structured-name>
      <city>Phoenix</city>
      <region>AZ</region>
      <postal-code>85044</postal-code>
      <country-code>US</country-code>
    </buyer-shipping-address>
    <buyer-marketing-preferences>
      <email-allowed>true</email-allowed>
    </buyer-marketing-preferences>
    <promotions />
    <order-total currency="USD">24.0</order-total>
    <fulfillment-order-state>PROCESSING</fulfillment-order-state>
    <financial-order-state>CHARGED</financial-order-state>
  </order-summary>
</charge-amount-notification>"""







