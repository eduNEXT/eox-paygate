"""Client of the Paygate REST API."""
import json

import requests

from zeitlabs_payments.exceptions import GatewayError

# Seconds to wait for Paygate when ``EOX_PAYGATE_SETTINGS`` sets no ``TIMEOUT``.
DEFAULT_TIMEOUT = 20


class PaygateClient:
    """
    Calls the Paygate REST API with the credentials of a site's ``EOX_PAYGATE_SETTINGS``.

    Errors are raised as ``GatewayError`` with messages that never carry a credential or Paygate's answer, since
    zeitlabs logs and stores them.
    """

    def __init__(self, paygate_settings: dict):
        """Keep the site's ``EOX_PAYGATE_SETTINGS`` to call Paygate with."""
        self.paygate_settings = paygate_settings

    def checkout(self, payload: dict) -> dict:
        """Open a payment session in Paygate and return its answer, which names the hosted payment page."""
        answer = self.call('CheckOut', payload)
        if not answer.get('URL') or not answer.get('SessionToken'):
            raise GatewayError('Paygate CheckOut answered without a hosted payment page.')
        return answer

    def call(self, operation: str, payload: dict) -> dict:
        """Send the payload to a Paygate operation, with the merchant's credentials, and return Paygate's answer."""
        body = {
            'ACCESS_TOKEN': self.paygate_settings['ACCESS_TOKEN'],
            'MERCHANT_CODE': self.paygate_settings['MERCHANT_CODE'],
            **payload,
        }
        try:
            response = requests.post(
                f"{self.paygate_settings['API_BASE_URL']}/api/{operation}",
                data=json.dumps(body),
                headers={'Content-Type': 'application/json'},
                auth=(self.paygate_settings['BASIC_AUTH_USER'], self.paygate_settings['BASIC_AUTH_PASSWORD']),
                timeout=self.paygate_settings.get('TIMEOUT', DEFAULT_TIMEOUT),
            )
        except requests.RequestException as error:
            raise GatewayError(f'Paygate {operation} could not be reached: {type(error).__name__}.') from error
        if response.status_code != 200:
            raise GatewayError(f'Paygate {operation} answered HTTP {response.status_code}.')
        try:
            answer = response.json()
        except ValueError as error:
            raise GatewayError(f'Paygate {operation} answered a body that is not JSON.') from error
        if not answer.get('Success'):
            raise GatewayError(f"Paygate {operation} failed with return code {answer.get('ReturnCode')}.")
        return answer
