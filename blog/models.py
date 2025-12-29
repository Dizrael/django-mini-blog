from django.db.models import Model, CharField, SlugField, TextField, DateTimeField, Index, TextChoices, ForeignKey
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(Model):
    class Status(TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = CharField(max_length=250)
    slug = SlugField(max_length=250, unique=True)
    author = ForeignKey(User, on_delete=models.CASCADE, related_name="blog_posts")
    body = TextField()

    publish = DateTimeField(default=timezone.now)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    status = CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        indexes = [
            Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title
