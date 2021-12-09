from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.fields import CharField, ChoiceField
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class TestPages(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='ТЕСТ Группа',
            slug='test_group_slug',
            description='Группа созданная во время исполнения теста'
        )
        cls.group2 = Group.objects.create(
            title='ТЕСТ Группа2',
            slug='test_group_slug_2',
            description='Группа 2 созданная во время исполнения теста'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.image
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_url_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html'
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
        self.assertNotEqual(post.group, self.group2)


class PaginatorViewsTest(TestCase):
    _n_records_page1 = 10
    _n_records_page2 = 7

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='ТЕСТ Группа',
            slug='test_group_slug',
            description='Группа созданная во время исполнения теста'
        )
        cls.reverse_args = [
            ['posts:index', []],
            ['posts:group_posts', [cls.group.slug]],
            ['posts:profile', [cls.user.username]]
        ]

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.posts = Post.objects.bulk_create([
            Post(author=cls.user,
                 text=f'Тестовый пост {i}',
                 group=cls.group,
                 image=cls.image
                 ) for i in range(PaginatorViewsTest._n_records_page1
                                  + PaginatorViewsTest._n_records_page2)
        ])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_check_last_post(self):
        for viewname, arg in self.reverse_args:
            response = self.client.get(reverse(viewname, args=arg))
            last_post = response.context['page_obj'][0]
            last_post_idx = (PaginatorViewsTest._n_records_page1
                             + PaginatorViewsTest._n_records_page2)

            expected_text = self.posts[last_post_idx - 1].text
            self.assertEqual(expected_text, last_post.text)
            self.assertEqual(last_post.group, self.group)
            self.assertEqual(last_post.author, self.user)
            self.assertTrue(last_post.image)

    def test_first_page_contains_ten_records(self):
        for viewname, arg in self.reverse_args:
            response = self.client.get(reverse(viewname, args=arg))
            self.assertEqual(HTTPStatus.OK, response.status_code)
            expected_count = len(response.context['page_obj'])
            self.assertEqual(expected_count, self._n_records_page1)

    def test_second_page_contains_three_records(self):
        for viewname, arg in self.reverse_args:
            response = self.client.get(reverse(viewname, args=arg) + '?page=2')
            self.assertEqual(HTTPStatus.OK, response.status_code)
            expected_count = len(response.context['page_obj'])
            self.assertEqual(expected_count, self._n_records_page2)

    def test_caching(self):
        response = self.client.get(reverse('posts:index'))
        Post.objects.all().delete()
        self.assertContains(response, self.posts[-1].text)
        response = self.client.get(reverse('posts:index'))
        posts = response.context['page_obj']
        self.assertEqual(0, len(posts))
