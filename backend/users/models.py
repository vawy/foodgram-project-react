from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import (
    CharField, EmailField, UniqueConstraint, Model, ForeignKey, CASCADE
)
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Кастомная модель User.
    При создании юзера все поля обязательные
    """
    first_name = CharField(
        'Имя',
        max_length=200,
    )
    last_name = CharField(
        'Фамилия',
        max_length=200,
    )
    username = CharField(
        'Логин',
        unique=True,
        max_length=150,
        validators=[
            RegexValidator(
                r'^[0-9a-zA-Z]*$',
                message='Введите логин как указано в подсказке'
            )
        ],
        help_text='Логин может состоять только из латинских букв и цифр'
    )
    email = EmailField(
        'Email',
        unique=True,
        max_length=200
    )
    password = CharField(
        'Пароль',
        max_length=200
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            )
        ]

    def __str__(self):
        return self.username


class Follow(Model):
    user = ForeignKey(
        CustomUser,
        related_name='followers',
        verbose_name='Подписчик',
        on_delete=CASCADE
    )
    author = ForeignKey(
        CustomUser,
        related_name='followings',
        verbose_name='Автор',
        on_delete=CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(
                fields=['author', 'user'],
                name='unique_follower'
            )
        ]

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.user == self.author:
            raise ValidationError("Невозможно подписаться на себя")
        super().save()

    def __str__(self):
        return f'Автор: {self.author}, подписчик: {self.user}'
