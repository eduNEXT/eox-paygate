"""
eox-paygate Django application initialization.
"""
from django.apps import AppConfig


class EoxPaygateConfig(AppConfig):
    """
    Configuration for the eox-paygate Django application.

    Installed in the LMS through the ``lms.djangoapp`` entry point so its templates are found. The processor is
    registered separately, through the ``zeitlabs_payments.v1`` entry point, and its views are mounted by zeitlabs.
    """

    name = 'eox_paygate'
    verbose_name = 'eox-paygate'
