Configuration
#############

All the configuration of the processor lives in the ``EOX_PAYGATE_SETTINGS`` dict. zeitlabs reads it with
``configuration_helpers.get_value``, from the configuration of the current site or, when the site does not set it,
from the Django settings:

- Set it in the Django settings to configure Paygate for the whole installation.
- Set it in a site's configuration to configure Paygate for that site.

The processor is offered at checkout only on sites where every required key holds a value.

Required keys
*************

.. list-table::
   :header-rows: 1

   * - Key
     - Description
   * - ``API_BASE_URL``
     - Base URL of the Paygate REST API, without a trailing slash, e.g. ``https://<paygate host>/paygateWS``. No
       Paygate URL is built into the code: it decides whether the site talks to Paygate's test or production
       environment.
   * - ``ACCESS_TOKEN``
     - Access token of the merchant, sent in the body of every request to Paygate.
   * - ``MERCHANT_CODE``
     - Code of the merchant, sent in the body of every request to Paygate.
   * - ``BASIC_AUTH_USER``
     - User of the HTTP Basic authentication of the Paygate API.
   * - ``BASIC_AUTH_PASSWORD``
     - Password of the HTTP Basic authentication of the Paygate API.
   * - ``CALLBACK_KEY``
     - Callback key configured for the merchant in Paygate, which Paygate sends in every server callback.

Optional keys
*************

.. list-table::
   :header-rows: 1

   * - Key
     - Description
   * - ``PAYMENT_TYPES``
     - Payment types offered on Paygate's hosted payment page. Defaults to
       ``['VISA', 'MASTERCARD', 'AMEX', 'PAYPAL', 'MBWAY', 'REFMB', 'DUC']``. Offer only the types the merchant has
       enabled in Paygate.
   * - ``TIMEOUT``
     - Seconds to wait for each answer of the Paygate API. Defaults to ``20``.

Example::

    EOX_PAYGATE_SETTINGS = {
        'API_BASE_URL': 'https://<paygate host>/paygateWS',
        'ACCESS_TOKEN': '<access token>',
        'MERCHANT_CODE': '<merchant code>',
        'BASIC_AUTH_USER': '<user>',
        'BASIC_AUTH_PASSWORD': '<password>',
        'CALLBACK_KEY': '<callback key>',
    }
