from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from mixer.backend.django import mixer

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend('posts.group')
        cls.post = mixer.blend('posts.post', group=cls.group)
        cls.anon = Client()
        cls.auth = Client()
        cls.author = Client()
        cls.user = User.objects.create_user(username='user')
        cls.auth.force_login(cls.user)
        cls.author.force_login(cls.post.author)
        cls.posts_edit_url = f'/posts/{cls.post.id}/edit/'
        cls.posts_create_url = '/create/'
        cls.public_url = (
            ('/', 'posts/index.html', HTTPStatus.OK, None),
            (
                f'/group/{cls.group.slug}/',
                'posts/group_list.html',
                HTTPStatus.OK,
                None,
            ),
            (
                f'/profile/{cls.user.username}/',
                'posts/profile.html',
                HTTPStatus.OK,
                None,
            ),
            (
                f'/posts/{cls.post.id}/',
                'posts/post_detail.html',
                HTTPStatus.OK,
                None,
            ),
        )
        cls.private_url = (
            (
                cls.posts_edit_url,
                'posts/create_post.html',
                HTTPStatus.FOUND,
                f'/posts/{cls.post.id}/',
            ),
            (
                cls.posts_create_url,
                'posts/create_post.html',
                HTTPStatus.FOUND,
                '/auth/login/?next=/create/',
            ),
            (
                '/follow/',
                'posts/follow.html',
                HTTPStatus.FOUND,
                '/auth/login/?next=/follow/',
            ),
        )
        cls.templates_url = cls.public_url + cls.private_url

    def setUp(self):
        cache.clear()

    def test_public_url_access_anonymous(self):
        for address, _, status, _ in self.public_url:
            with self.subTest(address=address):
                response = self.anon.get(address)
                self.assertEqual(
                    response.status_code,
                    status,
                    (
                        'Публичные страницы не доступны '
                        'неавторизованному пользователю'
                    ),
                )

    def test_private_url_redirect_anonymous(self):
        """Приватные страницы недоступны неавторизованному пользователю."""
        for address, _, _, redirection in self.private_url:
            with self.subTest(address=address):
                response = self.anon.get(address, follow=True)
                self.assertRedirects(response, redirection)

    def test_posts_create_url_access_authorized(self):
        response = self.auth.get(self.posts_create_url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Страница /create/ доступна авторизованному пользователю',
        )

    def test_posts_edit_url_redirect_authorized_on_post_id(self):
        """
        Страница по адресу /posts/post_id/edit/.
        перенаправит авторизованного пользователя на /posts/post_id/.
        """
        response = self.auth.get(self.posts_edit_url, follow=True)
        self.assertRedirects(
            response,
            f'/posts/{self.post.id}/',
        )

    def test_posts_edit_url_exists_at_desired_location_author(self):
        response = self.author.get(self.posts_edit_url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            'Страница /posts/post_id/edit/ доступна автору',
        )

    def test_urls_uses_correct_template(self):
        for address, template, _, _ in self.templates_url:
            with self.subTest(address=address):
                response = self.author.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    'URL-адреса используют соответствующие шаблоны',
                )
