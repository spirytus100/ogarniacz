from django import forms

from .models import Investment, InvestmentCategory, Income, IncomeCategory, Cash


class InvestmentForm(forms.ModelForm):

    category_id = forms.ModelChoiceField(
        queryset=InvestmentCategory.objects.all(),
        label='Kategoria',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Investment
        fields = ['name', 'category_id', 'buy_date', 'buy_quantity', 'buy_price', 'buy_commission', 'current_price', 'current_price_date', 'sell_date', 'sell_quantity', 'sell_price', 'sell_commission', 'active', 'interest_rate', 'currency', 'retirement']
        labels = {
            'name': 'Nazwa',
            'category_id': 'Kategoria',
            'buy_date': 'Data zakupu',
            'buy_quantity': 'Ilość',
            'buy_price': 'Cena zakupu',
            'buy_commission': 'Prowizja zakupu',
            'current_price': 'Aktualna cena',
            'current_price_date': 'Data aktualnej ceny',
            'sell_date': 'Data sprzedaży',
            'sell_quantity': 'Ilość',
            'sell_price': 'Cena sprzedaży',
            'sell_commission': 'Prowizja sprzedaży',
            'active': 'Aktywna',
            'interest_rate': 'Stopa procentowa',
            'currency': 'Waluta',
            'retirement': 'Emerytura'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'buy_date': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'buy_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'buy_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'buy_commission': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'current_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'current_price_date': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'sell_date': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'sell_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'sell_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'sell_commission': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'interest_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001',
                'min': '0',
            }),
            'currency': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '3',
            }),
            'retirement': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class IncomeForm(forms.ModelForm):

    class Meta:
        model = Income
        fields = ['name', 'category', 'date', 'value']
        labels = {
            'name': 'Nazwa',
            'category': 'Kategoria',
            'date': 'Data',
            'value': 'Wartość',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date': forms.DateInput(format='%Y-%m-%d', attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
        }


class CashForm(forms.ModelForm):

    class Meta:
        model = Cash
        fields = ['name', 'value']
        labels = {
            'name': 'Nazwa',
            'value': 'Wartość',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
            }),
        }

