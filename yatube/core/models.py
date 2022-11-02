from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""

    created = models.DateTimeField(
        'дата создания',
        auto_now_add=True,
        help_text='дата создания',
    )

    class Meta:
        abstract = True
