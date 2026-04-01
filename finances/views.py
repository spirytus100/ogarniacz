from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import F

from .models import Investment, Income, Cash

from .forms import InvestmentForm, IncomeForm, CashForm



def add_errors_to_messages(request, form):
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"Błąd w polu {field}: {error}")



def index(request):
    return HttpResponse("To jest aplikacja finances")


# Inwestycje


def list_of_investments(request):
    expenses_list = Investment.objects.filter(active=True).annotate(
        buy_total=F('buy_quantity') * F('buy_price') + F('buy_commission'),
        sell_total=F('sell_quantity') * F('sell_price') - F('sell_commission'),
        current_profit=F('current_price') * F('buy_quantity') - F('buy_total')
    ).annotate(
        profit=F('sell_total') - F('buy_total')
    ).order_by('-created_at')

    paginator = Paginator(expenses_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, "investments/investment_list.html", context)


def retirement_investments(request):
    expenses_list = Investment.objects.filter(retirement=True, active=True).annotate(
        buy_total=F('buy_quantity') * F('buy_price') + F('buy_commission'),
        sell_total=F('sell_quantity') * F('sell_price') - F('sell_commission'),
        current_profit=F('current_price') * F('buy_quantity') - F('buy_total')
    ).annotate(
        profit=F('sell_total') - F('buy_total')
    ).order_by('-created_at')

    paginator = Paginator(expenses_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, "investments/retirement_list.html", context)


def investment_details(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    return render(request, 'investments/details.html', {'investment': investment})


def edit_investment(request, pk):
    investment = get_object_or_404(Investment, pk=pk)

    if request.method == 'POST':
        form = InvestmentForm(request.POST, instance=investment)

        if form.is_valid():
            investment = form.save()

            if not investment.retirement:
                messages.success(request, "Inwestycja została zaktualizowana")
                return redirect('list_of_investments')
            else:
                messages.success(request, "Inwestycja emerytalna została zaktualizowana")
                return redirect('retirement_investments')
            
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = InvestmentForm(instance=investment)

    return render(request, 'investments/edit.html', {'form': form})


def new_investment(request):
    if request.method == 'POST':
        form = InvestmentForm(request.POST)

        if form.is_valid():
            investment = form.save()

            if not investment.retirement:
                messages.success(request, "Inwestycja została dodana")
                return redirect('list_of_investments')
            else:
                messages.success(request, "Inwestycja emerytalna została dodana")
                return redirect('retirement_investments')
        
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = InvestmentForm()

    return render(request, 'investments/new.html', {'form': form})


def delete_investment(request, pk):
    # 1. Pobieramy obiekt z bazy (lub zwracamy błąd 404, jeśli nie istnieje)
    investment = get_object_or_404(Investment, pk=pk)
    
    # 2. Jeśli użytkownik kliknął "Tak, usuń" w formularzu (metoda POST)
    if request.method == "POST":
        investment.delete() # Fizyczne usunięcie rekordu z bazy
        return redirect('list_of_investments') # Przekierowanie na listę inwestycji
        
    # 3. Jeśli użytkownik tylko wszedł w link "Usuń" (metoda GET), 
    # wyświetlamy stronę z prośbą o potwierdzenie
    context = {'investment': investment}
    return render(request, 'investments/confirm_delete.html', context)


# Incomes

def incomes(request):
    incomes = Income.objects.all().order_by("-date")
    paginator = Paginator(incomes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, "incomes/index.html", context)


def income_details(request, pk):
    income = get_object_or_404(Income, pk=pk)
    return render(request, 'incomes/details.html', {'income': income})


def edit_income(request, pk):
    income = get_object_or_404(Income, pk=pk)

    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)

        if form.is_valid():
            income = form.save()
            return redirect('income_details', pk=income.id)
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = IncomeForm(instance=income)

    return render(request, 'incomes/edit.html', {'form': form})


def new_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)

        if form.is_valid():
            income = form.save()

            messages.success(request, "Przychód został dodany")

            return redirect('incomes')
        
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = IncomeForm()

    return render(request, 'incomes/new.html', {'form': form})


def delete_income(request, pk):
    # 1. Pobieramy obiekt z bazy (lub zwracamy błąd 404, jeśli nie istnieje)
    income = get_object_or_404(Income, pk=pk)
    
    # 2. Jeśli użytkownik kliknął "Tak, usuń" w formularzu (metoda POST)
    if request.method == "POST":
        income.delete() # Fizyczne usunięcie rekordu z bazy
        return redirect('incomes') # Przekierowanie na listę przychodów     
        
    # 3. Jeśli użytkownik tylko wszedł w link "Usuń" (metoda GET), 
    # wyświetlamy stronę z prośbą o potwierdzenie
    context = {'income': income}
    return render(request, 'incomes/confirm_delete.html', context)


# cash

def cash(request):
    cash = Cash.objects.all().order_by("id")
    return render(request, "cash/index.html", {'cash': cash})


def edit_cash(request, pk):
    cash = get_object_or_404(Cash, pk=pk)

    if request.method == 'POST':
        form = CashForm(request.POST, instance=cash)

        if form.is_valid():
            cash = form.save()
            return redirect('cash')
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = CashForm(instance=cash)

    return render(request, 'cash/edit.html', {'form': form})

