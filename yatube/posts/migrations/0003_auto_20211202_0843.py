# Generated by Django 2.2.16 on 2021-12-02 08:43

from django.db import migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=sorl.thumbnail.fields.ImageField(blank=True, upload_to='posts/', verbose_name='Картинка'),
        ),
    ]