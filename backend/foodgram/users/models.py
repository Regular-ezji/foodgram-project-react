from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ'
        )],
        verbose_name='Никнейм',
    )
    password = models.CharField(
        max_length=50,
        blank=False,
        verbose_name='Пароль',

    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        verbose_name='Электронная почта',
    )
    first_name = models.TextField(
        max_length=150,
        null=True,
        blank=False,
        verbose_name='Имя',
    )
    last_name = models.TextField(
        max_length=150,
        null=True,
        blank=False,
        verbose_name='Фамилия',
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        models.UniqueConstraint(
            fields=['user', 'author'],
            name='author_and_user_unique'
        )

    def __str__(self):
        return (
            f'Пользователь {self.user_id}'
            f'подписан на пользователя {self.author_id}'
        )
