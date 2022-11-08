from behaviors.behaviors import Timestamped
from django.contrib.auth import get_user_model
from django.db import models

# from django.utils import timezone


User = get_user_model()


class DefaultModel(models.Model):
    class Meta:
        abstract = True


class TimestampedModel(DefaultModel, Timestamped):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field('created').verbose_name = 'дата создания'
        self._meta.get_field('created').help_text = 'дата создания'

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
        ordering = ('-created',)
        abstract = True

    # @property
    # def changed(self):
    #     return True if self.modified else False

    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         self.modified = timezone.now()
    #     return super(Timestamped, self).save(*args, **kwargs)
    # просто понравился декаратор, но на данном этапе не смог придумать
    # для чего бы это могло быть мне полезно, пока удалю.
