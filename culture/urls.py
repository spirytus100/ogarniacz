from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("movies/", views.movies_list, name="movies_list"),
    path("movies/<int:pk>/", views.movie_details, name="movie_details"),
    path("movies/<int:pk>/edit", views.edit_movie, name="edit_movie"),
    path("movies/new", views.new_movie, name="new_movie"),
    path("movies/<int:pk>/delete", views.delete_movie, name="delete_movie"),
    path("books/", views.books_list, name="books_list"),
    path("books/<int:pk>/", views.book_details, name="book_details"),
    path("books/<int:pk>/edit", views.edit_book, name="edit_book"),
    path("books/new", views.new_book, name="new_book"),
    path("books/<int:pk>/delete", views.delete_book, name="delete_book"),
]