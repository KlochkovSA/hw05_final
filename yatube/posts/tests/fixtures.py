from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Comment, Follow, Group, Post

User = get_user_model()


def set_up_environment(cls):
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

    cls.author = User.objects.create_user(username='author')
    cls.user = User.objects.create_user(username='user')
    cls.follower = User.objects.create_user(username='follower')

    cls.group1 = Group.objects.create(
        title='ТЕСТ Группа',
        slug='group1',
        description='Группа 1 созданная во время исполнения теста'
    )
    cls.empty_group = Group.objects.create(
        title='ТЕСТ Группа2 ПУСТАЯ',
        slug='group2',
        description='Группа 2 созданная во время исполнения теста'
    )

    cls.post = Post.objects.create(
        author=cls.author,
        text='Первый пост в БД',
        group=cls.group1,
        image=cls.image
    )

    cls.NUMBER_OF_POSTS = 10

    cls.posts = Post.objects.bulk_create([
        Post(author=cls.author,
             text=f'Тестовый пост {i}',
             group=cls.group1,
             image=cls.image
             ) for i in range(cls.NUMBER_OF_POSTS)
    ])

    cls.follow = Follow.objects.create(user=cls.follower,
                                       author=cls.author
                                       )

    cls.comment = Comment.objects.create(
        post=cls.post,
        author=cls.follower,
        text='Абырвалг'
    )
    cls.POSTS_QTY = len(cls.posts) + 1
    return cls
