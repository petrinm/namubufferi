from base64 import b64encode
from datetime import timedelta
from hashlib import sha256
from os import urandom

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


def generate_magic_token():
    magic = b64encode(sha256(urandom(32)).digest(), '-_')
    print magic
    return magic


class MagicToken(models.Model):
    user = models.OneToOneField(User)
    magic_token = models.CharField(max_length=44, unique=True, default=generate_magic_token)
    magic_token_ttl = models.DateTimeField(default=(timezone.now() + timedelta(minutes=15)))  # TODO: Static

    def update(self):
        self.magic_token_ttl = timezone.now() + timedelta(minutes=15)
        self.magic_token = generate_magic_token()
        self.save()
        return self.magic_token

    def deactivate(self):
        self.magic_token = generate_magic_token()
        self.magic_token_ttl = timezone.now()
        self.save()

    def is_alive(self):
        return timezone.now() < self.magic_token_ttl
