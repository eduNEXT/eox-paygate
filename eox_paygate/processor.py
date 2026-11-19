"""Paygate processor for openedx-zeitlabs-payments."""
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Optional
from urllib.parse import urlencode

from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from zeitlabs_payments.helpers import relative_url_to_absolute_url
from zeitlabs_payments.models import Cart
from zeitlabs_payments.providers.base import BaseProcessor

from eox_paygate.client import PaygateClient

# Payment types offered on the hosted payment page when ``EOX_PAYGATE_SETTINGS`` sets no ``PAYMENT_TYPES``.
DEFAULT_PAYMENT_TYPES = ('VISA', 'MASTERCARD', 'AMEX', 'PAYPAL', 'MBWAY', 'REFMB', 'DUC')


class PaygateProcessor(BaseProcessor):
    """
    Paygate payment processor.

    Registered by zeitlabs through the ``zeitlabs_payments.v1`` entry point, under its ``SLUG``.
    """

    SLUG = 'paygate'
    NAME = 'Paygate'
    CHECKOUT_TEXT = 'Pay with Paygate'
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

    def get_transaction_parameters(
        self,
        cart: Cart,
        request: Optional[HttpRequest] = None,
        use_client_side_checkout: bool = False,
        **kwargs: Any,
    ) -> dict:
        """
        Open a Paygate payment session for the cart and return where to send the learner.

        Paygate sends the learner back to zeitlabs' return route after a success, a cancel or a failure alike; the
        status view decides the outcome.
        """
        base_parameters = self.get_transaction_parameters_base(cart, request)
        payment_reference = base_parameters['order_reference']
        paygate_settings = self.get_settings()
        return_url = (
            f'{relative_url_to_absolute_url(self.get_return_url(), request)}'
            f'?{urlencode({self.GATEWAY_ORDER_ID_PARAM: payment_reference})}'
        )
        answer = PaygateClient(paygate_settings).checkout({
            'IS_RECURRENT': False,
            'PAYMENT_REF': payment_reference,
            'CLIENT_NAME': get_client_name(cart.user),
            'EMAIL': base_parameters['user_email'],
            'LANGUAGE': base_parameters['language'].upper(),
            'TRANSACTION_DESC': base_parameters['order_description'],
            'CURRENCY': base_parameters['currency'],
            'TOTAL_AMOUNT': float(base_parameters['amount'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'PAYMENT_TYPES': list(paygate_settings.get('PAYMENT_TYPES', DEFAULT_PAYMENT_TYPES)),
            'CALLBACK_SUCCESS_URL': return_url,
            'CALLBACK_CANCEL_URL': return_url,
            'CALLBACK_FAILURE_URL': return_url,
            # Nothing serves Paygate's server callback yet; an empty URL tells Paygate not to send it.
            'CALLBACK_SERVER_URL': '',
        })
        return {
            self.GATEWAY_ORDER_ID_PARAM: payment_reference,
            'payment_page_url': answer['URL'],
            'session_token': answer['SessionToken'],
        }

    def payment_view(
        self,
        cart: Cart,
        request: Optional[HttpRequest] = None,
        use_client_side_checkout: bool = False,
        **kwargs: Any,
    ) -> HttpResponse:
        """
        Redirect the learner to Paygate's hosted payment page, with the session token Paygate opened for the cart.

        Replaces zeitlabs' rendered payment page, so it records the cart's gateway order as zeitlabs would.
        """
        transaction_parameters = self.get_transaction_parameters(
            cart=cart,
            request=request,
            use_client_side_checkout=use_client_side_checkout,
            **kwargs,
        )
        cart.record_gateway_order(self.SLUG, self.get_gateway_order_id(transaction_parameters))
        session_query = urlencode({'SessionToken': transaction_parameters['session_token']})
        return HttpResponseRedirect(f"{transaction_parameters['payment_page_url']}?{session_query}")

    def get_gateway_order_id(self, transaction_parameters: dict) -> str:
        """
        Return the payment reference, which zeitlabs records as the cart's gateway order id.

        The transaction parameters carry the payment reference under the same name as the return URL parameter.
        """
        return transaction_parameters[self.GATEWAY_ORDER_ID_PARAM]


def get_client_name(user: AbstractUser) -> str:
    """Return the learner's name for Paygate: the profile name, or the first and last name without one."""
    profile = getattr(user, 'profile', None)
    return getattr(profile, 'name', '') or user.get_full_name()
