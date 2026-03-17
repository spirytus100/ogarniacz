from django import forms
from .models import Book, Movie, MovieGenre



class MovieForm(forms.ModelForm):

    genre_id = forms.ModelChoiceField(
        queryset=MovieGenre.objects.all(),
        label='Gatunek filmu',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Movie
        fields = ['title', 'production_year', 'genre_id', 'production_country', 'watch_date', 'rating']
        labels = {
            'title': 'Tytuł',
            'production_year': 'Rok produkcji',
            'genre_id': 'Gatunek',
            'production_country': 'Kraj produkcji',
            'watch_date': 'Data obejrzenia',
            'rating': 'Ocena'
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'production_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1900,
                'max': 2099 
            }),
            'production_country': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'watch_date': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
        }


class BookForm(forms.ModelForm):

    class Meta:
        model = Book
        fields = ['author', 'title', 'published_year', 'date_finished', 'rating', 'number_of_pages']
        labels = {
            'author': 'Autor',
            'title': 'Tytuł',
            'published_year': 'Rok publikacji',
            'date_finished': 'Data przeczytania',
            'rating': 'Ocena',
            'number_of_pages': 'Komentarz'
        }
        widgets = {
            'author': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'published_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1500,
                'max': 2099 
            }),
            'date_finished': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'number_of_pages': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 3000
            }),
        }