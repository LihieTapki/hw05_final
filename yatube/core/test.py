from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        num_post = 0
        while num_post < 13:
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
            )
            num_post += 1

    def test_first_page_contains_ten_records(self):
        templates = {
            ('posts:index', None, 10),
            ('posts:group_list', (self.group.slug,), 10),
            ('posts:profile', (self.user.username,), 10),
        }
        for views, args, template in templates:
            with self.subTest(views=views):
                response = self.client.get(reverse(views, args=args))
                self.assertEqual(len(response.context['page_obj']), template)

    def test_second_page_contains_three_records(self):
        templates = {
            ('posts:index', None, 3),
            ('posts:group_list', (self.group.slug,), 3),
            ('posts:profile', (self.user.username,), 3),
        }
        for views, args, template in templates:
            with self.subTest(views=views):
                response = self.client.get(
                    reverse(views, args=args) + '?page=2',
                )
                self.assertEqual(len(response.context['page_obj']), template)


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/unexisting_page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            'unexisting_page возвращает ошибку 404',
        )
        self.assertTemplateUsed(
            response,
            'core/404.html',
            'используется шаблон core/404.html',
        )
