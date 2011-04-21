
import unittest
import foo.google_checkout
from google.appengine.ext import testbed
from foo.models import *

class Test_Google_New_Order_Notification(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.AddNotification()

    def tearDown(self):
        self.testbed.deactivate()

    def testGoogleResponseParser(self):
        """ Testing the google response parser for a new order notification """

        notification_dict = foo.google_checkout.parse_google_response(self.notification)
        self.assertTrue(notification_dict)

        self.assertTrue(notification_dict['type'] == 'new-order-notification')
        self.assertTrue(notification_dict['cart-key'] == 'agtmb29qYWx3b3JsZHIKCxIEQ2FydBhXDA')
        self.assertTrue(notification_dict['google-order-number'] == '529653432629116')
        self.assertTrue(notification_dict['merchant-item-id'] == '87' )
        self.assertTrue(notification_dict['quantity'] == '1')

    def testProcessingNewOrderNotification(self):
        notification_dict = foo.google_checkout.parse_google_response(self.notification)
        cart = Cart(price = 24.00, number_of_days=365)
        cart.put()
        notification_dict['cart-key'] =cart.key()
        
        notification_processed = foo.google_checkout.new_order_notification(notification_dict)

        self.assertTrue(notification_processed)
        purchase = Purchase.all().filter("google_order_number =", int(notification_dict['google-order-number'])).get()
        cart = Cart.get(notification_dict['cart-key'])
        self.assertTrue(purchase)
        self.assertTrue(purchase.google_order_number == int(notification_dict['google-order-number']))

        self.assertTrue(cart.status == 'Order Received')
        

    def AddNotification(self):
        self.notification = """<?xml version="1.0" encoding="UTF-8"?>
<new-order-notification xmlns="http://checkout.google.com/schema/2" serial-number="529653432629116-00001-7">
  <buyer-billing-address>
    <email>SandboxBuyer@foojal.com</email>
    <contact-name>Buyer Sandbox</contact-name>
    <company-name></company-name>
    <phone>480 236-2455</phone>
    <fax></fax>
    <address1>4465 E Kachina Trail</address1>
    <address2></address2>
    <structured-name>
      <first-name>Buyer</first-name>
      <last-name>Sandbox</last-name>
    </structured-name>
    <city>Phoenix</city>
    <region>AZ</region>
    <postal-code>85044</postal-code>
    <country-code>US</country-code>
  </buyer-billing-address>
  <timestamp>2011-04-20T19:47:58.492Z</timestamp>
  <google-order-number>529653432629116</google-order-number>
  <order-summary>
    <total-chargeback-amount currency="USD">0.0</total-chargeback-amount>
    <google-order-number>529653432629116</google-order-number>
    <total-charge-amount currency="USD">0.0</total-charge-amount>
    <total-refund-amount currency="USD">0.0</total-refund-amount>
    <purchase-date>2011-04-20T19:47:58.000Z</purchase-date>
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
          <merchant-item-id>87</merchant-item-id>
        </item>
      </items>
      <merchant-private-data>
        <cart-key>agtmb29qYWx3b3JsZHIKCxIEQ2FydBhXDA</cart-key>
      </merchant-private-data>
    </shopping-cart>
    <order-adjustment>
      <merchant-codes />
      <total-tax currency="USD">0.0</total-tax>
      <adjustment-total currency="USD">0.0</adjustment-total>
    </order-adjustment>
    <buyer-id>644068786438005</buyer-id>
    <buyer-shipping-address>
      <email>SandboxBuyer@foojal.com</email>
      <contact-name>Buyer Sandbox</contact-name>
      <company-name></company-name>
      <phone>480 236-2455</phone>
      <fax></fax>
      <address1>4465 E Kachina Trail</address1>
      <address2></address2>
      <structured-name>
        <first-name>Buyer</first-name>
        <last-name>Sandbox</last-name>
      </structured-name>
      <city>Phoenix</city>
      <region>AZ</region>
      <postal-code>85044</postal-code>
      <country-code>US</country-code>
    </buyer-shipping-address>
    <buyer-marketing-preferences>
      <email-allowed>false</email-allowed>
    </buyer-marketing-preferences>
    <promotions />
    <order-total currency="USD">24.0</order-total>
    <fulfillment-order-state>NEW</fulfillment-order-state>
    <financial-order-state>REVIEWING</financial-order-state>
  </order-summary>
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
        <merchant-item-id>87</merchant-item-id>
      </item>
    </items>
    <merchant-private-data>
      <cart-key>agtmb29qYWx3b3JsZHIKCxIEQ2FydBhXDA</cart-key>
    </merchant-private-data>
  </shopping-cart>
  <order-adjustment>
    <merchant-codes />
    <total-tax currency="USD">0.0</total-tax>
    <adjustment-total currency="USD">0.0</adjustment-total>
  </order-adjustment>
  <buyer-id>644068786438005</buyer-id>
  <buyer-shipping-address>
    <email>SandboxBuyer@foojal.com</email>
    <contact-name>Buyer Sandbox</contact-name>
    <company-name></company-name>
    <phone>480 236-2455</phone>
    <fax></fax>
    <address1>4465 E Kachina Trail</address1>
    <address2></address2>
    <structured-name>
      <first-name>Buyer</first-name>
      <last-name>Sandbox</last-name>
    </structured-name>
    <city>Phoenix</city>
    <region>AZ</region>
    <postal-code>85044</postal-code>
    <country-code>US</country-code>
  </buyer-shipping-address>
  <buyer-marketing-preferences>
    <email-allowed>false</email-allowed>
  </buyer-marketing-preferences>
  <promotions />
  <order-total currency="USD">24.0</order-total>
  <fulfillment-order-state>NEW</fulfillment-order-state>
  <financial-order-state>REVIEWING</financial-order-state>
</new-order-notification>"""