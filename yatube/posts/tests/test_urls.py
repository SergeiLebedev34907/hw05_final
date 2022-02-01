# posts/tests/test_urls.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.auth = User.objects.create_user(username="auth")
        cls.user = User.objects.create_user(username="user")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            id=1, author=cls.auth, text="Тестовый текст поста", group=cls.group
        )
        cls.addr_list = [
            "/",
            "/group/test-slug/",
            "/profile/auth/",
            f"/posts/{PostsURLTests.post.id}/",
            f"/posts/{PostsURLTests.post.id}/edit/",
            "/create/",
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client_auth = Client()
        self.authorized_client.force_login(PostsURLTests.user)
        self.authorized_client_auth.force_login(PostsURLTests.auth)

    def test_unexisting_page(self):
        """Получен ожидаемый status code несуществующей страницы."""
        response = self.client.get("/unexisting-page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_address_status(self):
        """Получен ожидаемый status code страниц."""
        for addr in PostsURLTests.addr_list:
            with self.subTest(addr=addr):
                response = self.authorized_client_auth.get(addr)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_post_create_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу '/create/' перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.client.get(reverse("posts:post_create"), follow=True)
        self.assertRedirects(
            response,
            reverse("users:login") + "?next=" + reverse("posts:post_create"),
        )

    def test_post_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу '/posts/<post_id>/edit/' перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.client.get(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{PostsURLTests.post.id}"},
            ),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("users:login")
            + "?next="
            + reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{PostsURLTests.post.id}"},
            ),
        )

    def test_add_comment_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу '/posts/<post_id>/comment/' перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.client.get(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": f"{PostsURLTests.post.id}"},
            ),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("users:login")
            + "?next="
            + reverse(
                "posts:add_comment",
                kwargs={"post_id": f"{PostsURLTests.post.id}"},
            ),
        )

    def test_post_edit_url_redirect_authorized_client_on_post_detail(self):
        """Страница по адресу '/posts/<post_id>/edit/' перенаправит авторизованного
        пользователя на страницу подробного описания поста.
        """
        response = self.authorized_client.get(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": f"{PostsURLTests.post.id}"},
            ),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={"post_id": f"{PostsURLTests.post.id}"},
            ),
        )
