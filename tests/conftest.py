"""Fixtures of the hand-off tests."""
import pytest
import responses
from common.djangoapps.student.models import UserProfile
from django.contrib.auth import get_user_model
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from zeitlabs_payments.models import Cart, CatalogueItem

from tests.paygate_data import CHECKOUT_ANSWER, CHECKOUT_URL, COURSE_ID


@pytest.fixture
def cart():
    """Return a cart of one paid course, being handed off to Paygate by a learner with a profile name."""
    user = get_user_model().objects.create(
        username='learner', email='learner@example.com', first_name='Ana', last_name='Learner',
    )
    UserProfile.objects.create(user=user, name='Ana Maria Learner')
    CourseOverview.objects.create(id=COURSE_ID, org='org', display_name='Course')
    item = CatalogueItem.objects.create(
        sku='org-course-run-paid', type=CatalogueItem.ItemType.PAID_COURSE, title='Course',
        item_ref_id=COURSE_ID, price='49.90', currency='EUR',
    )
    paid_cart = Cart.objects.create(user=user, status=Cart.Status.PROCESSING, gateway='paygate')
    paid_cart.items.create(catalogue_item=item, original_price=item.price, final_price=item.price)
    return paid_cart


@pytest.fixture
def checkout():
    """Simulate a successful CheckOut answer from Paygate."""
    with responses.RequestsMock() as paygate:
        paygate.add(responses.POST, CHECKOUT_URL, json=CHECKOUT_ANSWER)
        yield paygate
