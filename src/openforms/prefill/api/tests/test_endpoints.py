from unittest.mock import patch

from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.reverse import reverse, reverse_lazy
from rest_framework.test import APITestCase

from openforms.accounts.tests.factories import UserFactory
from openforms.authentication.constants import AuthAttribute

from ...base import BasePlugin
from ...registry import Registry


class TestPrefill(BasePlugin):
    requires_auth = AuthAttribute.bsn
    verbose_name = "Test"

    def get_available_attributes(self):
        return [("foo", "Foo"), ("bar", "Bar")]


register = Registry()

register("test")(TestPrefill)


class AuthTests(APITestCase):
    endpoints = [
        reverse_lazy("api:prefill-plugin-list"),
        reverse_lazy("api:prefill-attribute-list", kwargs={"plugin": "test"}),
    ]

    def setUp(self):
        super().setUp()

        patcher = patch("openforms.prefill.api.views.register", new=register)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_forbidden_not_authenticated(self):
        for endpoint in self.endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)

                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_authenticated_but_not_staff(self):
        user = UserFactory.create(is_staff=False)
        self.client.force_authenticate(user=user)

        for endpoint in self.endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)

                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_and_staff(self):
        other_user = UserFactory.create(is_staff=True)

        self.client.force_authenticate(user=other_user)

        for endpoint in self.endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)

                self.assertEqual(response.status_code, status.HTTP_200_OK)


class ResponseTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = UserFactory.create(is_staff=True)

    def setUp(self):
        super().setUp()

        self.client.force_authenticate(user=self.user)

        patcher = patch("openforms.prefill.api.views.register", new=register)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_prefill_list(self):
        endpoint = reverse("api:prefill-plugin-list")

        response = self.client.get(endpoint)

        expected = [
            {
                "id": "test",
                "label": "Test",
                "requiresAuth": AuthAttribute.bsn,
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected)

    def test_attributes_list(self):
        endpoint = reverse("api:prefill-attribute-list", kwargs={"plugin": "test"})

        response = self.client.get(endpoint)

        expected = [
            {
                "id": "foo",
                "label": "Foo",
            },
            {
                "id": "bar",
                "label": "Bar",
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected)

    def test_attributes_invalid_plugin_ids(self):
        invalid = ["demo", 1234, "None"]
        for plugin in invalid:
            with self.subTest(plugin_id=plugin):
                endpoint = reverse(
                    "api:prefill-attribute-list", kwargs={"plugin": plugin}
                )

                response = self.client.get(endpoint)

                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
