import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Movie, Book, MovieProposition, BookProposition
from .forms import MovieForm, BookForm, MoviePropositionForm, BookPropositionForm



def index(request):
    return HttpResponse("To jest aplikacja culture")


def add_errors_to_messages(request, form):
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"Błąd w polu {field}: {error}")


# FILMY

def movies_list(request):
    movies_list = Movie.objects.all().order_by("-watch_date")
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


# PROPOZYCJE    

def propositions_dashboard(request):
    movies_to_watch = MovieProposition.objects.all().order_by("-created_at")[:10]
    books_to_read = BookProposition.objects.all().order_by("-created_at")[:10]
    total_movies_to_watch = MovieProposition.objects.count()
    total_books_to_read = BookProposition.objects.count()
    watched_this_year = Movie.objects.filter(watch_date__year=datetime.datetime.now().year).count()
    read_this_year = Book.objects.filter(date_finished__year=datetime.datetime.now().year).count()
    context = {
        'movies_to_watch': movies_to_watch,
        'books_to_read': books_to_read,
        'watched_this_year': watched_this_year,
        'read_this_year': read_this_year,
        'total_movies_to_watch': total_movies_to_watch,
        'total_books_to_read': total_books_to_read,
    }
    return render(request, 'propositions/index.html', context)


def new_movie_proposition(request):
    if request.method == 'POST':
        form = MoviePropositionForm(request.POST)

        if form.is_valid():
            movie_proposition = form.save()
            return redirect('propositions_dashboard')
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = MoviePropositionForm()

    return render(request, 'propositions/new_movie_proposition.html', {'form': form})


def new_book_proposition(request):
    if request.method == 'POST':
        form = BookPropositionForm(request.POST)

        if form.is_valid():
            book_proposition = form.save()
            return redirect('propositions_dashboard')
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = BookPropositionForm()

    return render(request, 'propositions/new_book_proposition.html', {'form': form})


def delete_movie_proposition(request, pk):
    movie_proposition = get_object_or_404(MovieProposition, pk=pk)
    
    if request.method == "POST":
        movie_proposition.delete()
        return redirect('propositions_dashboard')
        
    context = {'movie_proposition': movie_proposition}
    return render(request, 'propositions/confirm_delete_movie.html', context)


def delete_book_proposition(request, pk):
    book_proposition = get_object_or_404(BookProposition, pk=pk)
    
    if request.method == "POST":
        book_proposition.delete()
        return redirect('propositions_dashboard')
        
    context = {'book_proposition': book_proposition}
    return render(request, 'propositions/confirm_delete_book.html', context)

