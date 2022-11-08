import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Follow, Post
from posts.tests.common import uploaded, new_uploaded

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
        field_values = (
            ('text', 'Тестовый пост'),
            ('author', self.user),
            ('group', None),
            ('image', 'posts/small.gif'),
        )
        for field, expected in field_values:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(post, field),
                    expected,
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
            image=new_uploaded,
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
        post = Post.objects.select_related('group', 'author').get()
        field_values = (
            ('text', 'Тестовый пост отредактирован'),
            ('author', self.user_author),
            ('group', None),
            ('image', 'posts/new_small.gif'),
        )
        for field, expected in field_values:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(post, field),
                    expected,
                    (
                        'Значения измененного поста не соответвуют '
                        'значениям сохраненного в базе поста'
                    ),
                )

    def test_anon_and_auth_edit_other_user_post_denied(self):
        post = mixer.blend(
            'posts.post',
            author=self.other_user,
            group=self.group,
        )
        client_list = ('anon', 'auth')
        for client in client_list:
            response = getattr(self, client).post(
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
            edited = Post.objects.select_related('group', 'author').get()
            for field in ('text', 'author', 'group'):
                with self.subTest(field=field):
                    self.assertEqual(
                        getattr(post, field),
                        getattr(edited, field),
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
            redirect_to_login(f'/posts/{post.id}/comment/').url,
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
        field_values = (
            ('user', self.user),
            ('author', self.user_author),
        )
        for field, expected in field_values:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(follow, field),
                    expected,
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
