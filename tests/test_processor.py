"""Tests for the registration of the Paygate processor and its visibility at checkout."""
import pytest
from django.test import RequestFactory, override_settings
from django.utils.module_loading import import_string

from zeitlabs_payments.providers.registry import PROCESSORS

from eox_paygate.processor import PaygateProcessor

COMPLETE_SETTINGS = {
    'API_BASE_URL': 'https://paygate.example.com/paygateWS',
    'ACCESS_TOKEN': 'access-token',
    'MERCHANT_CODE': 'merchant-code',
    'BASIC_AUTH_USER': 'basic-user',
    'BASIC_AUTH_PASSWORD': 'basic-password',
    'CALLBACK_KEY': 'callback-key',
}


def test_zeitlabs_registers_the_paygate_processor_at_startup():
    """The package's entry point makes zeitlabs register the Paygate processor at startup.

    Expected result:
    - The zeitlabs processor registry maps the paygate slug to PaygateProcessor.
    """
    assert PROCESSORS.get('paygate') is PaygateProcessor


@override_settings(EOX_PAYGATE_SETTINGS=COMPLETE_SETTINGS)
def test_paygate_is_enabled_when_the_platform_settings_are_complete():
    """A complete EOX_PAYGATE_SETTINGS in the Django settings enables Paygate.

    Expected result:
    - is_enabled returns True for the request.
    """
    assert PaygateProcessor().is_enabled(RequestFactory().get('/'))


def test_paygate_is_not_enabled_without_configuration():
    """Without EOX_PAYGATE_SETTINGS Paygate is not enabled.

    Expected result:
    - is_enabled returns False for the request.
    """
    assert not PaygateProcessor().is_enabled(RequestFactory().get('/'))


@pytest.mark.parametrize('missing_key', sorted(COMPLETE_SETTINGS))
def test_paygate_is_not_enabled_when_a_required_key_is_missing(missing_key):
    """EOX_PAYGATE_SETTINGS without one of its required keys does not enable Paygate.

    Expected result:
    - is_enabled returns False for the request.
    """
    incomplete_settings = {key: value for key, value in COMPLETE_SETTINGS.items() if key != missing_key}
    with override_settings(EOX_PAYGATE_SETTINGS=incomplete_settings):
        assert not PaygateProcessor().is_enabled(RequestFactory().get('/'))


@pytest.mark.parametrize('empty_key', sorted(COMPLETE_SETTINGS))
def test_paygate_is_not_enabled_when_a_required_key_is_empty(empty_key):
    """EOX_PAYGATE_SETTINGS with one of its required keys empty does not enable Paygate.

    Expected result:
    - is_enabled returns False for the request.
    """
    settings_with_empty_key = {**COMPLETE_SETTINGS, empty_key: ''}
    with override_settings(EOX_PAYGATE_SETTINGS=settings_with_empty_key):
        assert not PaygateProcessor().is_enabled(RequestFactory().get('/'))


@override_settings(PAYGATE_SETTINGS=COMPLETE_SETTINGS)
def test_the_previous_setting_name_is_not_read():
    """A complete configuration under the scaffold's PAYGATE_SETTINGS name does not enable Paygate.

    Expected result:
    - is_enabled returns False for the request.
    """
    assert not PaygateProcessor().is_enabled(RequestFactory().get('/'))


def test_paygate_is_hidden_at_checkout_when_it_is_not_enabled():
    """zeitlabs hides Paygate at checkout when it is not enabled for the request.

    Expected result:
    - is_hidden_for returns True for the request.
    """
    assert PaygateProcessor().is_hidden_for(RequestFactory().get('/'))


def test_the_gateway_order_id_is_the_payment_reference():
    """The gateway order id zeitlabs records for a hand-off is the payment reference.

    Expected result:
    - get_gateway_order_id returns the order reference of the transaction parameters.
    """
    assert PaygateProcessor().get_gateway_order_id({'order_reference': '1-42'}) == '1-42'


@pytest.mark.parametrize('view_attribute', ['RETURN_VIEW', 'STATUS_VIEW'])
def test_the_declared_views_belong_to_the_paygate_processor(view_attribute):
    """The return and status views the processor declares exist and serve the Paygate processor.

    Expected result:
    - The view class at the declared dotted path has PaygateProcessor as its processor class.
    """
    assert import_string(getattr(PaygateProcessor, view_attribute)).processor_class is PaygateProcessor
