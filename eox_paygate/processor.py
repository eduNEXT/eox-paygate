"""Paygate processor for openedx-zeitlabs-payments."""
from django.http import HttpRequest

from zeitlabs_payments.providers.base import BaseProcessor


# get_transaction_parameters will be implemented together with the hand-off to Paygate.
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
    GATEWAY_ORDER_ID_PARAM = 'payment_reference'

    # Keys of ``EOX_PAYGATE_SETTINGS`` that must hold a value for Paygate to be enabled.
    REQUIRED_SETTINGS = (
        'API_BASE_URL',
        'ACCESS_TOKEN',
        'MERCHANT_CODE',
        'BASIC_AUTH_USER',
        'BASIC_AUTH_PASSWORD',
        'CALLBACK_KEY',
    )

    def is_enabled(self) -> bool:
        """Return whether ``EOX_PAYGATE_SETTINGS`` holds a value for every required key for the current site."""
        paygate_settings = self.get_settings()
        return all(paygate_settings.get(key) for key in self.REQUIRED_SETTINGS)

    def is_hidden_for(self, request: HttpRequest) -> bool:
        """Hide the processor in the checkout while it is not enabled for the current site."""
        return not self.is_enabled()

    def get_gateway_order_id(self, transaction_parameters: dict) -> str:
        """
        Return the payment reference, which zeitlabs records as the cart's gateway order id.

        The transaction parameters carry the payment reference under the same name as the return URL parameter.
        """
        return transaction_parameters[self.GATEWAY_ORDER_ID_PARAM]
