"""Paygate processor for openedx-zeitlabs-payments."""
from django.http import HttpRequest

from zeitlabs_payments.providers.base import BaseProcessor


# get_transaction_parameters is implemented in the future, together with the hand-off to Paygate.
class PaygateProcessor(BaseProcessor):  # pylint: disable=abstract-method
    """
    Paygate payment processor.

    Registered by zeitlabs through the ``zeitlabs_payments.v1`` entry point, under its ``SLUG``.
    """

    SLUG = 'paygate'
    NAME = 'Paygate'
    CHECKOUT_TEXT = 'Pay with Paygate'
    TEMPLATE_NAME = 'eox_paygate/payment.html'
    SETTINGS_ROOT_KEY = 'EOX_PAYGATE_SETTINGS'
    RETURN_VIEW = 'eox_paygate.views.PaygateReturnView'
    STATUS_VIEW = 'eox_paygate.views.PaygateStatusView'
    GATEWAY_ORDER_ID_PARAM = 'payment_ref'

    # Keys of ``EOX_PAYGATE_SETTINGS`` that must hold a value for Paygate to be enabled.
    REQUIRED_SETTINGS = (
        'API_BASE_URL',
        'ACCESS_TOKEN',
        'MERCHANT_CODE',
        'BASIC_AUTH_USER',
        'BASIC_AUTH_PASSWORD',
        'CALLBACK_KEY',
    )

    def is_enabled(self, _request: HttpRequest) -> bool:
        """
        Return whether ``EOX_PAYGATE_SETTINGS`` holds a value for every required key for the request's site.

        The settings are resolved for the site of the current request by ``configuration_helpers``, so the request
        itself is not read.
        """
        settings = self.get_settings()
        return all(settings.get(key) for key in self.REQUIRED_SETTINGS)

    def is_hidden_for(self, request: HttpRequest) -> bool:
        """Hide the processor in the checkout while it is not enabled for the request's site."""
        return not self.is_enabled(request)

    def get_gateway_order_id(self, transaction_parameters: dict) -> str:
        """Return the payment reference, which zeitlabs records as the cart's gateway order id."""
        return transaction_parameters['order_reference']
