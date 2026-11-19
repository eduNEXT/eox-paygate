"""Return and status views of the Paygate processor, mounted by zeitlabs under the processor's slug."""
from django.views import View

from zeitlabs_payments.providers.mixins import PaymentReturnViewMixin, PaymentStatusViewMixin

from eox_paygate.processor import PaygateProcessor


class PaygateReturnView(PaymentReturnViewMixin, View):
    """Page the gateway sends the learner back to; it polls the status view."""

    processor_class = PaygateProcessor


class PaygateStatusView(PaymentStatusViewMixin, View):
    """Asks the gateway where the payment stands and settles it."""

    processor_class = PaygateProcessor
