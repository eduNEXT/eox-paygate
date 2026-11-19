"""Tests for the hand-off of the learner to Paygate's hosted payment page."""
import base64
import json
import logging

import pytest
import requests
import responses
from common.djangoapps.student.models import UserProfile
from django.contrib.sites.models import Site
from django.test import RequestFactory

from zeitlabs_payments.exceptions import GatewayError

from eox_paygate.processor import PaygateProcessor
from tests.paygate_data import (
    CHECKOUT_ANSWER,
    CHECKOUT_URL,
    CREDENTIALS,
    DEFAULT_PAYMENT_TYPES,
    PAYGATE_SETTINGS,
    PAYMENT_PAGE_URL,
    SESSION_TOKEN,
)

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def paygate_settings(settings):
    """Configure Paygate for the platform."""
    settings.EOX_PAYGATE_SETTINGS = PAYGATE_SETTINGS


def hand_off(cart):
    """Hand the cart off to Paygate as zeitlabs does when the learner chooses Paygate at checkout."""
    request = RequestFactory().get('/')
    request.site = Site.objects.get_current()
    request.user = cart.user
    request.LANGUAGE_CODE = 'en'
    return PaygateProcessor().payment_view(cart, request)


def payment_reference(cart):
    """Return the payment reference of the cart: the site id and the cart id."""
    return f'{Site.objects.get_current().id}-{cart.id}'


def test_the_checkout_request_carries_the_cart_and_the_site_configuration(cart, checkout):
    """Handing a cart off sends Paygate a CheckOut request built from the cart and the site's configuration.

    Expected result:
    - The request goes to the CheckOut operation of the configured API base URL.
    - The request is authenticated with the configured Basic auth user and password.
    - The request body carries the merchant, the learner, the cart, the payment types and the return URLs.
    """
    hand_off(cart)

    request = checkout.calls[0].request
    return_url = (
        'http://example.com/payment/v1/processor/paygate/return/'
        f'?payment_reference={payment_reference(cart)}'
    )
    assert request.url == CHECKOUT_URL
    assert request.headers['Authorization'] == f'Basic {base64.b64encode(b"basic-user:basic-password").decode()}'
    assert json.loads(request.body) == {
        'ACCESS_TOKEN': 'access-token',
        'MERCHANT_CODE': 'merchant-code',
        'IS_RECURRENT': False,
        'PAYMENT_REF': payment_reference(cart),
        'CLIENT_NAME': 'Ana Maria Learner',
        'EMAIL': 'learner@example.com',
        'LANGUAGE': 'EN',
        'TRANSACTION_DESC': 'course-v1:org_course_run',
        'CURRENCY': 'EUR',
        'TOTAL_AMOUNT': 49.9,
        'PAYMENT_TYPES': DEFAULT_PAYMENT_TYPES,
        'CALLBACK_SUCCESS_URL': return_url,
        'CALLBACK_CANCEL_URL': return_url,
        'CALLBACK_FAILURE_URL': return_url,
        'CALLBACK_SERVER_URL': '',
    }


@pytest.mark.usefixtures('checkout')
def test_the_learner_is_redirected_to_the_hosted_payment_page(cart):
    """Handing a cart off redirects the learner to Paygate's hosted payment page with the session token.

    Expected result:
    - The response is a redirect.
    - The redirect goes to the URL Paygate answered, with the session token in the query string.
    """
    response = hand_off(cart)

    assert response.status_code == 302
    assert response['Location'] == f'{PAYMENT_PAGE_URL}?SessionToken={SESSION_TOKEN}'


@pytest.mark.usefixtures('checkout')
def test_the_payment_reference_is_recorded_as_the_gateway_order_id(cart):
    """Handing a cart off records the payment reference as the cart's gateway order id.

    Expected result:
    - The cart's gateway order id is its payment reference.
    """
    hand_off(cart)

    cart.refresh_from_db()
    assert cart.gateway_order_id == payment_reference(cart)


