from django.contrib import admin

from .models import MovieGenre, Movie, Book, MovieProposition, BookProposition



admin.site.register([MovieGenre, Movie, Book, MovieProposition, BookProposition])
