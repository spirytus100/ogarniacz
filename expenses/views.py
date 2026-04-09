import datetime

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.db.models import F, Sum

from .models import Expense, Budget, BudgetResult, BudgetResultExpenses, ExpensesCategories, Need, Wish
from .forms import ExpenseForm, BudgetForm, NeedForm, WishForm



def add_errors_to_messages(request, form):
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"Błąd w polu {field}: {error}")

# wydatki

def index(request):
    two_years_ago = timezone.now() - datetime.timedelta(days=730)

    expenses_list = Expense.objects.filter(
        expense_date__gte=two_years_ago
    ).annotate(
        total_price=F('quantity') * F('price')
    ).order_by('-expense_date')
    
    paginator = Paginator(expenses_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, "expenses/index.html", context)


def expense_details(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    return render(request, 'expenses/details.html', {'expense': expense})


def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)

        if form.is_valid():
            expense = form.save()
            return redirect('expenses:details', pk=expense.id)
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expenses/edit.html', {'form': form})


def new_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)

        if form.is_valid():
            expense = form.save()

            price = expense.price
            category = expense.category_id

            budget_row = Budget.objects.get(category_id=category)
            budget_row.actual_cost = F('actual_cost') + price
            budget_row.save()

            messages.success(request, "Wydatek został dodany. Budżet został zaktualizowany")

            return redirect('expenses:index')
        
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = ExpenseForm()

    return render(request, 'expenses/new.html', {'form': form})


def delete_expense(request, pk):
    # 1. Pobieramy obiekt z bazy (lub zwracamy błąd 404, jeśli nie istnieje)
    expense = get_object_or_404(Expense, pk=pk)
    
    # 2. Jeśli użytkownik kliknął "Tak, usuń" w formularzu (metoda POST)
    if request.method == "POST":
        expense.delete() # Fizyczne usunięcie rekordu z bazy
        return redirect('expenses:index') # Przekierowanie na listę potrzeb
        
    # 3. Jeśli użytkownik tylko wszedł w link "Usuń" (metoda GET), 
    # wyświetlamy stronę z prośbą o potwierdzenie
    context = {'expense': expense}
    return render(request, 'expenses/confirm_delete.html', context)

# Budżet

def budget(request):
    budget = Budget.objects.all()
    totals = budget.aggregate(
        total_expected=Sum('expected_cost'),
        total_actual=Sum('actual_cost'),
    )
    total_expected = totals['total_expected'] or Decimal('0.00')
    total_actual = totals['total_actual'] or Decimal('0.00')
    total_difference = total_expected - total_actual

    return render(request, 'budget/index.html', {
        'budget': budget,
        'total_expected': total_expected,
        'total_actual': total_actual,
        'total_difference': total_difference,
    })


def new_budget(request):
    categories = ExpensesCategories.objects.all()
    
    if request.method == 'POST':
        # Przekazujemy kategorie jako pierwszy argument do formularza
        form = BudgetForm(categories, request.POST)
        
        if form.is_valid():
            
            # zapisanie zsumowanych danych starego budżetu
            old_budget = Budget.objects.aggregate(
                sum_expected=Sum('expected_cost'),
                sum_actual=Sum('actual_cost')
            )

            total_expected = old_budget['sum_expected'] or 0
            total_actual = old_budget['sum_actual'] or 0

            month=datetime.datetime.now().month
            year=datetime.datetime.now().year

            BudgetResult.objects.create(
                month=month,
                year=year,
                budget=total_expected,
                expenses=total_actual,
                result=total_expected-total_actual
            )

            # zapisanie szczegółowych danych starego budżetu
            old_expenses = Budget.objects.all()
            print(old_expenses)
            items_to_save = []
            for budget_item in old_expenses:
                model = BudgetResultExpenses(
                    month=month,
                    year=year,
                    budget=budget_item.expected_cost,
                    expenses=budget_item.actual_cost,
                    category_id=budget_item.category_id
                )
                items_to_save.append(model)
            print(items_to_save)
            BudgetResultExpenses.objects.bulk_create(items_to_save)


            # 2. Pętla po kategoriach i zapis do bazy
            for cat in categories:
                field_name = f'category_{cat.id}'
                
                # Pobieramy wpisaną kwotę. Jeśli pole puste, dajemy 0.00
                expected = form.cleaned_data.get(field_name) or 0.00
                
                # 3. ZAPISUJEMY WIERSZ W BAZIE (lub aktualizujemy istniejący)
                Budget.objects.update_or_create(
                    category_id=cat.id, # Klucz wyszukiwania
                    
                    # Jeśli Twój budżet przypisany jest do konkretnego użytkownika,
                    # KONIECZNIE musisz to uwzględnić tutaj, żeby nie nadpisać budżetu kogoś innego!
                    # user=request.user, 
                    
                    defaults={
                        'expected_cost': expected,
                        # actual_cost i comment zostają nietknięte lub domyślne,
                        # created_at/updated_at obsługują się same
                    }
                )

            
            messages.success(request, "Zapisano dane starego budżetu")
            messages.success(request, "Utworzono nowy budżet")
            return redirect('expenses:budget')
    else:
            
        form = BudgetForm(categories)

    return render(request, 'budget/new_budget.html', {'form': form})

