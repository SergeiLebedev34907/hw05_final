# posts/tests/test_views.py
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.core.cache import cache
from ..models import Post, Group, Comment, Follow

User = get_user_model()


class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.auth = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='another-test-slug',
            description='Тестовое описание',
        )
        cls.image_name = 'small.gif'
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name=cls.image_name,
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.auth,
            text='Тестовый текст поста',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            author=cls.auth,
            text='Комментарий',
            post=cls.post
        )

    def setUp(self):
        # Создаем клиент автора поста
        self.authorized_client_auth = Client()
        # Авторизуем автора поста
        self.authorized_client_auth.force_login(PostsViewTests.auth)
        # Очистим кэш
        cache.clear()

    # Проверяем, что если при создании поста указать группу, то этот пост
    # не появляется в группе, для которой не был предназначен
    def test_create_post(self):
        """Тестовый пост не попал в группу, для которой не был предназначен"""
        self.assertFalse(PostsViewTests.another_group.posts.filter(
            id=PostsViewTests.post.id))

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        templates_pages_names = {

            reverse('posts:index'): 'posts/index.html',

            reverse('posts:post_create'): 'posts/post_create.html',

            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',

            reverse(
                'posts:profile',
                kwargs={'username': f'{PostsViewTests.auth.username}'}
            ): 'posts/profile.html',

            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{PostsViewTests.post.id}'}
            ): 'posts/post_detail.html',

            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{PostsViewTests.post.id}'}
            ): 'posts/post_create.html',
        }
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_auth.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем используемые словари context

    # Проверяем, что словарь context страниц /, group/<slug>/ и
    # profile/<username>/ в первом элементе списка page_obj содержат
    # ожидаемые значения

    # Заодно проверяем, что если при создании поста указать группу,
    # то этот пост появляется:
    # на главной странице сайта,
    # на странице выбранной группы,
    # в профайле пользователя.
    def test_page_obj_page_show_correct_context(self):
        """Шаблон page_obj сформирован с правильным контекстом."""

        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse(
                'posts:profile',
                kwargs={'username': f'{PostsViewTests.auth.username}'}
            ),
        ]
        for reverse_name in urls:
            response = self.authorized_client_auth.get(reverse_name)
            # Взяли первый элемент из списка и проверили, что его содержание
            # совпадает с ожидаемым
            first_object = response.context['page_obj'][0]
            first_obj_field_value = {
                first_object.text: PostsViewTests.post.text,
                first_object.group: PostsViewTests.group,
                first_object.image: PostsViewTests.post.image,
                first_object.author: PostsViewTests.auth
            }
            for field, value in first_obj_field_value.items():
                with self.subTest(field=field):
                    self.assertEqual(field, value)

    # Проверяем, что словарь context страницы posts/post_detail/<post_id>
    # содержит ожидаемые значения
    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client_auth.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{PostsViewTests.post.id}'})))
        context_value = {
            response.context.get('post').text: PostsViewTests.post.text,
            response.context.get('post').group: PostsViewTests.group,
            response.context.get('post').image: PostsViewTests.post.image,
            response.context.get('post').author: PostsViewTests.auth,
            response.context.get('comments').latest('pk'):
                PostsViewTests.comment,
            response.context.get('posts_count'):
                PostsViewTests.auth.posts.count()
        }
        for context, value in context_value.items():
            with self.subTest(context=context):
                self.assertEqual(context, value)

    # Проверяем, что словарь context страницы group/<slug>
    # содержит ожидаемые значения
    def test_post_list_pages_show_correct_context(self):
        """Шаблон post_list сформирован с правильным контекстом."""
        response = (self.authorized_client_auth.get(reverse(
            'posts:group_list',
            kwargs={'slug': f'{PostsViewTests.group.slug}'})))
        self.assertEqual(
            response.context.get('group').title,
            PostsViewTests.group.title)
        self.assertEqual(
            response.context.get('group').description,
            PostsViewTests.group.description)

    # Проверяем, что словарь context страницы profile/<username>
    # содержит ожидаемые значения
    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client_auth.get(reverse(
            'posts:profile',
            kwargs={'username': f'{PostsViewTests.auth.username}'})))
        self.assertEqual(response.context.get('author'), PostsViewTests.auth)
        self.assertEqual(
            response.context.get('posts_count'),
            PostsViewTests.auth.posts.count())

    # Проверка словаря контекста страницы создания поста
    # (в нём передаётся форма)
    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client_auth.get(
            reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_cache_is_work(self):
        """Кэш используется."""
        content1 = self.client.get(reverse('posts:index')).content
        Post.objects.latest('pk').delete()
        content2 = self.client.get(reverse('posts:index')).content
        self.assertEqual(content1, content2)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Очистимм кэш
        cache.clear()
        cls.auth = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        objs = []
        for i in range(1, 14):
            objs.append(
                Post(
                    author=cls.auth,
                    text=f'Тестовый текст {i} поста',
                    group=cls.group
                )
            )
        Post.objects.bulk_create(objs)
        cls.urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse(
                'posts:profile',
                kwargs={'username': f'{PaginatorViewsTest.auth.username}'}
            ),
        ]

    def test_first_page_contains_ten_records(self):
        for reverse_name in PaginatorViewsTest.urls:
            response = self.client.get(reverse_name)
            # Проверка: количество постов на первой странице равно 10.
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        for reverse_name in PaginatorViewsTest.urls:
            # Проверка: на второй странице должно быть три поста.
            response = self.client.get(reverse_name + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='user')
        cls.another_user = User.objects.create_user(username='another_user')
        cls.auth = User.objects.create_user(username='auth')

        cls.post = Post.objects.create(
            author=cls.auth,
            text='Тестовый текст поста',
        )

    def follow(self):
        self.authorized_client_user.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': f'{FollowViewsTest.auth.username}'}
            )
        )

    def setUp(self):
        self.authorized_client_user = Client()
        self.authorized_client_auth = Client()
        self.authorized_client_another_user = Client()
        self.authorized_client_user.force_login(FollowViewsTest.user)
        self.authorized_client_auth.force_login(FollowViewsTest.auth)
        self.authorized_client_another_user.force_login(
            FollowViewsTest.another_user
        )
        self.follow_count = Follow.objects.count()
        # Создаем подписку
        self.follow()
        cache.clear()

    def test_authenticated_user_follow(self):
        """Авторизованный пользователь может подписываться."""
        # Проверяем, что авторизованный пользователь может подписываться на
        # других пользователей
        self.assertEqual(Follow.objects.count(), self.follow_count + 1)
        # Проверяем не создается ли дублирующаяся подписка
        self.follow()
        self.assertEqual(Follow.objects.count(), self.follow_count + 1)

    def test_authenticated_user_follow_to_himself(self):
        """Пользователь не может подпсаться на самого себя."""
        self.authorized_client_auth.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': f'{FollowViewsTest.auth.username}'}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=FollowViewsTest.auth,
                author=FollowViewsTest.auth
            ).exists()
        )

    def test_authenticated_user_unfollow(self):
        """Авторизованный пользователь может отписываться."""
        # Проверяем, что авторизованный пользователь может отписываться от
        # других пользователей
        self.authorized_client_user.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': f'{FollowViewsTest.auth.username}'}
            )
        )
        self.assertEqual(Follow.objects.count(), self.follow_count)

    def test_following_post_in_users_news_feed(self):
        # Новая запись пользователя появляется в ленте тех,
        # кто на него подписан
        response = self.authorized_client_user.get(
            reverse('posts:follow_index')
        )
        posts_objects = response.context['page_obj']
        self.assertTrue(FollowViewsTest.post in posts_objects)
        # Новая запись пользователя не появляется в ленте тех,
        # кто на него не подписан
        response = self.authorized_client_another_user.get(
            reverse('posts:follow_index')
        )
        posts_objects = response.context['page_obj']
        self.assertFalse(FollowViewsTest.post in posts_objects)
