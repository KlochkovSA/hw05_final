from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class TestPostsURLS(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_group_slug',
            description='The group created during the test'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template_all(self):
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            # Тестирование ведется для авторизованного клиента
            # т.к неавторизованный будет перенаправляться
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_annon_user_cannot_create_post(self):
        create_post_url = '/create/'

        response = self.client.get(create_post_url)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)

    def test_only_author_can_edit_post(self):
        edit_post_url = f'/posts/{self.post.pk}/edit/'

        response = self.client.get(edit_post_url)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)

    def test_nonexisting_url(self):
        urls = ['/test',
                f'/{self.post.pk}',
                f'{self.group.slug}',
                f'{self.user.username}'
                ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
