from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Post
from ..tests.fixtures import set_up_environment

User = get_user_model()


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        set_up_environment(cls)

    def test_object_names(self):
        object_names = {self.group1.title: self.group1,
                        self.post.text[:15]: self.post}

        for expected, obj_to_check in object_names.items():
            given = str(obj_to_check)
            with self.subTest(given):
                self.assertEqual(expected, given)

    def test_post_verbose_names(self):
        field_verbose = {'author': 'Автор',
                         'group': 'Группа',
                         'image': 'Картинка'
                         }
        post = self.post
        for field_name, expected in field_verbose.items():
            with self.subTest(value=field_name):
                self.assertEqual(expected,
                                 post._meta.get_field(field_name).verbose_name)

    def test_comment_verbose_names(self):
        field_verbose = {'author': 'Автор',
                         'post': 'Пост'
                         }
        comment = self.comment
        for field_name, expected in field_verbose.items():
            with self.subTest(value=field_name):
                self.assertEqual(expected,
                                 comment._meta.get_field(field_name)
                                 .verbose_name)

    def test_follow_verbose_names(self):
        field_verbose = {'author': 'Автор',
                         'user': 'Подписчик'
                         }
        follow = self.follow
        for field_name, expected in field_verbose.items():
            with self.subTest(value=field_name):
                self.assertEqual(expected,
                                 follow._meta.get_field(field_name)
                                 .verbose_name)

    def test_post_help_texts(self):
        field_verbose = {'group': 'Выберите группу',
                         'text': 'Введите текст поста',
                         'image': 'Загрузите изображение'
                         }
        post = self.post
        for field_name, expected in field_verbose.items():
            with self.subTest(value=field_name):
                self.assertEqual(expected,
                                 post._meta.get_field(field_name)
                                 .help_text)

    def test_comment_help_texts(self):
        field_verbose = {'text': 'Напишите что-нибудь'}
        post = self.comment
        for field_name, expected in field_verbose.items():
            with self.subTest(value=field_name):
                self.assertEqual(expected,
                                 post._meta.get_field(field_name)
                                 .help_text)

    def test_follow(self):
        follows_count_before = Follow.objects.all().count()
        Follow.objects.create(author=self.author, user=self.user)
        follows_count_after = Follow.objects.all().count()
        self.assertEqual(follows_count_before + 1, follows_count_after)

    def test_delete_author_clear_posts(self):
        last_post = Post.objects.latest('pub_date')
        posts_qty_before = last_post.author.posts.count()
        self.assertEqual(self.POSTS_QTY, posts_qty_before)

        last_post.author.delete()

        posts_qty_after = Post.objects.all().count()
        self.assertEqual(self.POSTS_QTY - posts_qty_before, posts_qty_after)

    def test_delete_post_clear_comments(self):
        before = Comment.objects.count()
        self.assertEqual(1, before)

        Post.objects.earliest('pub_date').delete()

        after = Comment.objects.count()
        self.assertEqual(0, after)

    def test_delete_author_delete_follow(self):
        last_post = Post.objects.latest('pub_date')
        followers_qty = Follow.objects.all().filter(author=self.author).count()
        self.assertEqual(1, followers_qty)

        last_post.author.delete()

        after = Follow.objects.all().count()
        self.assertEqual(0, after)

    def test_cannot_follow_himself(self):
        follows_count_before = Follow.objects.all().count()
        with self.assertRaises(Exception):
            Follow.objects.create(user=self.author, author=self.author)
            follows_count_after = Follow.objects.all().count()
            self.assertEqual(follows_count_before, follows_count_after)

    def tearDown(self):
        del self
