# about/tests.py
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def test_about_address_status(self):
        """Проверка доступности адресов about."""
        addresses = ["/about/tech/", "/about/author/"]
        for address in addresses:
            response = self.client.get(address)
            self.assertEqual(response.status_code, HTTPStatus.OK.value)


class StaticViewsTests(TestCase):
    def test_about_author_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        urls = {
            reverse("about:tech"): "about/tech.html",
            reverse("about:author"): "about/author.html",
        }
        for reverse_name, template in urls.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
