from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.forms.fields import CharField, ChoiceField
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post
from ..tests.fixtures import set_up_environment

User = get_user_model()


class TestPages(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        set_up_environment(cls)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_url_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group1.slug}):
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.author.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template_name in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(HTTPStatus.OK, response.status_code)
                self.assertTemplateUsed(response, template_name)

    def test_detail_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk})
        )
        context = response.context.get('post_detail')
        self.assertIsInstance(context, Post)
        self.assertTrue(context.image, self.image)

    def _check_context(self, response):
        form_fields = {
            'text': CharField,
            'group': ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                self.assertEqual(HTTPStatus.OK, response.status_code)
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self._check_context(response)

    def test_post_edit_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk})
        )
        self._check_context(response)

    def test_post_not_in_group(self):
        response = self.client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        self.assertNotEqual(post.group, self.empty_group)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        from .. import views

        super().setUpClass()
        # Переопределяем количество постов на странице
        views.POSTS_PER_PAGE = 5
        set_up_environment(cls)
        cls.reverse_args = [
            ['posts:index', []],
            ['posts:group_posts', [cls.group1.slug]],
            ['posts:profile', [cls.author.username]]
        ]

        cls.POSTS_PER_PAGE = views.POSTS_PER_PAGE

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_check_last_post(self):
        for viewname, arg in self.reverse_args:
            response = self.client.get(reverse(viewname, args=arg))
            last_post = response.context['page_obj'][0]

            expected_text = self.posts[self.NUMBER_OF_POSTS - 1].text
            self.assertEqual(expected_text, last_post.text)
            self.assertEqual(self.group1, last_post.group)
            self.assertEqual(self.author, last_post.author)
            self.assertTrue(last_post.image)

    def test_first_page_contains_five_posts(self):
        for viewname, arg in self.reverse_args:
            response = self.client.get(reverse(viewname, args=arg))
            self.assertEqual(HTTPStatus.OK, response.status_code)
            expected_count = len(response.context['page_obj'])
            self.assertEqual(expected_count, self.POSTS_PER_PAGE)

    def test_third_page_contains_one_post(self):
        for viewname, arg in self.reverse_args:
            response = self.client.get(reverse(viewname, args=arg) + '?page=3')
            self.assertEqual(HTTPStatus.OK, response.status_code)
            expected_count = len(response.context['page_obj'])
            self.assertEqual(expected_count, 1)

    def test_caching(self):
        index_url = reverse('posts:index')
        response = self.client.get(index_url)
        Post.objects.all().delete()
        self.assertContains(response, self.posts[-1].text)
        response = self.client.get(index_url)
        posts = response.context['page_obj']
        self.assertEqual(0, len(posts))


class TestFollowService(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        set_up_environment(cls)

        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follower)

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_follow_index(self):
        follow_index_url = '/follow/'
        response = self.follower_client.get(follow_index_url)
        last_post = Post.objects.latest('pub_date')
        self.assertContains(response, last_post.text)
        response = self.authorized_client.get(follow_index_url)
        self.assertNotIn(last_post.text, response)
