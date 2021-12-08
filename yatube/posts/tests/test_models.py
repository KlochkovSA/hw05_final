from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Group, Post

User = get_user_model()


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Автор поста')
        cls.commentator = User.objects.create_user(username='комментатор')
        cls.group = Group.objects.create(
            title='ТЕСТ Группа',
            slug='test_group_slug',
            description='Группа созданная во время исполнения теста'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.commentator,
            text='Абырвалг'
        )

    def test_object_names(self):
        object_names = {ModelsTest.group.title: ModelsTest.group,
                        ModelsTest.post.text: ModelsTest.post}

        for expected, obj_to_check in object_names.items():
            given = str(obj_to_check)
            with self.subTest(given):
                self.assertEqual(expected, given)

    def test_post_verbose_names(self):
        field_verbose = {'author': 'Автор',
                         'group': 'Группа'
                         }
        post = ModelsTest.post
        for field_name, expected in field_verbose.items():
            with self.subTest(value=field_name):
                self.assertEqual(expected,
                                 post._meta.get_field(field_name).verbose_name)

    def test_post_help_texts(self):
        field_verbose = {'group': 'Выберите группу',
                         'text': 'Введите текст поста'
                         }
        post = ModelsTest.post
        for field_name, expected in field_verbose.items():
            with self.subTest(value=field_name):
                self.assertEqual(expected,
                                 post._meta.get_field(field_name).help_text)

    def test_delete_post(self):
        Post.objects.last().delete()
        after = Comment.objects.count()
        self.assertEqual(0, after)

    def test_delete_user(self):
        User.objects.get(username='Автор поста').delete()
        after = Comment.objects.count()
        self.assertEqual(0, after)
