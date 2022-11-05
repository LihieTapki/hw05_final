from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class DefaultModel(models.Model):
    class Meta:
        abstract = True


class Timestamped(models.Model):
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
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата создания',
        help_text='дата создания',
    )
    modified = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ('-created',)
        abstract = True

    @property
    def changed(self):
        return True if self.modified else False

    def save(self, *args, **kwargs):
        if self.pk:
            self.modified = timezone.now()
        return super(Timestamped, self).save(*args, **kwargs)
