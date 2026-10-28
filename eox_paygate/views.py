"""
Return and status views of the Paygate processor, mounted by zeitlabs under the processor's slug.
"""
from typing import Optional

from django.views import View

from zeitlabs_payments.models import Cart
from zeitlabs_payments.providers.mixins import PaymentReturnViewMixin, PaymentStatus, PaymentStatusViewMixin

from eox_paygate.processor import PaygateProcessor


class PaygateReturnView(PaymentReturnViewMixin, View):
    """Page the gateway sends the learner back to; it polls the status view."""

    processor_class = PaygateProcessor


class PaygateStatusView(PaymentStatusViewMixin, View):
    """Asks the gateway where the payment stands and settles it."""

    processor_class = PaygateProcessor

    def get_order_cart_reference(self, gateway_order_id: str) -> Optional[str]:
        """Return the merchant reference (``<site id>-<cart id>``) the gateway holds for the order."""
        raise NotImplementedError

    def get_order_status(self, gateway_order_id: str, cart: Cart) -> Optional[dict]:
        """Return the gateway's answer about the order."""
        raise NotImplementedError

    def get_payment_status(self, data: dict) -> Optional[PaymentStatus]:
        """Return where the gateway's answer says the payment stands."""
        raise NotImplementedError

    def verify_success_response(self, data: dict, cart: Cart) -> None:
        """
        Check that a success answer really pays for this cart.

        :raises GatewayError: When the answer does not pay for the cart.
        """
        raise NotImplementedError

    def get_transaction_details(self, data: dict, cart: Cart) -> Optional[dict]:
        """Return ``transaction_id``, ``method``, ``amount``, ``currency`` and ``reason`` of the payment."""
        raise NotImplementedError
