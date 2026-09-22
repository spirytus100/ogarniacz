from decimal import Decimal
from datetime import timedelta
import json

from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import F, Subquery, OuterRef, DecimalField, ExpressionWrapper, Sum, Value
from django.db.models.functions import Coalesce, Cast
import constance

from .models import Investment, Income, ExchangeRate, Crypto, FinancialAccount

from .forms import InvestmentForm, IncomeForm, FinancialAccountForm

from dashboard.views import get_total_wealth



def add_errors_to_messages(request, form):
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"Błąd w polu {field}: {error}")



### Widok główny dla finansów ###

def get_savings():
    # 1. Podzapytanie pobierające najnowszy kurs dla danej waluty inwestycji
    exchange_rate_subquery = ExchangeRate.objects.filter(
        currency=OuterRef('exchange_rate_id__currency')
    ).order_by('-updated_at').values('rate')[:1]

    # 2. Wyciągnięcie kursu i przemnożenie go wewnątrz zapytania agregującego
    result = Investment.objects.filter(
        active=True,
        financial_account_id__retirement=False  # <--- TUTAJ DODANO FILTR (zamień 'account' na nazwę Twojego klucza obcego)
    ).annotate(
        # Przypisujemy kurs do każdego wiersza (jeśli brak, domyślnie 1.0)
        current_exchange_rate=Coalesce(
            Subquery(exchange_rate_subquery, output_field=DecimalField(max_digits=10, decimal_places=2)),
            Value(1.0), # <--- POPRAWKA: użyto Value() dla bezpieczeństwa typowania w ORM
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).aggregate(
        total_value=Sum(
            ExpressionWrapper(
                (
                    Cast(F('buy_quantity'), output_field=DecimalField(max_digits=10, decimal_places=2)) * F('buy_price') 
                    - F('buy_commission')
                ) * F('current_exchange_rate'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
    )

    investments_total = result['total_value'] or 0

    # BONUS: Jeśli "oszczędności normalne" nie powinny zawierać gotówki z kont emerytalnych,
    # to tutaj również powinieneś odfiltrować retirement=False
    cash_total = FinancialAccount.objects.filter(
        retirement=False  # <--- Opcjonalnie: filtrujemy też gotówkę
    ).aggregate(Sum("cash"))["cash__sum"] or 0
    
    crypto_total = Crypto.objects.aggregate(Sum("value"))["value__sum"] or 0

    return cash_total + crypto_total + investments_total


def get_retirement_savings():
    # 1. Podzapytanie pobierające najnowszy kurs dla danej waluty inwestycji
        exchange_rate_subquery = ExchangeRate.objects.filter(
            currency=OuterRef('exchange_rate_id__currency')
        ).order_by('-updated_at').values('rate')[:1]
    
        # 2. Wyciągnięcie kursu i przemnożenie go wewnątrz zapytania agregującego
        result = Investment.objects.filter(
            active=True,
            financial_account_id__retirement=True  # <--- TUTAJ DODANO FILTR (zamień 'account' na nazwę Twojego klucza obcego)
        ).annotate(
            # Przypisujemy kurs do każdego wiersza (jeśli brak, domyślnie 1.0)
            current_exchange_rate=Coalesce(
                Subquery(exchange_rate_subquery, output_field=DecimalField(max_digits=10, decimal_places=2)),
                Value(1.0), # <--- POPRAWKA: użyto Value() dla bezpieczeństwa typowania w ORM
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).aggregate(
            total_value=Sum(
                ExpressionWrapper(
                    (
                        Cast(F('buy_quantity'), output_field=DecimalField(max_digits=10, decimal_places=2)) * F('buy_price') 
                        - F('buy_commission')
                    ) * F('current_exchange_rate'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        )
    
        investments_total = result['total_value'] or 0
    
        # BONUS: Jeśli "oszczędności normalne" nie powinny zawierać gotówki z kont emerytalnych,
        # to tutaj również powinieneś odfiltrować retirement=False
        cash_total = FinancialAccount.objects.filter(
            retirement=True  # <--- Opcjonalnie: filtrujemy też gotówkę
        ).aggregate(Sum("cash"))["cash__sum"] or 0
    
        return cash_total + investments_total


def get_cash_total(retirement=False):
    return FinancialAccount.objects.filter(
        retirement=retirement
    ).aggregate(Sum("cash"))["cash__sum"] or 0


def path_to_million(current_savings):
    percent = current_savings / 1000000 * 100
    to_save = 1000000 - current_savings
    if to_save < 0:
        to_save = 0
    if percent > 100:
        percent = 100
    return round(percent, 2), round(to_save, 2)


def get_passive_income():
    one_year_ago = timezone.now() - timedelta(days=365)

    passive_income = Income.objects.filter(
        category__name="Kapitał",
        date__gte=one_year_ago
    ).aggregate(
        total_value=Sum('value')
    )['total_value'] or Decimal('0.00')

    return round(passive_income / 12, 2)


def get_asset_allocation(retirement=False):
    investments = Investment.objects.filter(
        active=True,
        financial_account_id__retirement=retirement
    )

    allocation_qs = investments.values(
        category_name=F('category_id__name')
    ).annotate(
        total_value=Sum(
            ExpressionWrapper(
                Cast(F('buy_quantity'), output_field=DecimalField(max_digits=12, decimal_places=2)) 
                * Coalesce(F('current_price'), F('buy_price')) 
                * Coalesce(F('exchange_rate_id__rate'), Value(1.0), output_field=DecimalField(max_digits=10, decimal_places=2)),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        )
    )

    # 1. Zbieramy surowe wartości do słownika zamiast od razu liczyć procenty
    raw_data = {}
    
    for item in allocation_qs:
        cat_name = item['category_name'] or "Bez kategorii"
        val = item['total_value'] or Decimal('0.00')
        # Dodajemy do istniejącej kategorii (na wypadek gdyby zapytanie zwróciło duplikaty)
        raw_data[cat_name] = raw_data.get(cat_name, Decimal('0.00')) + val

    # 2. Dodajemy gotówkę bezpośrednio do naszego słownika surowych wartości
    cash_total = FinancialAccount.objects.filter(
        retirement=retirement
    ).aggregate(Sum("cash"))["cash__sum"] or Decimal('0.00')

    if cash_total > Decimal('0.00'):
        raw_data["Gotówka"] = raw_data.get("Gotówka", Decimal('0.00')) + cash_total

    # 3. Obliczamy całkowitą wartość całego portfela (inwestycje + gotówka)
    total_portfolio_value = sum(raw_data.values())

    labels = []
    data = []

    # 4. Dopiero teraz liczymy procenty dla wszystkich kategorii za jednym razem
    for cat_name, val in raw_data.items():
        if total_portfolio_value > 0:
            percentage = (val / total_portfolio_value) * Decimal('100.0')
        else:
            percentage = Decimal('0.00')
            
        labels.append(cat_name)
        data.append(round(float(percentage), 2))

    return {
        'labels': labels,
        'data': data
    }


def get_capital_projection(current_capital, yearly_contribution=24000.0, annual_return=0.07):
    """
    Oblicza projekcję wzrostu kapitału od obecnego roku do 2050 roku.
    
    :param current_capital: Aktualny stan portfela (np. z funkcji get_savings())
    :param yearly_contribution: Roczna kwota, którą zamierzasz dokładać do portfela (np. 24 000 PLN = 2 000 PLN/m-c)
    :param annual_return: Szacunkowa roczna stopa zwrotu (domyślnie 7% = 0.07)
    :return: Słownik z dwiema listami: etykietami (lata) i danymi (kapitał)
    """
    # Pobieramy aktualny rok (w Twoim przypadku 2026)
    current_year = timezone.now().year
    end_year = 2050
    
    labels = []
    data = []
    
    # Rzutujemy kapitał początkowy na typ float, aby ułatwić obliczenia
    capital = float(current_capital)
    
    for year in range(current_year, end_year + 1):
        labels.append(str(year))
        
        # Dodajemy zaokrąglony kapitał do listy (bez groszy, żeby wykres był czytelniejszy)
        data.append(int(round(capital, 0)))
        
        # Obliczamy kapitał na kolejny rok: 
        # Obecny kapitał * (1 + stopa zwrotu) + nowe środki wpłacone w ciągu roku
        capital = (capital * (1.0 + annual_return)) + float(yearly_contribution)
        
    return {
        'labels': labels,
        'data': data
    }


def get_invested_capital(total, cash):
    return round((total - cash) / total * 100, 2)


def get_projected_pension_zus():
    projected_pension_zus = constance.config.PROJECTED_PENSION_ZUS - (constance.config.PROJECTED_PENSION_ZUS - 2500) * 0.12 - constance.config.PROJECTED_PENSION_ZUS * 0.09 # emerytura brutto - 12% podatek - 9% składka zdrowotna (przy założeniu, że nie ma innych dochodów)
    return round(Decimal(projected_pension_zus), 2)


def index(request):
    total_savings = round(get_total_wealth(), 2)
    normal_savings = round(get_savings(), 2)
    cash_total = round(get_cash_total(), 2)
    invested_capital = round(get_invested_capital(normal_savings, cash_total), 2)
    perc_of_million, diff_to_million = path_to_million(total_savings)
    passive_income = get_passive_income()
    allocation = get_asset_allocation()
    capital_projection = get_capital_projection(total_savings, constance.config.CAPITAL_PROJECTION_ANNUAL_CONTRIBUTION, constance.config.CAPITAL_PROJECTION_ANNUAL_RETURN)

    return render(request, "dashboard/dashboard_finances.html", {
        'total_savings': total_savings, 
        'normal_savings': normal_savings,
        'invested_capital': invested_capital,
        'cash_amount': cash_total,
        'perc_of_million': perc_of_million,
        'diff_to_million': diff_to_million,
        'passive_income': passive_income,
        'asset_labels': json.dumps(allocation['labels']),
        'asset_data': json.dumps(allocation['data']),
        'projection_labels': json.dumps(capital_projection['labels']),
        'projection_data': json.dumps(capital_projection['data']),})


def retirement(request):
    total_retirement_savings = round(get_retirement_savings(), 2) + round(constance.config.RETIREMENT_CAPITAL_ZUS, 2)
    zus = round(constance.config.RETIREMENT_CAPITAL_ZUS, 2)
    private_pension_plan = round(get_retirement_savings(), 2)
    cash = round(get_cash_total(retirement=True), 2)
    invested_capital = round(get_invested_capital(total_retirement_savings, cash), 2)
    perc_of_million, diff_to_million = path_to_million(total_retirement_savings)
    passive_income = get_passive_income()
    allocation = get_asset_allocation(retirement=True)
    capital_projection = get_capital_projection(private_pension_plan, constance.config.CAPITAL_PROJECTION_ANNUAL_CONTRIBUTION, constance.config.CAPITAL_PROJECTION_ANNUAL_RETURN)
    projected_pension_zus = get_projected_pension_zus()
    projected_private_pension = private_pension_plan / constance.config.LIFE_EXPECTANCY
    projected_pension = round(Decimal(projected_pension_zus + projected_private_pension), 2)

    return render(request, "dashboard/dashboard_retirement.html", {
        'total_retirement_savings': total_retirement_savings,
        'zus': zus,
        'private_pension_plan': private_pension_plan,
        'invested_capital': invested_capital,
        'cash_amount': cash,
        'perc_of_million': perc_of_million,
        'diff_to_million': diff_to_million,
        'projected_pension': projected_pension,
        'asset_labels': json.dumps(allocation['labels']),
        'asset_data': json.dumps(allocation['data']),
        'projection_labels': json.dumps(capital_projection['labels']),
        'projection_data': json.dumps(capital_projection['data']),})


### Inwestycje ###


def list_of_investments(request):
    # 1. Przygotowujemy podzapytanie, które wyciągnie kurs dla waluty danej inwestycji.
    # Zakładam, że w modelu Investment masz pole 'currency'.
    # Bierzemy najnowszy kurs (order_by('-updated_at')).
    exchange_rate_subquery = ExchangeRate.objects.filter(
        currency=OuterRef('exchange_rate_id__currency')
    ).order_by('-updated_at').values('rate')[:1]

    # 2. Główny Queryset
    investments_list = Investment.objects.filter(active=True).annotate(
        # Pobieramy kurs waluty do każdej inwestycji (jeśli brak kursu, używamy 1.0)
        current_exchange_rate=Coalesce(
            Subquery(exchange_rate_subquery, output_field=DecimalField()),
            1.0, # wartość domyślna
            output_field=DecimalField()
        )
    ).annotate(
        # Obliczamy wartości bazowe
        raw_buy_total=F('buy_quantity') * F('buy_price') + F('buy_commission'),
        raw_sell_total=F('sell_quantity') * F('sell_price') - F('sell_commission'),
    ).annotate(
        # Przemnażamy przez kurs waluty
        buy_total=ExpressionWrapper(
            F('raw_buy_total') * F('current_exchange_rate') + F('buy_commission'),
            output_field=DecimalField()
        ),
        sell_total=ExpressionWrapper(
            F('raw_sell_total') * F('current_exchange_rate') + F('sell_commission'),
            output_field=DecimalField()
        ),
        # Obliczamy zysk na podstawie przeliczonych wartości
        current_profit=ExpressionWrapper(
            (F('current_price') * F('buy_quantity') * F('current_exchange_rate')) - 
            (F('raw_buy_total') * F('current_exchange_rate')),
            output_field=DecimalField()
        )
    ).annotate(
        profit=F('sell_total') - F('buy_total')
    ).order_by('-created_at')

    # Paginacja pozostaje bez zmian
    paginator = Paginator(investments_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, "investments/investment_list.html", context)


def retirement_investments(request):
    retirement_investments_list = Investment.objects.filter(retirement=True, active=True).annotate(
        buy_total=F('buy_quantity') * F('buy_price') + F('buy_commission'),
        sell_total=F('sell_quantity') * F('sell_price') - F('sell_commission'),
        current_profit=F('current_price') * F('buy_quantity') - F('buy_total')
    ).annotate(
        profit=F('sell_total') - F('buy_total')
    ).order_by('-created_at')

    paginator = Paginator(retirement_investments_list, 10)
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


### Incomes ###

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


### Gotówka ###

def cash(request):
    cash = FinancialAccount.objects.order_by("id")
    return render(request, "cash/index.html", {'cash': cash})


def edit_cash(request, pk):
    fin_account = get_object_or_404(FinancialAccount, pk=pk)

    if request.method == 'POST':
        form = FinancialAccountForm(request.POST, instance=fin_account)

        if form.is_valid():
            cash = form.save()
            return redirect('cash')
        else:
            add_errors_to_messages(request, form)
        
    else:
        form = FinancialAccountForm(instance=fin_account)

    return render(request, 'cash/edit.html', {'form': form})

