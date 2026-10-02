from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extended Django user — room for future profile fields."""

    class Meta:
        verbose_name = 'korisnik'
        verbose_name_plural = 'korisnici'