def test_the_configured_payment_types_are_offered(cart, checkout, settings):
    """The payment types configured in EOX_PAYGATE_SETTINGS replace the default ones.

    Expected result:
    - The CheckOut request offers only the configured payment types.
    """
    settings.EOX_PAYGATE_SETTINGS = {**PAYGATE_SETTINGS, 'PAYMENT_TYPES': ['MBWAY', 'REFMB']}

    hand_off(cart)

    assert json.loads(checkout.calls[0].request.body)['PAYMENT_TYPES'] == ['MBWAY', 'REFMB']


@pytest.mark.parametrize('profile_name', [
    pytest.param('', id='empty-profile-name'),
    pytest.param(None, id='no-profile'),
])
def test_the_learner_full_name_is_sent_without_a_profile_name(cart, checkout, profile_name):
    """Without a profile name, the learner's full name is sent as the client name.

    Expected result:
    - The CheckOut request's client name is the learner's first and last name.
    """
    if profile_name is None:
        UserProfile.objects.filter(user=cart.user).delete()
    else:
        UserProfile.objects.filter(user=cart.user).update(name=profile_name)
    cart.user.refresh_from_db()

    hand_off(cart)

    assert json.loads(checkout.calls[0].request.body)['CLIENT_NAME'] == 'Ana Learner'


@pytest.mark.parametrize('configured_timeout, timeout', [
    pytest.param({}, 20, id='default'),
    pytest.param({'TIMEOUT': 5}, 5, id='configured'),
])
def test_the_checkout_request_times_out(cart, checkout, settings, configured_timeout, timeout):
    """The CheckOut request waits for Paygate the configured TIMEOUT, or 20 seconds by default.

    Expected result:
    - The CheckOut request is sent with the expected timeout.
    """
    settings.EOX_PAYGATE_SETTINGS = {**PAYGATE_SETTINGS, **configured_timeout}

    hand_off(cart)

    assert checkout.calls[0].request.req_kwargs['timeout'] == timeout


@pytest.mark.parametrize('answer', [
    pytest.param({'body': requests.ConnectionError('connection refused')}, id='network-error'),
    pytest.param({'body': requests.Timeout('read timed out')}, id='timeout'),
    pytest.param({'status': 500, 'json': CHECKOUT_ANSWER}, id='not-200'),
    pytest.param({'body': 'not json'}, id='not-json'),
    pytest.param({'json': {**CHECKOUT_ANSWER, 'Success': False}}, id='not-successful'),
    pytest.param({'json': {key: value for key, value in CHECKOUT_ANSWER.items() if key != 'URL'}}, id='no-url'),
    pytest.param(
        {'json': {key: value for key, value in CHECKOUT_ANSWER.items() if key != 'SessionToken'}},
        id='no-session-token',
    ),
])
def test_a_failed_checkout_is_a_gateway_error_without_credentials(cart, caplog, answer):
    """A CheckOut that fails or answers without a hosted payment page is a gateway error that reveals no credential.

    Expected result:
    - Handing the cart off raises GatewayError.
    - The error message contains no credential.
    - The logs contain no credential.
    """
    caplog.set_level(logging.DEBUG)
    with responses.RequestsMock() as paygate:
        paygate.add(responses.POST, CHECKOUT_URL, **answer)

        with pytest.raises(GatewayError) as error:
            hand_off(cart)

    assert not [credential for credential in CREDENTIALS if credential in str(error.value)]
    assert not [credential for credential in CREDENTIALS if credential in caplog.text]


@pytest.mark.usefixtures('checkout')
def test_a_successful_checkout_logs_no_credential(cart, caplog):
    """Handing a cart off successfully logs no credential.

    Expected result:
    - The logs contain no credential.
    """
    caplog.set_level(logging.DEBUG)

    hand_off(cart)

    assert not [credential for credential in CREDENTIALS if credential in caplog.text]
