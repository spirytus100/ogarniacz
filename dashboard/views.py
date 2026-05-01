import datetime
import json

from django.shortcuts import render
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Cast
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.utils import timezone

from finances.models import Investment, Cash, Crypto, ExchangeRate, Income
from expenses.models import Expense, Budget



def get_total_wealth():
    result = Investment.objects.filter(
        active=True
    ).aggregate(
        total_value=Sum(
            Cast(F('buy_quantity'), output_field=DecimalField(max_digits=10, decimal_places=2)) * F('buy_price') - F('buy_commission'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
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
            Cast(F('quantity'), output_field=DecimalField(max_digits=10, decimal_places=2)) * F('price'),
            output_field=DecimalField(max_digits=10, decimal_places=2),
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


def dashboard_chart_view():
    today = timezone.now().date()
    
    # 1. Generujemy listę 6 ostatnich miesięcy (od najstarszego do obecnego)
    months_list =[]
    for i in range(6):
        month = today.month - i
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        # Dodajemy na początek listy, aby wykres szedł chronologicznie (od lewej do prawej)
        months_list.insert(0, (year, month))
        
    # Wyznaczamy datę początkową do filtrowania zapytań
    start_date = datetime.date(months_list[0][0], months_list[0][1], 1)
    
    # 2. Pobieramy zgrupowane po miesiącach sumy z bazy danych
    expenses = Expense.objects.filter(expense_date__gte=start_date)\
        .annotate(month=TruncMonth('expense_date'))\
        .values('month')\
        .annotate(total=Sum(Cast(F('price'), output_field=DecimalField(max_digits=10, decimal_places=2)) * Cast(F('quantity'), output_field=DecimalField(max_digits=10, decimal_places=2)), output_field=DecimalField(max_digits=10, decimal_places=2)))
        
    incomes = Income.objects.filter(date__gte=start_date)\
        .annotate(month=TruncMonth('date'))\
        .values('month')\
        .annotate(total=Sum('value'))
        
    # 3. Mapujemy wyniki do słowników, gdzie kluczem jest 'YYYY-MM'
    # Pozwoli to łatwo odszukać kwotę dla konkretnego miesiąca
    expense_dict = {f"{item['month'].year}-{item['month'].month:02d}": item['total'] for item in expenses}
    income_dict = {f"{item['month'].year}-{item['month'].month:02d}": item['total'] for item in incomes}
    
    # 4. Przygotowujemy dane do Chart.js
    labels = []
    expense_data =[]
    income_data = []
    
    # Krótkie nazwy miesięcy do wyświetlenia na osi X
    month_names =["Sty", "Lut", "Mar", "Kwi", "Maj", "Cze", "Lip", "Sie", "Wrz", "Paź", "Lis", "Gru"]
    
    for year, month in months_list:
        key = f"{year}-{month:02d}"
        labels.append(f"{month_names[month-1]} {year}")
        
        # Pobieramy wartość ze słownika lub 0 jeśli w danym miesiącu nic nie było
        # Rzutujemy na float, ponieważ Decimal z Django nie jest domyślnie serializowalny do JSON
        expense_data.append(float(expense_dict.get(key, 0)))
        income_data.append(float(income_dict.get(key, 0)))

    # 5. Przekazujemy zserializowane dane do szablonu
    context = {
        'labels': json.dumps(labels),
        'expense_data': json.dumps(expense_data),
        'income_data': json.dumps(income_data),
    }
    
    return context



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
    chart_context = dashboard_chart_view()


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
        "chart_context": chart_context,
    })
