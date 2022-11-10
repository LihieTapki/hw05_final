import shutil
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.anon = Client()
        cls.auth = Client()
        cls.author = Client()

        cls.user, cls.author_user = mixer.cycle(2).blend(
            User,
            username=(
                name
                for name in (
                    'user',
                    'author',
                )
            ),
        )
        cls.group = mixer.blend('posts.group')
        cls.post = mixer.blend(
            'posts.post',
            author=cls.author_user,
            group=cls.group,
        )

        cls.auth.force_login(cls.user)
        cls.author.force_login(cls.author_user)

        cls.urls = {
            'index': reverse('posts:index'),
            'post_create': reverse('posts:post_create'),
            'follow': reverse('posts:follow_index'),
            'group': reverse('posts:group_list', args=(cls.group.slug,)),
            'post_detail': reverse('posts:post_detail', args=(cls.post.id,)),
            'add_comment': reverse('posts:add_comment', args=(cls.post.id,)),
            'post_edit': reverse('posts:post_edit', args=(cls.post.id,)),
            'profile': reverse('posts:profile', args=(cls.user.username,)),
            'missing': 'unexisting_page',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_http_statuses(self) -> None:
        httpstatuses = (
            (self.urls.get('index'), HTTPStatus.OK, self.anon),
            (self.urls.get('post_create'), HTTPStatus.FOUND, self.anon),
            (self.urls.get('post_create'), HTTPStatus.OK, self.auth),
            (self.urls.get('follow'), HTTPStatus.FOUND, self.anon),
            (self.urls.get('follow'), HTTPStatus.OK, self.auth),
            (self.urls.get('group'), HTTPStatus.OK, self.anon),
            (self.urls.get('post_detail'), HTTPStatus.OK, self.anon),
            (self.urls.get('post_edit'), HTTPStatus.FOUND, self.anon),
            (self.urls.get('post_edit'), HTTPStatus.FOUND, self.auth),
            (self.urls.get('post_edit'), HTTPStatus.OK, self.author),
            (self.urls.get('profile'), HTTPStatus.OK, self.anon),
            (self.urls.get('missing'), HTTPStatus.NOT_FOUND, self.anon),
        )
        for address, status, client in httpstatuses:
            with self.subTest(address=address):
                self.assertEqual(
                    client.get(address).status_code,
                    status,
                    ('Cтатус-код страницы ' 'не соответсвует ожидаемому'),
                )

    def test_templates(self) -> None:
        templates = (
            (self.urls.get('index'), 'posts/index.html', self.anon),
            (
                self.urls.get('post_create'),
                'posts/create_post.html',
                self.auth,
            ),
            (self.urls.get('follow'), 'posts/follow.html', self.auth),
            (self.urls.get('group'), 'posts/group_list.html', self.anon),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                self.anon,
            ),
            (
                self.urls.get('post_edit'),
                'posts/create_post.html',
                self.author,
            ),
            (self.urls.get('profile'), 'posts/profile.html', self.anon),
            (self.urls.get('missing'), 'core/404.html', self.anon),
        )
        for address, template, client in templates:
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    client.get(address),
                    template,
                    'URL-адреса не используют соответствующие шаблоны',
                )

    def test_redirects(self) -> None:
        """Проверка redirect в соответвии с правами пользователя."""
        redirects = (
            (
                self.urls.get('post_create'),
                '/auth/login/?next=/create/',
                self.anon,
            ),
            (self.urls.get('follow'), '/auth/login/?next=/follow/', self.anon),
            (self.urls.get('post_edit'), f'/posts/{self.post.id}/', self.anon),
            (self.urls.get('post_edit'), f'/posts/{self.post.id}/', self.auth),
        )
        for address, redirection, client in redirects:
            with self.subTest(address=address):
                self.assertRedirects(
                    client.get(address, follow=True),
                    redirection,
                )
