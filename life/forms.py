from django import forms

from .models import Task, Activity



class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['name', 'description', 'priority', 'completion_date']
        labels = {
            'name': 'Nazwa',
            'description': 'Opis',
            'priority': 'Priorytet',
            'completion_date': 'Data ukończenia',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'completion_date': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'date', 'duration']
        labels = {
            'name': 'Kategoria aktywności',
            'date': 'Data',
            'duration': 'Czas trwania (minuty)',
        }
        widgets = {
            'name': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
        }

