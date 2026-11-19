"""Paygate data shared by the hand-off tests and their fixtures."""

API_BASE_URL = 'https://paygate.example.com/paygateWS'
CHECKOUT_URL = f'{API_BASE_URL}/api/CheckOut'
PAYGATE_SETTINGS = {
    'API_BASE_URL': API_BASE_URL,
    'ACCESS_TOKEN': 'access-token',
    'MERCHANT_CODE': 'merchant-code',
    'BASIC_AUTH_USER': 'basic-user',
    'BASIC_AUTH_PASSWORD': 'basic-password',
    'CALLBACK_KEY': 'callback-key',
}
CREDENTIALS = ['access-token', 'basic-password', 'callback-key']
COURSE_ID = 'course-v1:org+course+run'
PAYMENT_PAGE_URL = 'https://paygate.example.com/widget'
SESSION_TOKEN = 'session-token'
CHECKOUT_ANSWER = {
    'Success': True,
    'ReturnCode': '0',
    'URL': PAYMENT_PAGE_URL,
    'SessionToken': SESSION_TOKEN,
    'PaymentID': 1234,
}
DEFAULT_PAYMENT_TYPES = ['VISA', 'MASTERCARD', 'AMEX', 'PAYPAL', 'MBWAY', 'REFMB', 'DUC']
