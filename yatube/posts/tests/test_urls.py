from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Follow
from ..tests.fixtures import set_up_environment

User = get_user_model()


class TestPostsURLS(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        set_up_environment(cls)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

    def test_urls_uses_correct_template_all(self):
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group1.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in templates_url_names.items():
            # Тестирование ведется для авторизованного клиента
            # т.к неавторизованный будет перенаправляться
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_annon_user_cannot_create_post(self):
        create_post_url = '/create/'
        redirects_to = f'/auth/login/?next={create_post_url}'

        response = self.client.get(create_post_url)
        self.assertRedirects(response, redirects_to)

    def test_annon_user_cannot_comment(self):
        comment_url = f'/posts/{self.post.pk}/comment/'
        redirects_to = f'/auth/login/?next={comment_url}'

        response = self.client.get(comment_url)
        self.assertRedirects(response, redirects_to)

    def test_annon_user_cannot_follow(self):
        follow_url = f'/profile/{self.user.username}/follow/'
        redirects_to = f'/auth/login/?next={follow_url}'

        response = self.client.get(follow_url)
        self.assertRedirects(response, redirects_to)

    def test_annon_user_cannot_see_follow_index(self):
        follow_index_url = '/follow/'
        redirects_to = f'/auth/login/?next={follow_index_url}'

        response = self.client.get(follow_index_url)
        self.assertRedirects(response, redirects_to)

    def test_edit_post_url(self):
        edit_post_url = f'/posts/{self.post.pk}/edit/'

        response = self.authorised_client.get(edit_post_url)
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_comment_url(self):
        comment_url = f'/posts/{self.post.pk}/comment/'
        redirects_to = f'/posts/{self.post.pk}/'

        response = self.authorised_client.get(comment_url)
        self.assertRedirects(response, redirects_to)

    def test_author_cannot_follow(self):
        follow_url = f'/profile/{self.author.username}/follow/'
        redirects_to = f'/profile/{self.author.username}/'
        followers_count = self.author.following.count()
        self.assertEqual(1, followers_count)
        response = self.author_client.get(follow_url)
        self.assertRedirects(response, redirects_to)
        self.assertEqual(followers_count, Follow.objects.all().count())

    def test_nonexisting_url(self):
        urls = ['/test',
                f'/{self.post.pk}',
                f'{self.group1.slug}',
                f'{self.user.username}'
                ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
