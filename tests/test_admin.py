from django.contrib.auth import get_user_model
from django.core.urlresolvers import resolve
from django.test import TestCase
from django.test.client import RequestFactory
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


class AdminTestCase(TestCase):
    def setUp(self):
        self.user_password = 'pw'
        self.user = get_user_model().objects.create_user(
            'user', email='user@example.com', password=self.user_password)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

    def tearDown(self):
        self.user.delete()

    def test_has_add_permission(self):
        self.client.login(username=self.user, password=self.user_password)

        url = reverse('admin:email_extras_address_changelist')
        response = self.client.get(url)

        self.assertFalse(response.context['has_add_permission'])
