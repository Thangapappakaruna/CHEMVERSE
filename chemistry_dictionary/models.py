from django.db import models


class Term(models.Model):
    term = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    definition = models.TextField()
    category = models.CharField(max_length=40)
    example = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ['term']

    def __str__(self):
        return self.term

