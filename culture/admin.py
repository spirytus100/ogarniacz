from django.contrib import admin

from .models import MovieGenre, Movie, Book



admin.site.register([MovieGenre, Movie, Book])
