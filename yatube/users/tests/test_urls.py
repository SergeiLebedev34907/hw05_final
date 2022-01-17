# users/tests/test_urls.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class AuthURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="user")

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(AuthURLTests.user)

    def test_guest_client_signup_url_status(self):
        """Получен ожидаемый status code страницы."""
        response = self.client.get("/auth/signup/")
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            reverse("users:login"): "users/login.html",
            reverse(
                "users:password_change_form"
            ): "users/password_change_form.html",
            reverse(
                "users:password_change_done"
            ): "users/password_change_done.html",
            reverse("users:logout"): "users/logged_out.html",
            reverse(
                "users:password_reset_form"
            ): "users/password_reset_form.html",
            reverse(
                "users:password_reset_done"
            ): "users/password_reset_done.html",
            reverse(
                "users:password_reset_confirm",
                kwargs={"uidb64": "uidb64", "token": "token"},
            ): "users/password_reset_confirm.html",
            reverse(
                "users:password_reset_complete"
            ): "users/password_reset_complete.html",
            reverse("users:signup"): "users/signup.html",
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
