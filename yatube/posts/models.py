from django.contrib.auth import get_user_model
from django.db import models

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

    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Загрузите изображение',
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
                             verbose_name='Пост',
                             on_delete=models.CASCADE
                             )
    author = models.ForeignKey(User,
                               related_name='comments',
                               verbose_name='Автор',
                               on_delete=models.CASCADE
                               )
    text = models.TextField(help_text='Напишите что-нибудь')
    created = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             verbose_name='Подписчик',
                             related_name='follower',
                             on_delete=models.CASCADE
                             )
    author = models.ForeignKey(User,
                               related_name='following',
                               verbose_name='Автор',
                               on_delete=models.CASCADE
                               )

    def save(self, *args, **kwargs):
        if self.author == self.user:
            raise Exception('Author cannot follow himself')
        super(Follow, self).save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                condition=~models.Q(user=models.F('author')),
                name='no_self_subscription'
            ),
        ]
