from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Post
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

        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_group_cant_use_existing_slug(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group1.slug
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_can_create_post(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        posts_count = Post.objects.count()

        form_data = {'text': 'Текст из формы', 'group': self.group1.pk,
                     'image': uploaded}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_created_post = Post.objects.first()
        self.assertEqual(posts_count + 1, Post.objects.count())
        self.assertEqual(form_data['text'], last_created_post.text)
        self.assertEqual(form_data['group'], last_created_post.group.pk)
        self.assertTrue(last_created_post.image)
        self.assertEqual(response.context['user'], last_created_post.author)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        redirects_to = reverse('posts:profile',
                               kwargs={'username': self.user.username})
        self.assertRedirects(response, redirects_to)

    def test_can_edit_post(self):
        text_before = self.post.text
        text_after = 'Текст после редактирования'
        form_data = {
            'text': text_after,
            'group': self.group1.pk
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertNotEqual(text_after, text_before)
        redirects_to = reverse('posts:profile',
                               kwargs={'username': self.author.username})
        self.assertRedirects(response, redirects_to)

    def test_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий автора'
        }
        self.author_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.pk}),
            data=form_data
        )
        last_comment = Comment.objects.last()
        self.assertEqual(comment_count + 1, Comment.objects.count())
        self.assertEqual(form_data['text'], last_comment.text)
        self.assertEqual(self.author, last_comment.author)
        form_data = {
            'text': 'Комментарий комментатора'
        }
        self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.pk}),
            data=form_data
        )
        self.assertEqual(comment_count + 2, Comment.objects.count())
        last_comment = Comment.objects.last()
        self.assertEqual(form_data['text'], last_comment.text)
        self.assertEqual(self.user, last_comment.author)

    def test_follow_post(self):
        redirects_to = f'/profile/{self.author.username}/'
        followers_count_before = Follow.objects.all().count()
        response = self.authorized_client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username}),
        )
        followers_count_after = Follow.objects.all().count()
        self.assertEqual(followers_count_before + 1, followers_count_after)
        self.assertRedirects(response, redirects_to, 302, 200)

    def test_unfollow(self):
        redirects_to = f'/profile/{self.author.username}/'
        followers_count_before = Follow.objects.all().count()
        response = self.follower_client.post(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author.username}),
        )
        followers_count_after = Follow.objects.all().count()
        self.assertEqual(followers_count_after, followers_count_before - 1)
        self.assertRedirects(response, redirects_to, 302, 200)

    def test_unauthorised_cant_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Анонимный пользователь создает пост'
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        from_url = reverse('users:login')
        target_utl = reverse('posts:post_create')
        redirects_to = f'{from_url}?next={target_utl}'
        self.assertRedirects(response, redirects_to)
        self.assertEqual(posts_count, Post.objects.count())

    def test_unauthorised_cant_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Анонимный пользователь комментирует пост'
        }
        self.client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.pk}),
            data=form_data
        )

        self.assertEqual(comment_count, Comment.objects.count())

    def test_unauthorised_cant_follow(self):
        followers_count = Follow.objects.count()
        self.client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username}),
        )

        self.assertEqual(followers_count, Follow.objects.count())

    def test_author_cant_follow(self):
        followers_count = Follow.objects.count()
        with self.assertRaises(Exception):
            self.author_client.post(
                reverse('posts:profile_follow',
                        kwargs={'username': self.author.username}),
            )
            self.assertEqual(followers_count, Follow.objects.count())
