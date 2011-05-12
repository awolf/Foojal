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

PIN_COLORS = ["black", "blue", "green", "grey", "purple", "red", "yellow"]

TAG_PUNCTUATION_BLACKLIST = """!"#$%&()*+,./:;<=>?@[\]^`{|}~"""

COUNTRY_TIMEZONES = [
            {'zone': 'United States', 'key': 'US/Alaska', 'value': 'Alaska'},
            {'zone': 'United States', 'key': 'America/Anchorage', 'value': 'Anchorage'},
            {'zone': 'United States', 'key': 'US/Arizona', 'value': 'Arizona'},
            {'zone': 'United States', 'key': 'America/Boise', 'value': 'Boise'},
            {'zone': 'United States', 'key': 'US/Central', 'value': 'Central'},
            {'zone': 'United States', 'key': 'America/Chicago', 'value': 'Chicago'},
            {'zone': 'United States', 'key': 'America/Detroit', 'value': 'Detroit'},
            {'zone': 'United States', 'key': 'America/Denver', 'value': 'Denver'},
            {'zone': 'United States', 'key': 'US/Eastern', 'value': 'Eastern'},
            {'zone': 'United States', 'key': 'US/Hawaii', 'value': 'Hawaii'},
            {'zone': 'United States', 'key': 'Pacific/Honolulu', 'value': 'Honolulu'},
            {'zone': 'United States', 'key': 'America/Los_Angeles', 'value': 'Los Angeles'},
            {'zone': 'United States', 'key': 'US/Michigan', 'value': 'Michigan'},
            {'zone': 'United States', 'key': 'US/Mountain', 'value': 'Mountain'},
            {'zone': 'United States', 'key': 'America/New_York', 'value': 'New York'},
            {'zone': 'United States', 'key': 'US/Pacific', 'value': 'Pacific'},
            {'zone': 'United States', 'key': 'America/Phoenix', 'value': 'Phoenix'},
            {'zone': 'Australia', 'key': 'Australia/Adelaide', 'value': 'Adelaide'},
            {'zone': 'Australia', 'key': 'Australia/Brisbane', 'value': 'Brisbane'},
            {'zone': 'Australia', 'key': 'Australia/Broken_Hill', 'value': 'Broken Hill'},
            {'zone': 'Australia', 'key': 'Australia/Currie', 'value': 'Currie'},
            {'zone': 'Australia', 'key': 'Australia/Darwin', 'value': 'Darwin'},
            {'zone': 'Australia', 'key': 'Australia/Eucla', 'value': 'Eucla'},
            {'zone': 'Australia', 'key': 'Australia/Hobart', 'value': 'Hobart'},
            {'zone': 'Australia', 'key': 'Australia/Lindeman', 'value': 'Lindeman'},
            {'zone': 'Australia', 'key': 'Australia/Lord_Howe', 'value': 'Lord Howe'},
            {'zone': 'Australia', 'key': 'Australia/Melbourne', 'value': 'Melbourne'},
            {'zone': 'Australia', 'key': 'Australia/Perth', 'value': 'Perth'},
            {'zone': 'Australia', 'key': 'Australia/Sydney', 'value': 'Sydney'},
            {'zone': 'Canada', 'key': 'Canada/Atlantic', 'value': 'Atlantic'},
            {'zone': 'Canada', 'key': 'Canada/Central', 'value': 'Central'},
            {'zone': 'Canada', 'key': 'Canada/East-Saskatchewan', 'value': 'East Saskatchewan'},
            {'zone': 'Canada', 'key': 'Canada/Eastern', 'value': 'Eastern'},
            {'zone': 'Canada', 'key': 'America/Montreal', 'value': 'Montreal'},
            {'zone': 'Canada', 'key': 'Canada/Mountain', 'value': 'Mountain'},
            {'zone': 'Canada', 'key': 'Canada/Newfoundland', 'value': 'Newfoundland'},
            {'zone': 'Canada', 'key': 'Canada/Pacific', 'value': 'Pacific'},
            {'zone': 'Canada', 'key': 'Canada/Saskatchewan', 'value': 'Saskatchewan'},
            {'zone': 'Canada', 'key': 'America/Toronto', 'value': 'Toronto'},
            {'zone': 'Canada', 'key': 'Canada/Yukon', 'value': 'Yokon'},
            {'zone': 'Canada', 'key': 'America/Vancouver', 'value': 'Vancouver'},
            {'zone': 'Europe', 'key': 'Europe/Amsterdam', 'value': 'Amsterdam'},
            {'zone': 'Europe', 'key': 'Europe/Athens', 'value': 'Athens'},
            {'zone': 'Europe', 'key': 'Europe/Belgrade', 'value': 'Belgrade'},
            {'zone': 'Europe', 'key': 'Europe/Berlin', 'value': 'Berlin'},
            {'zone': 'Europe', 'key': 'Europe/Brussels', 'value': 'Brussels'},
            {'zone': 'Europe', 'key': 'Europe/Copenhagen', 'value': 'Copenhagen'},
            {'zone': 'Europe', 'key': 'Europe/Dublin', 'value': 'Dublin'},
            {'zone': 'Europe', 'key': 'Europe/Gibraltar', 'value': 'Gibraltar'},
            {'zone': 'Europe', 'key': 'Europe/Helsinki', 'value': 'Helsinki'},
            {'zone': 'Europe', 'key': 'Europe/Kiev', 'value': 'Kiev'},
            {'zone': 'Europe', 'key': 'Europe/Lisbon', 'value': 'Lisbon'},
            {'zone': 'Europe', 'key': 'Europe/London', 'value': 'London'},
            {'zone': 'Europe', 'key': 'Europe/Luxembourg', 'value': 'Luxembourg'},
            {'zone': 'Europe', 'key': 'Europe/Madrid', 'value': 'Madrid'},
            {'zone': 'Europe', 'key': 'Europe/Malta', 'value': 'Malta'},
            {'zone': 'Europe', 'key': 'Europe/Minsk', 'value': 'Minsk'},
            {'zone': 'Europe', 'key': 'Europe/Monaco', 'value': 'Monaco'},
            {'zone': 'Europe', 'key': 'Europe/Moscow', 'value': 'Moscow'},
            {'zone': 'Europe', 'key': 'Europe/Oslo', 'value': 'Oslo'},
            {'zone': 'Europe', 'key': 'Europe/Paris', 'value': 'Paris'},
            {'zone': 'Europe', 'key': 'Europe/Prague', 'value': 'Prague'},
            {'zone': 'Europe', 'key': 'Europe/Rome', 'value': 'Rome'},
            {'zone': 'Europe', 'key': 'Europe/Stockholm', 'value': 'Stockholm'},
            {'zone': 'Europe', 'key': 'Europe/Vienna', 'value': 'Vienna'},
            {'zone': 'Europe', 'key': 'Europe/Warsaw', 'value': 'Warsaw'},
            {'zone': 'Europe', 'key': 'Europe/Zurich', 'value': 'Zurich'},
            {'zone': 'Pacific', 'key': 'Pacific/Auckland', 'value': 'Auckland'},
            {'zone': 'Pacific', 'key': 'Pacific/Fiji', 'value': 'Fiji'},
            {'zone': 'Pacific', 'key': 'Pacific/Galapagos', 'value': 'Galapagos'},
            {'zone': 'Pacific', 'key': 'Pacific/Guam', 'value': 'Guam'},
            {'zone': 'Pacific', 'key': 'Pacific/Midway', 'value': 'Midway'},
            {'zone': 'Pacific', 'key': 'Pacific/Norfolk', 'value': 'Norfolk'},
            {'zone': 'Pacific', 'key': 'Pacific/Tahiti', 'value': 'Tahiti'}
]




