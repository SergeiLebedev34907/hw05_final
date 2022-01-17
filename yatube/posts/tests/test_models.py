# posts/tests/test_models.py
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostsModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст поста",
        )

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        self.assertEqual(
            f"{PostsModelsTest.post}",
            PostsModelsTest.post.text[:15],
            "Метод __str__ модели Post работает неправильно",
        )

    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(
            f"{PostsModelsTest.group}",
            PostsModelsTest.group.title,
            "Метод __str__ модели Group работает неправильно",
        )

    def test_post_verbose_name(self):
        """verbose_name модели Post в полях совпадает с ожидаемым."""
        field_verboses = {
            "text": "Текст поста:",
            "pub_date": "Дата публикации",
            "group": "Группа",
            "author": "Автор",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostsModelsTest.post._meta.get_field(field).verbose_name,
                    expected_value,
                )

    def test_group_verbose_name(self):
        """verbose_name модели Group в полях совпадает с ожидаемым."""
        field_verboses = {
            "title": "Заголовок",
            "slug": "Краткое название",
            "description": "Описание",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostsModelsTest.group._meta.get_field(field).verbose_name,
                    expected_value,
                )

    def test_post_help_text(self):
        """help_text модели Post в полях совпадает с ожидаемым."""
        field_help_text = {
            "text": "Текст нового поста",
            "group": "Группа, к которой будет относиться пост",
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostsModelsTest.post._meta.get_field(field).help_text,
                    expected_value,
                )
