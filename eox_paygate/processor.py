"""
Paygate processor for openedx-zeitlabs-payments.
"""
from typing import Any, Optional

from django.http import HttpRequest

from zeitlabs_payments.models import Cart
from zeitlabs_payments.providers.base import BaseProcessor


class PaygateProcessor(BaseProcessor):
    """
    Paygate payment processor.

    Registered by zeitlabs through the ``zeitlabs_payments.v1`` entry point, under its ``SLUG``.
    """

    SLUG = 'paygate'
    NAME = 'Paygate'
    CHECKOUT_TEXT = 'Pay with Paygate'
    TEMPLATE_NAME = 'eox_paygate/payment.html'
    SETTINGS_ROOT_KEY = 'PAYGATE_SETTINGS'
    RETURN_VIEW = 'eox_paygate.views.PaygateReturnView'
    STATUS_VIEW = 'eox_paygate.views.PaygateStatusView'
    GATEWAY_ORDER_ID_PARAM: Optional[str] = None

    def is_hidden_for(self, request: HttpRequest) -> bool:
        """Hide the processor in the checkout while ``PAYGATE_SETTINGS`` is not configured."""
        return not self.get_settings()

    def get_transaction_parameters(
        self,
        cart: Cart,
        request: Optional[HttpRequest] = None,
        use_client_side_checkout: bool = False,
        **kwargs: Any,
    ) -> dict:
        """Return the parameters the payment page sends to the gateway."""
        raise NotImplementedError

    def reconcile_payment(self, response: Optional[dict], cart: Cart) -> None:
        """
        Check that the money taken is what the cart expected.

        :raises GatewayError: When the amount or the currency does not match the cart.
        """
        raise NotImplementedError
