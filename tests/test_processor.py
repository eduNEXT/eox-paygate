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

# None stands for EOX_PAYGATE_SETTINGS not being set at all.
INCOMPLETE_SETTINGS = [
    pytest.param(None, id='not-set'),
    pytest.param({}, id='empty-settings'),
    *[
        pytest.param(
            {key: value for key, value in COMPLETE_SETTINGS.items() if key != missing_key},
            id=f'no-{missing_key}',
        )
        for missing_key in COMPLETE_SETTINGS
    ],
    *[
        pytest.param({**COMPLETE_SETTINGS, empty_key: ''}, id=f'empty-{empty_key}')
        for empty_key in COMPLETE_SETTINGS
    ],
]


def test_zeitlabs_registers_the_paygate_processor_at_startup():
    """The package's entry point makes zeitlabs register the Paygate processor at startup.

    Expected result:
    - The zeitlabs processor registry maps the paygate slug to PaygateProcessor.
    """
    assert PROCESSORS.get('paygate') is PaygateProcessor


@override_settings(EOX_PAYGATE_SETTINGS=COMPLETE_SETTINGS)
def test_paygate_is_enabled_when_every_required_key_holds_a_value():
    """An EOX_PAYGATE_SETTINGS with a value for every required key enables Paygate.

    Expected result:
    - is_enabled returns True.
    """
    assert PaygateProcessor().is_enabled()


@pytest.mark.parametrize('paygate_settings', INCOMPLETE_SETTINGS)
def test_paygate_is_not_enabled_when_a_required_key_has_no_value(paygate_settings):
    """An EOX_PAYGATE_SETTINGS that is not set, lacks a required key or leaves one empty does not enable Paygate.

    Expected result:
    - is_enabled returns False.
    """
    overrides = {} if paygate_settings is None else {'EOX_PAYGATE_SETTINGS': paygate_settings}
    with override_settings(**overrides):
        assert not PaygateProcessor().is_enabled()


@override_settings(EOX_PAYGATE_SETTINGS=COMPLETE_SETTINGS)
def test_paygate_is_not_hidden_at_checkout_when_it_is_enabled():
    """Zeitlabs does not hide Paygate at checkout when it is enabled.

    Expected result:
    - is_hidden_for returns False for the request.
    """
    assert not PaygateProcessor().is_hidden_for(RequestFactory().get('/'))


def test_the_payment_reference_is_recorded_as_the_gateway_order_id():
    """The payment reference is what zeitlabs records as the gateway order id of a hand-off.

    Expected result:
    - get_gateway_order_id returns the payment reference of the transaction parameters.
    """
    assert PaygateProcessor().get_gateway_order_id({'payment_reference': '1-42'}) == '1-42'


@pytest.mark.parametrize('view_attribute', ['RETURN_VIEW', 'STATUS_VIEW'])
def test_the_declared_views_belong_to_the_paygate_processor(view_attribute):
    """The return and status views the processor declares exist and serve the Paygate processor.

    Expected result:
    - The view class at the declared dotted path has PaygateProcessor as its processor class.
    """
    view_class = import_string(getattr(PaygateProcessor, view_attribute))
    assert view_class.processor_class is PaygateProcessor
