from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from mixer.backend.django import mixer

from core.utils import truncatechars

User = get_user_model()


class GroupModelTest(TestCase):
    MODEL_INFO = (
        ('title', 'название', 'название группы'),
        (
            'slug',
            'текстовый идентификатор страницы',
            'текстовый идентификатор страницы',
        ),
        ('description', 'описание', 'описание группы'),
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend('posts.group')

    def test_correct___str__(self) -> None:
        self.assertEqual(
            truncatechars(self.group.title, settings.NUMCATECHARS),
            str(self.group),
            'У модели некорректно работает __str__ 15 символов.',
        )

    def test_verbose_name_help_text(self) -> None:
        for field, verbose_name, help_text in self.MODEL_INFO:
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    verbose_name,
                    'verbose_name не совпадает с ожидаемым.',
                )
                self.assertEqual(
                    self.group._meta.get_field(field).help_text,
                    help_text,
                    'help_text в полях не совпадает с ожидаемым',
                )


class PostModelTest(TestCase):
    MODEL_INFO = (
        ('text', 'текст', 'введите текст'),
        ('group', 'группа', 'выберите группу'),
        ('created', 'дата создания', 'дата создания'),
        ('author', 'автор', 'укажите автора'),
        ('image', 'изображение', 'добавьте изображение'),
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = mixer.blend('posts.post')

    def test__correct___str__(self) -> None:
        self.assertEqual(
            truncatechars(self.post.text, settings.NUMCATECHARS),
            str(self.post),
            'У модели некорректно работает __str__ 15 символов.',
        )

    def test_verbose_name_help_text(self) -> None:
        for field, verbose_name, help_text in self.MODEL_INFO:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    verbose_name,
                    'verbose_name не совпадает с ожидаемым.',
                )
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    help_text,
                    'help_text в полях не совпадает с ожидаемым',
                )


class CommentModelTest(TestCase):
    MODEL_INFO = (
        ('post', 'пост', 'укажите пост для комментария'),
        ('author', 'автор', 'укажите автора'),
        ('created', 'дата создания', 'дата создания'),
        ('text', 'текст', 'введите текст'),
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = mixer.blend('posts.post')
        cls.comment = mixer.blend('posts.comment', post=cls.post)

    def test_correct___str__(self) -> None:
        self.assertEqual(
            truncatechars(self.comment.text, settings.NUMCATECHARS),
            str(self.comment),
            'У модели некорректно работает __str__ 15 символов.',
        )

    def test_verbose_name_help_text(self) -> None:
        for field, verbose_name, help_text in self.MODEL_INFO:
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).verbose_name,
                    verbose_name,
                    'verbose_name не совпадает с ожидаемым.',
                )
                self.assertEqual(
                    self.comment._meta.get_field(field).help_text,
                    help_text,
                    'help_text в полях не совпадает с ожидаемым',
                )


class FollowModelTest(TestCase):
    MODEL_INFO = (
        ('user', 'подписчик', 'укажите подписчика'),
        ('author', 'автор', 'укажите автора на которого подписываются'),
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follow = mixer.blend('posts.follow')

    def test_correct___str__(self) -> None:
        self.assertEqual(
            f'{self.follow.user} подписан на {self.follow.author}',
            str(self.follow),
            'У модели некорректно работает __str__.',
        )

    def test_verbose_name_help_text(self) -> None:
        for field, verbose_name, help_text in self.MODEL_INFO:
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(field).verbose_name,
                    verbose_name,
                    'verbose_name не совпадает с ожидаемым.',
                )
                self.assertEqual(
                    self.follow._meta.get_field(field).help_text,
                    help_text,
                    'help_text в полях не совпадает с ожидаемым',
                )