# Potrzeby

def needs(request):
    needs = Need.objects.all().order_by("id")
    paginator = Paginator(needs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, "needs/index.html", context)


def need_details(request, pk):
    need = get_object_or_404(Need, pk=pk)
    return render(request, 'needs/details.html', {'need': need})


def edit_need(request, pk):
    need = get_object_or_404(Need, pk=pk)

    if request.method == 'POST':
        form = NeedForm(request.POST, instance=need)

        if form.is_valid():
            need = form.save()
            return redirect('expenses:needs', pk=need.id)
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = NeedForm(instance=need)

    return render(request, 'needs/edit.html', {'form': form})


def new_need(request):
    if request.method == 'POST':
        form = NeedForm(request.POST)

        if form.is_valid():
            need = form.save()

            messages.success(request, "Potrzeba została dodana")

            return redirect('expenses:needs')
        
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = NeedForm()

    return render(request, 'needs/new.html', {'form': form})


def delete_need(request, pk):
    # 1. Pobieramy obiekt z bazy (lub zwracamy błąd 404, jeśli nie istnieje)
    need = get_object_or_404(Need, pk=pk)
    
    # 2. Jeśli użytkownik kliknął "Tak, usuń" w formularzu (metoda POST)
    if request.method == "POST":
        need.delete() # Fizyczne usunięcie rekordu z bazy
        return redirect('expenses:needs') # Przekierowanie na listę potrzeb 
        
    # 3. Jeśli użytkownik tylko wszedł w link "Usuń" (metoda GET), 
    # wyświetlamy stronę z prośbą o potwierdzenie
    context = {'need': need}
    return render(request, 'needs/confirm_delete.html', context)


# Lista życzeń


def wishes(request):
    wishes = Wish.objects.all().order_by("id")
    paginator = Paginator(wishes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, "wishes/index.html", context)


def wish_details(request, pk):
    wish = get_object_or_404(Wish, pk=pk)
    return render(request, 'wishes/details.html', {'wish': wish})


def edit_wish(request, pk):
    wish = get_object_or_404(Wish, pk=pk)

    if request.method == 'POST':
        form = WishForm(request.POST, instance=wish)

        if form.is_valid():
            wish = form.save()
            return redirect('expenses:wish_details', pk=wish.id)
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = WishForm(instance=wish)

    return render(request, 'wishes/edit.html', {'form': form})


def new_wish(request):
    if request.method == 'POST':
        form = WishForm(request.POST)

        if form.is_valid():
            wish = form.save()

            messages.success(request, "Życzenie zostało dodane")

            return redirect('expenses:wishes')
        
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = WishForm()

    return render(request, 'wishes/new.html', {'form': form})


def delete_wish(request, pk):
    # 1. Pobieramy obiekt z bazy (lub zwracamy błąd 404, jeśli nie istnieje)
    wish = get_object_or_404(Wish, pk=pk)
    
    # 2. Jeśli użytkownik kliknął "Tak, usuń" w formularzu (metoda POST)
    if request.method == "POST":
        wish.delete() # Fizyczne usunięcie rekordu z bazy
        return redirect('expenses:wishes') # Przekierowanie na listę życzeń 
        
    # 3. Jeśli użytkownik tylko wszedł w link "Usuń" (metoda GET), 
    # wyświetlamy stronę z prośbą o potwierdzenie
    context = {'wish': wish}
    return render(request, 'wishes/confirm_delete.html', context)