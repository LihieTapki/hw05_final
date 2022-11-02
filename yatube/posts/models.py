from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel
from core.utils import truncatechars
from yatube.settings import NUMCATECHARS

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'название',
        max_length=200,
        help_text='название группы',
    )
    slug = models.SlugField(
        'текстовый идентификатор страницы',
        unique=True,
        help_text='текстовый идентификатор страницы',
    )
    description = models.TextField(
        'описание',
        help_text='описание группы',
    )

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self) -> str:
        return truncatechars(self.title, NUMCATECHARS)


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='текст поста',
        help_text='введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        help_text='укажите автора поста',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='группа',
        help_text='выберите группу',
    )
    image = models.ImageField(
        'изображение',
        upload_to='posts/',
        blank=True,
        help_text='добавьте изображение',
    )

    class Meta:
        ordering = ('-created',)
        default_related_name = 'posts'
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return truncatechars(self.text, NUMCATECHARS)


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='пост',
        help_text='укажите пост для комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        help_text='укажите автора комментария',
    )
    text = models.TextField(
        verbose_name='текст комментария',
        help_text='введите текст комментария',
    )

    class Meta:
        ordering = ('-created',)
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self) -> str:
        return truncatechars(self.text, NUMCATECHARS)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='подписчик',
        help_text='укажите подписчика',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
        help_text='укажите автора на которого подписываются',
    )

    class Meta:
        verbose_name = 'подписчик'
        verbose_name_plural = 'подписчики'
        default_related_name = 'follow'

    def __str__(self) -> str:
        return self.user.username
