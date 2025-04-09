# Generated by Django 5.2 on 2025-04-09 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_post_curtidas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='curtidas',
        ),
        migrations.AddField(
            model_name='post',
            name='imagem',
            field=models.ImageField(blank=True, null=True, upload_to='imagens_posts/'),
        ),
    ]
