import datetime

from django.shortcuts import render
from django.db.models import Sum, F
from django.utils import timezone

from finances.models import Investment, Cash, Crypto, ExchangeRate, Income
from expenses.models import Expense, Budget



def get_total_wealth():
    result = Investment.objects.filter(
        active=True
    ).aggregate(
        total_value=Sum(
            F('buy_quantity') * F('buy_price') - F('buy_commission'),
            default=0
        )
    )

    investments_total = result['total_value'] or 0

    cash_total = Cash.objects.aggregate(Sum("value"))["value__sum"] or 0
    crypto_total = Crypto.objects.aggregate(Sum("value"))["value__sum"] or 0

    return cash_total + crypto_total + investments_total


def get_current_month_expenses():
    # 1. Pobieramy dzisiejszą datę (np. marzec 2026)
    today = timezone.now()
    
    # 2. Tworzymy zapytanie ORM
    result = Expense.objects.filter(
        expense_date__year=today.year,     # Filtrujemy po obecnym roku
        expense_date__month=today.month    # Filtrujemy po obecnym miesiącu
    ).aggregate(
        total_spent=Sum(
            F('quantity') * F('price'), # Zgodnie z Twoim modelem
            default=0                   # Zabezpieczenie przed błędem w przypadku braku wydatków
        )
    )
    
    # 3. Zwracamy samą wyliczoną kwotę
    return result['total_spent']


def get_current_month_income():
    # 1. Pobieramy dzisiejszą datę (np. marzec 2026)
    today = timezone.now()
    
    # 2. Tworzymy zapytanie ORM
    result = Income.objects.filter(
        date__year=today.year,     # Filtrujemy po obecnym roku
        date__month=today.month    # Filtrujemy po obecnym miesiącu
    ).aggregate(
        total_income=Sum('value', default=0) # Zakładam, że masz pole 'amount' w modelu Income
    )
    
    # 3. Zwracamy samą wyliczoną kwotę
    return result['total_income']


def get_current_month_budget():
    today = timezone.now()
    result = Budget.objects.aggregate(
        total_budget=Sum('expected_cost', default=0)
    )
    return result['total_budget']


def get_top_categories():
    # 1. Pobieramy 3 najwyższe budżety (bez .values(), żeby mieć pełne obiekty)
    top_budgets_qs = Budget.objects.order_by('-actual_cost')[:5]
    
    # 2. Definiujemy kolory dla 1, 2 i 3 miejsca (klasy z Bootstrapa)
    colors = ['danger', 'primary', 'info', 'light', 'success']  # Możesz dodać więcej kolorów, jeśli chcesz wyświetlać więcej niż 3 kategorie
    
    # 3. Przygotowujemy nową listę z wyliczonymi procentami
    top_budgets =[]
    for index, budget in enumerate(top_budgets_qs):
        
        # Zabezpieczenie przed dzieleniem przez zero (gdyby expected_cost wynosiło 0)
        if budget.expected_cost and budget.expected_cost > 0:
            percent = (budget.actual_cost / budget.expected_cost) * 100

        elif budget.actual_cost > budget.expected_cost:
            percent = 100  # Jeśli wydatki przekraczają budżet, ustawiamy 100%

        else:
            percent = 0
            
        top_budgets.append({
            # Jeśli category_id to klucz obcy (ForeignKey), użyj: budget.category_id.name
            'category_name': budget.category_id, 
            'cost': budget.actual_cost,
            
            # min(percent, 100) ucina pasek do 100%, żeby graficznie nie "wyjechał" za kartę,
            # jeśli wydatki przekroczą zaplanowany budżet (np. 120%)
            'bar_width': min(round(percent), 100), 
            
            # Przypisujemy kolor (np. dla index=0 będzie to 'danger')
            'color': colors[index] if index < len(colors) else 'secondary'
        })
        
    # 4. Przekazujemy listę do szablonu
    return top_budgets


def get_used_budget_amounts():
    result = Budget.objects.aggregate(
        total_budget=Sum('expected_cost', default=0),
        total_actual=Sum('actual_cost', default=0)
    )

    amount_left = result['total_budget'] - result['total_actual']
    used_budget_percentage = result['total_actual'] / result['total_budget'] if result['total_budget'] else 0
    return amount_left, round(used_budget_percentage * 100)


def get_last_three_expenses():
    expenses_qs = Expense.objects.order_by('-expense_date')[:3]
    expenses = []
    for expense in expenses_qs:
        total_cost = expense.quantity * expense.price
        expenses.append({
            'item': expense.item,
            'total_cost': total_cost,
            'date': expense.expense_date.strftime("%d.%m.%Y") if expense.expense_date != datetime.date.today() else "Dziś"
        })
    return expenses


def get_last_three_incomes():
    incomes_qs = Income.objects.order_by('-date')[:3]
    incomes = []
    for income in incomes_qs:
        incomes.append({
            'source': income.name,
            'value': income.value,
            'date': income.date.strftime("%d.%m.%Y") if income.date != datetime.date.today() else "Dziś"
        })
    return incomes



def index(request):
    total_wealth = get_total_wealth()
    current_month_expenses = get_current_month_expenses()
    current_month_budget = get_current_month_budget()
    balance = current_month_budget - current_month_expenses
    overspent = False
    if balance < 0:
        overspent = True
        balance = balance * -1
    current_month_income = get_current_month_income()
    top_categories = get_top_categories()
    budget_amount_left, used_budget_percentage = get_used_budget_amounts()
    last_three_expenses = get_last_three_expenses()
    last_three_incomes = get_last_three_incomes()


    return render(request, "dashboard/index.html", {
        "total_wealth": total_wealth,
        "current_month_expenses": current_month_expenses,
        "current_month_income": current_month_income,
        "overspent": overspent,
        "balance": balance,
        "top_categories": top_categories,
        "used_budget_percentage": used_budget_percentage,
        "last_three_expenses": last_three_expenses,
        "last_three_incomes": last_three_incomes,
        "budget_amount_left": budget_amount_left,
    })
