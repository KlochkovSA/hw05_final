from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class TestPostsURLS(TestCase):
    def setUp(self):
        self.authorized_client = Client()
        user = User.objects.create_user(username='test_user')
        self.authorized_client.force_login(user)

    def test_urls_uses_correct_template_all(self):
        templates_url_names = {
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/logout/': 'users/logged_out.html',
        }

        for url, template in templates_url_names.items():
            # Тестирование ведется для авторизованного клиента
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
