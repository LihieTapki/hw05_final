from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:author доступен."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)

    def test_about_tech_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:tech доступен."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200)

    def test_about_pages_uses_correct_template(self):
        """При запросе к about: author и tech
        применяются шаблоны about.html и tech.html."""
        templates = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for views, template in templates.items():
            with self.subTest(views=views):
                response = self.guest_client.get(reverse(views))
                self.assertTemplateUsed(response, template)
