eox-paygate
###########

Payment processor for `openedx-zeitlabs-payments`_ (contract ``v1``).

.. _openedx-zeitlabs-payments: https://github.com/zeit-labs/openedx-zeitlabs-payments

Installation
************

Requires ``openedx-zeitlabs-payments`` >= 1.0.0 (processor contract ``v1``) installed in the LMS. Install the package
next to it::

    pip install eox-paygate

The package registers itself through two entry points, without changes in zeitlabs:

- ``zeitlabs_payments.v1``: ``paygate = eox_paygate.processor:PaygateProcessor``.
- ``lms.djangoapp``: installs the Django app, so the LMS finds its templates.

The processor is hidden in the checkout while ``EOX_PAYGATE_SETTINGS`` does not hold every required key.

Configuration
*************

See `docs/configuration.rst <docs/configuration.rst>`_.

URLs
****

zeitlabs mounts the views of the processor by its slug:

- ``payment/v1/processor/paygate/return/``
- ``payment/v1/processor/paygate/status/``

Not implemented yet
*******************

- The hand-off of the learner to Paygate's hosted payment page.
- The settlement of the payment when the learner returns, and through Paygate's server callback.
