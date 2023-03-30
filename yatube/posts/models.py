from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

from core.models import DefaultModel, TextAuthorModel
from core.utils import truncatechars

User = get_user_model()


class Group(DefaultModel):
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
        return truncatechars(self.title, settings.NUMCATECHARS)


class Post(TextAuthorModel):
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

    class Meta(DefaultModel.Meta, TextAuthorModel.Meta):
        default_related_name = 'posts'
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return truncatechars(self.text, settings.NUMCATECHARS)


class Comment(TextAuthorModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='пост',
        help_text='укажите пост для комментария',
    )

    class Meta(DefaultModel.Meta, TextAuthorModel.Meta):
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self) -> str:
        return truncatechars(self.text, settings.NUMCATECHARS)


class Follow(DefaultModel):
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
        UniqueConstraint(
            fields=['user', 'author'],
            name='unique_follow',
        )
        verbose_name = 'подписчик'
        verbose_name_plural = 'подписчики'

    def __str__(self) -> str:
        return f'{self.user.username} подписан на {self.author.username}'
