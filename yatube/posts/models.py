# posts/models.py
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(
        unique=True,
        verbose_name='Краткое название'
    )
    description = models.TextField(max_length=400, verbose_name='Описание')

    def __str__(self):
        return self.title


class Post(models.Model):

    text = models.TextField(
        max_length=400,
        verbose_name='Текст поста:',
        help_text='Текст нового поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True, null=True,
        help_text='Группа, к которой будет относиться пост',
        verbose_name='Группа',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    # Поле для картинки (необязательное)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    # Аргумент upload_to указывает директорию,
    # в которую будут загружаться пользовательские файлы.

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария'
    )
    text = models.TextField(
        max_length=400,
        verbose_name='Комментарий:',
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow'
            )
        ]
