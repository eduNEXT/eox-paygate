"""URLs of the tests: the zeitlabs routes the processor builds its return URLs from."""
from django.urls import include, path

urlpatterns = [
    path('', include('zeitlabs_payments.urls')),
]
