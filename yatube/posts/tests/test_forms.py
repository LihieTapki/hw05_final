import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Follow, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend('posts.group')
        cls.anon = Client()
        cls.auth = Client()
        cls.author = Client()
        cls.user = User.objects.create_user(username='user')
        cls.user_author = User.objects.create_user(username='user_author')
        cls.other_user = User.objects.create_user(username='other_user')
        cls.auth.force_login(cls.user)
        cls.author.force_login(cls.user_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_auth_user_create_post_ok(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        response = self.auth.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
                'image': uploaded,
            },
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                args=(self.user.username,),
            ),
        )
        self.assertEqual(
            Post.objects.count(),
            1,
            'После создания поста количество постов в базе не равно единице',
        )
        post = Post.objects.select_related('author', 'group').first()
        field_values = {
            'text': 'Тестовый пост',
            'author': self.user,
            'group': None,
            'image': 'posts/small.gif',
        }
        for field, expected_value in field_values.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(post, field),
                    expected_value,
                    (
                        'Значения созданого поста не соответвуют '
                        'значениям сохраненного в базе поста'
                    ),
                )

    def test_anon_user_create_post_denied(self):
        self.anon.post(
            reverse('posts:post_create'),
            {'text': 'Тестовый пост'},
            follow=True,
        )
        self.assertEqual(
            Post.objects.count(),
            0,
            (
                'После попытки создания поста'
                'количество постов в базе не равно нулю'
            ),
        )

    def test_author_post_edit_ok(self):
        post = Post.objects.create(
            author=self.user_author,
            text='Тестовый пост',
            group=self.group,
        )
        response = self.author.post(
            reverse('posts:post_edit', args=(post.id,)),
            {'text': 'Тестовый пост отредактирован'},
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=(post.id,),
            ),
        )
        self.assertEqual(
            Post.objects.count(),
            1,
            (
                'После редактирования поста '
                'количество постов в базе изменилось'
            ),
        )
        post = Post.objects.first()
        field_values = {
            post.text: 'Тестовый пост отредактирован',
            post.author: self.user_author,
            post.group: None,
        }
        for field, expected_value in field_values.items():
            with self.subTest(field=field):
                self.assertEqual(
                    field,
                    expected_value,
                    (
                        'Значения измененного поста не соответвуют '
                        'значениям сохраненного в базе поста'
                    ),
                )

    def test_auth_user_edit_other_user_post_denied(self):
        post = Post.objects.create(
            author=self.other_user,
            text='Тестовый пост',
            group=self.group,
        )
        response = self.auth.post(
            reverse('posts:post_edit', args=(post.id,)),
            {'text': 'Тестовый пост отредактирован'},
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=(post.id,),
            ),
        )
        self.assertEqual(
            Post.objects.count(),
            1,
            (
                'После попытки редактирования поста '
                'количество постов в базе изменилось'
            ),
        )
        post = Post.objects.first()
        field_values = {
            post.text: 'Тестовый пост',
            post.author: self.other_user,
            post.group: self.group,
        }
        for field, expected_value in field_values.items():
            with self.subTest(field=field):
                self.assertEqual(
                    field,
                    expected_value,
                    (
                        'Значения поста в базе после '
                        'попытки редатировнаия изменились'
                    ),
                )

    def test_anon_user_edit_post_denied(self):
        post = Post.objects.create(
            author=self.user_author,
            text='Тестовый пост',
            group=self.group,
        )
        response = self.anon.post(
            reverse('posts:post_edit', args=(post.id,)),
            {'text': 'Тестовый пост отредактирован'},
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=(post.id,),
            ),
        )
        self.assertEqual(
            Post.objects.count(),
            1,
            (
                'После попытки редактирования поста '
                'количество постов в базе изменилось'
            ),
        )
        post = Post.objects.first()
        field_values = {
            post.text: 'Тестовый пост',
            post.author: self.user_author,
            post.group: self.group,
        }
        for field, expected_value in field_values.items():
            with self.subTest(field=field):
                self.assertEqual(
                    field,
                    expected_value,
                    (
                        'Значения поста в базе после '
                        'попытки редатировнаия изменились'
                    ),
                )

    def test_anon_user_create_comment_denied(self):
        post = Post.objects.create(
            author=self.other_user,
            text='Тестовый пост',
            group=self.group,
        )
        response = self.anon.post(
            reverse('posts:add_comment', args=(post.id,)),
            {'text': 'Тестовый комментарий'},
            follow=True,
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{post.id}/comment/',
        )
        self.assertEqual(
            Comment.objects.count(),
            0,
            (
                'После попытки создания комментария'
                'количество постов в базе не равно нулю'
            ),
        )

    def test_auth_follow_author(self):
        self.auth.post(
            reverse('posts:profile_follow', args=(self.user_author.username,)),
            follow=True,
        )
        self.assertEqual(
            Follow.objects.count(),
            1,
            (
                'После создания подписки количество подписок'
                'в базе не равно единице'
            ),
        )
        follow = Follow.objects.first()
        field_values = {
            follow.user: self.user,
            follow.author: self.user_author,
        }
        for field, expected_value in field_values.items():
            with self.subTest(field=field):
                self.assertEqual(
                    field,
                    expected_value,
                    (
                        'Значения созданой подписки не соответвуют '
                        'значениям сохраненной в базе подписки'
                    ),
                )

    def test_auth_unfollow_author(self):
        Follow.objects.create(
            user=self.user,
            author=self.user_author,
        )
        self.auth.post(
            reverse(
                'posts:profile_unfollow',
                args=(self.user_author.username,),
            ),
            follow=True,
        )
        self.assertEqual(
            Follow.objects.count(),
            0,
            (
                'После удаления тестовой подписки количество подписок'
                'в базе не равно нулю'
            ),
        )
