from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import ImageField

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста')
    pub_date = models.DateTimeField(auto_now_add=True)

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор')
    group = models.ForeignKey(
        'Group',
        models.SET_NULL,
        blank=True,
        related_name='post_group',
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу'
    )

    image = ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             related_name='comments',
                             on_delete=models.CASCADE
                             )
    author = models.ForeignKey(User,
                               related_name='comments',
                               on_delete=models.CASCADE
                               )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             related_name='follower',
                             on_delete=models.CASCADE,
                             null=True
                             )
    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE
                               )
