import os

try:
    DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')
except:
    DEBUG = True

ENABLE_DEBUG = True
SITE_DOWN_MESSAGE = "The website is currently undergoing maintenance  and will be back online shortly."
SITE_EMAIL = 'support@foojal.com'
SITE_NAME = "Foojal"
SITE_URL = 'http://FoojalWorld.appspot.com'
PURCHASE_ID_START = 999 #purchase id start number

MEMCACHE_LENGTH = 3600 #default memcache length in seconds
MEMCACHE_SESSION_LENGTH = 3600 #number of seconds to store memcache data

SAFE_FETCH_NUMBER = 300 #number of entities to fetch during large tasks

SESSION_LENGTH = 5 #session length in days

# Error messages
# ERROR_EMAIL = 'There are no purchases with that email address.'
# ERROR_EMAIL_LIMIT = 'Only one reminder email can be sent every 24 hours.'
# ERROR_GOOGLE_POST = 'An error occurred during checkout. Please try again.'
# ERROR_PRODUCT_PURCHASED = "This product has been purchased, so it can't be deleted."
# ERROR_QUANTITY = 'You may only add ' + str(MAX_QUANTITY_PER_ITEM) + ' of each item.'
# ERROR_KEY = 'Incorrect key. Make sure there are no spaces before or after your key.'
# ERROR_DICT = { 'email': ERROR_EMAIL, 'email_limit': ERROR_EMAIL_LIMIT, 'key': ERROR_KEY, 'google_post' : ERROR_GOOGLE_POST, 'quantity' : ERROR_QUANTITY, 'product_purchased' : ERROR_PRODUCT_PURCHASED }

# Notice messages
# NOTICE_EMAIL = 'Your purchase key has been emailed.'
# NOTICE_ITEM_USED = 'Unable to delete, because this product has been purchased.'
# NOTICE_PURCHASE_ADDED = 'Purchase added.'
# NOTICE_DICT = { 'email': NOTICE_EMAIL, 'item_used' : NOTICE_ITEM_USED, 'purchase': NOTICE_PURCHASE_ADDED }

#Google Checkout

# Test Accounts
# SandboxMerchant@foojal.com  bluecog.
# SandboxBuyer@foojal.com bluecog.

#MERCHANT_ID = ''
#MERCHANT_KEY = ''
MERCHANT_KEY = '4WgWqbfXUfXdqfAcIsDqWg' #sandbox
MERCHANT_ID = '620790402144452' #sandbox
GOOGLE_ANALYTICS_ACCOUNT = ''

#GOOGLE_URL = 'https://checkout.google.com/api/checkout/v2/merchantCheckout/Merchant/' + MERCHANT_ID
GOOGLE_URL = 'https://sandbox.google.com/checkout/api/checkout/v2/merchantCheckout/Merchant/' + MERCHANT_ID #sandbox

#Images
NO_IMAGE_URL = '/public/images/noimage.gif'
ALLOWED_IMAGE_EXTENSIONS = ('.jpg', '.JPG', '.jpeg', '.JPEG')

#Invitations
INVITATION_EMAIL = 'Invites@foojalworld.appspotmail.com'
INVITATION_SUBJECT = 'Your Foojal Invitation'
INVITATION_URL = 'http://foojalworld.appspot.com/invites/'
INVITATION_EMAIL_CONTENT = """
You have been invited to Foojal.com!

To accept this invitation, click the following link,
or copy and paste the URL into your browser's address
bar:

%s"""

#Google checkout text after successful transaction
DOWNLOAD_INSTRUCTIONS = 'Your subscription to Foojal.com has been setup. Please check ' + SITE_URL + '/account to access your purchase.'

NEW_ORDER_NOTIFICATION = [
        'cart-key',
        'google-order-number',
        'merchant-item-id',
        'quantity',
        ]

RISK_INFORMATION_NOTIFICATION = [
        'google-order-number',
        ]
ORDER_STATE_CHANGE_NOTIFICATION = [
        'google-order-number',
        ]
AMOUNT_NOTIFICATION = [
        'google-order-number',
        'total-charge-amount',
        ]
AMOUNT_CHARGED_NOTIFICATION = [
        'cart-key',
        'google-order-number',
        'total-charge-amount',
        ]

PIN_COLORS = ["black","blue","green","grey","purple","red","yellow"]

TAG_PUNCTUATION_BLACKLIST = """!"#$%&()*+,./:;<=>?@[\]^`{|}~"""
