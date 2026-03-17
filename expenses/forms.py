from django import forms

from .models import Expense, ExpensesCategories, Need, Wish



class ExpenseForm(forms.ModelForm):

    category_id = forms.ModelChoiceField(
        queryset=ExpensesCategories.objects.all(),
        label='Kategoria',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Expense
        fields = ['item', 'price', 'quantity', 'category_id', 'date', 'company']
        labels = {
            'item': 'Przedmiot',
            'price': 'Cena',
            'quantity': 'Ilość',
            'category_id': 'Kategoria',
            'date': 'Data',
            'company': 'Firma'
        }
        widgets = {
            'item': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 999 
            }),
            'date': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }


class BudgetForm(forms.Form):
    
    def __init__(self, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tworzymy dynamicznie pola na podstawie przekazanych kategorii
        for cat in categories:
            # Nazwa pola to np. "category_1", "category_2" (gdzie 1 i 2 to ID)
            field_name = f'category_{cat.id}'
            field_value = self.initial.get(field_name, None)
            
            self.fields[field_name] = forms.DecimalField(
                label=cat.name, # Tu podaj nazwę pola w Twoim modelu Kategorii (np. cat.title)
                initial=field_value,
                max_digits=10, 
                decimal_places=2, 
                required=False,
                widget=forms.NumberInput(attrs={
                    'class': 'form-control form-control-sm text-end fw-bold',
                    'step': '0.01',
                    'min': '0',
                    'placeholder': '0.00'
                })
            )


class NeedForm(forms.ModelForm):

    category_id = forms.ModelChoiceField(
        queryset=ExpensesCategories.objects.all(),
        label='Kategoria',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Need
        fields = ['item', 'category_id', 'price']
        labels = {
            'item': 'Przedmiot',
            'category_id': 'Kategoria',
            'price': 'Cena',
        }
        widgets = {
            'item': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
        }


class WishForm(forms.ModelForm):

    category_id = forms.ModelChoiceField(
        queryset=ExpensesCategories.objects.all(),
        label='Kategoria',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Wish
        fields = ['item', 'category_id', 'price']
        labels = {
            'item': 'Przedmiot',
            'category_id': 'Kategoria',
            'price': 'Szacowana cena',
        }
        widgets = {
            'item': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
        }
