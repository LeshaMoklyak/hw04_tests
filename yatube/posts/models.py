from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

NUMBER_OF_CHAR_TEXT = 15


class Group(models.Model):
    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.text[:NUMBER_OF_CHAR_TEXT]

    class Meta:
        ordering = ['-pub_date']
        default_related_name = '%(app_label)s'
