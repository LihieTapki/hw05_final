from behaviors.behaviors import Timestamped
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class DefaultModel(models.Model):
    class Meta:
        abstract = True


class TimestampedModel(DefaultModel, Timestamped):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field('created').verbose_name = 'дата создания'
        self._meta.get_field('created').help_text = 'дата создания'
        self._meta.get_field('modified').verbose_name = 'дата изменения'
        self._meta.get_field('modified').help_text = 'дата изменения'

    class Meta:
        abstract = True


class TextAuthorModel(TimestampedModel):
    text = models.TextField(
        verbose_name='текст',
        help_text='введите текст',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        help_text='укажите автора',
    )

    class Meta:
        abstract = True
        ordering = ('-created',)
