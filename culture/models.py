from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



class MovieGenre(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200, unique=True)
    production_year = models.SmallIntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2100)])
    genre_id = models.ForeignKey(MovieGenre, null=True, on_delete=models.SET_NULL)
    production_country = models.CharField(max_length=50, blank=True)
    watch_date = models.DateField()
    rating = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.title


class Book(models.Model):
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=200, unique=True)
    published_year = models.SmallIntegerField(validators=[MinValueValidator(1500), MaxValueValidator(2100)])
    date_finished = models.DateField()
    rating = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    number_of_pages = models.SmallIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return ", ".join((self.author, self.title))
    

class MovieSuggestion(models.Model):
    title = models.CharField(max_length=200, unique=True)
    genre_id = models.ForeignKey(MovieGenre, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class BookSuggestion(models.Model):
    author = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
