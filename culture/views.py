from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Movie, Book
from .forms import MovieForm, BookForm



def index(request):
    return HttpResponse("To jest aplikacja culture")


def add_errors_to_messages(request, form):
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"Błąd w polu {field}: {error}")


# FILMY

def movies_list(request):
    movies_list = Movie.objects.all().order_by("-id")
    paginator = Paginator(movies_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, "movies/index.html", context)


def movie_details(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, 'movies/details.html', {'movie': movie})


def edit_movie(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    if request.method == 'POST':
        form = MovieForm(request.POST, instance=movie)

        if form.is_valid():
            movie = form.save()
            return redirect('movie_details', pk=movie.id)
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = MovieForm(instance=movie)

    return render(request, 'movies/edit.html', {'form': form})


def new_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST)

        if form.is_valid():
            movie = form.save()
            return redirect('movies_list')
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = MovieForm()

    return render(request, 'movies/new.html', {'form': form})


def delete_movie(request, pk):
    # 1. Pobieramy obiekt z bazy (lub zwracamy błąd 404, jeśli nie istnieje)
    movie = get_object_or_404(Movie, pk=pk)
    
    # 2. Jeśli użytkownik kliknął "Tak, usuń" w formularzu (metoda POST)
    if request.method == "POST":
        movie.delete() # Fizyczne usunięcie rekordu z bazy
        return redirect('movies_list') # Przekierowanie na listę filmów
        
    # 3. Jeśli użytkownik tylko wszedł w link "Usuń" (metoda GET), 
    # wyświetlamy stronę z prośbą o potwierdzenie
    context = {'movie': movie}
    return render(request, 'movies/confirm_delete.html', context)


# KSIĄŻKI

def books_list(request):
    books_list = Book.objects.all().order_by("-id")
    paginator = Paginator(books_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, "books/index.html", context)


def book_details(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/details.html', {'book': book})


def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)

        if form.is_valid():
            book = form.save()
            return redirect('book_details', pk=book.id)
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = BookForm(instance=book)

    return render(request, 'books/edit.html', {'form': form})


def new_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)

        if form.is_valid():
            book = form.save()
            return redirect('books_list')
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = BookForm()

    return render(request, 'books/new.html', {'form': form})


def delete_book(request, pk):
    # 1. Pobieramy obiekt z bazy (lub zwracamy błąd 404, jeśli nie istnieje)
    book = get_object_or_404(Book, pk=pk)
    
    # 2. Jeśli użytkownik kliknął "Tak, usuń" w formularzu (metoda POST)
    if request.method == "POST":
        book.delete() # Fizyczne usunięcie rekordu z bazy
        return redirect('books_list') # Przekierowanie na listę książek
        
    # 3. Jeśli użytkownik tylko wszedł w link "Usuń" (metoda GET), 
    # wyświetlamy stronę z prośbą o potwierdzenie
    context = {'book': book}
    return render(request, 'books/confirm_delete.html', context)

