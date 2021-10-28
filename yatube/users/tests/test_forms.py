# users/tests/test_forms.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class CreationFormTests(TestCase):

    def test_signup_user(self):
        """Валидная форма создает пользователя."""
        # Подсчитаем количество записей в User
        users_count = User.objects.count()
        form_data = {
            'username': 'username',
            'password1': 'lejhc8e74847jzdf',
            'password2': 'lejhc8e74847jzdf'
        }
        # Отправляем POST-запрос
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:index'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(User.objects.count(), users_count + 1)
