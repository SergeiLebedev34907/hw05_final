# posts/tests/test_forms.py
import shutil
import tempfile

from django.contrib.auth import get_user_model
from ..models import Post, Group, Comment
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.auth = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Создадим 2 поста. 1-ый с группой. 2-ой без группы.
        cls.post_1 = Post.objects.create(
            author=cls.auth,
            text='Тестовый текст первого поста',
            group=cls.group
        )
        cls.post_2 = Post.objects.create(
            author=cls.auth,
            text='Тестовый текст второго поста'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями: создание, удаление,
        # копирование, перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем клиент автора поста
        self.authorized_client_auth = Client()
        # Авторизуем автора поста
        self.authorized_client_auth.force_login(PostFormTests.auth)

    def test_create_post_with_group_and_image(self):
        """
        Валидная форма создает запись в Post с указанием группы и картинки.
        """
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        image_name = 'small.gif'
        uploaded = SimpleUploadedFile(
            name=image_name,
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': PostFormTests.post_1.text,
            'group': PostFormTests.group.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client_auth.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': PostFormTests.auth.username}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('pk')
        self.assertEqual(
            post.text,
            PostFormTests.post_1.text
        )
        self.assertEqual(
            post.image,
            f'posts/{image_name}'
        )

    def test_create_post_without_group(self):
        """Валидная форма создает запись в Post без указания группы."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()
        form_data = {
            'text': PostFormTests.post_2.text,
        }
        # Отправляем POST-запрос
        response = self.authorized_client_auth.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': PostFormTests.auth.username}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('pk')
        self.assertEqual(
            post.text,
            PostFormTests.post_2.text
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': 'Отредактиованный текст поста'
        }
        # Отправляем POST-запрос
        response = self.authorized_client_auth.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostFormTests.post_1.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': PostFormTests.post_1.id})
        )
        # Проверяем, изменился ли текст поста
        edit_post = Post.objects.get(id=PostFormTests.post_1.id)
        self.assertEqual(
            edit_post.text,
            form_data['text'])

    def test_add_comment(self):
        """Валидная форма создает комментарий."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий',
        }
        # Отправляем POST-запрос
        response = self.authorized_client_auth.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': f'{PostFormTests.post_1.id}'}
            ),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{PostFormTests.post_1.id}'}
            )
        )
        # Проверяем, увеличилось ли число комментариев
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        comment = Comment.objects.latest('pk')
        self.assertEqual(comment.text, form_data['text'])
