import datetime
import json
from math import floor

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Sum
from constance import config

from .models import Task, Activity, ActivityGoal
from .forms import TaskForm, ActivityForm
from.utils import calculate_streak



def add_errors_to_messages(request, form):
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"Błąd w polu {field}: {error}")


def index(request):
    return HttpResponse("To jest aplikacja life")

# Tasks
def tasks(request):
    tasks = Task.objects.all().order_by('priority', 'completion_date')
    paginator = Paginator(tasks, 20)  # Pokaż 20 zadań na stronie
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "tasks/index.html", {'page_obj': page_obj})


def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            task = form.save()
            return redirect('tasks')
        else:
            add_errors_to_messages(request, form)
    else:
        form = TaskForm(instance=task)

    context = {'form': form}
    return render(request, "tasks/edit_task.html", context)


def new_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save()
            return redirect('tasks')
        else:
            add_errors_to_messages(request, form)
    else:
        form = TaskForm()

    context = {'form': form}
    return render(request, "tasks/new_task.html", context)


def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        task.delete()
        return redirect('tasks')

    context = {'task': task}
    return render(request, "tasks/confirm_delete.html", context)


def task_details(request, pk):
    task = get_object_or_404(Task, pk=pk)
    context = {'task': task}
    return render(request, "tasks/task_details.html", context)


#Activities
def learning(request):
    activities = Activity.objects.all().order_by('-date', '-id')
    paginator = Paginator(activities, 20)  # Pokaż 20 aktywności na stronie
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "activities/index.html", {'page_obj': page_obj})


def edit_learning(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)

        if form.is_valid():
            a = form.save()
            return redirect('learning_dashboard')
        else:
            add_errors_to_messages(request, form)
    else:
        form = ActivityForm(instance=activity)

    context = {'form': form}
    return render(request, "activities/edit_activity.html", context)


def new_learning(request):
    if request.method == "POST":
        form = ActivityForm(request.POST)

        if form.is_valid():
            activity = form.save()
            return redirect('learning_dashboard')
        else:
            add_errors_to_messages(request, form)
    else:
        form = ActivityForm()

    context = {'form': form}
    return render(request, "activities/new_activity.html", context)


def delete_learning(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if request.method == "POST":
        activity.delete()
        return redirect('learning_dashboard')

    context = {'activity': activity}
    return render(request, "activities/confirm_delete.html", context)


def learning_details(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    context = {'activity': activity}
    return render(request, "activities/activity_details.html", context)


def calculate_learning_daily_7d_average(activity_name):
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=7)

    # Pobieramy wszystkie aktywności z ostatnich 7 dni dla danej kategorii
    recent_activities = Activity.objects.filter(
        name__name=activity_name,
        date__range=(seven_days_ago, today)
    )

    # Sumujemy czas trwania aktywności w minutach
    total_duration = recent_activities.aggregate(total=Sum('duration'))['total'] or 0

    # Obliczamy średnią dzienną (w minutach)
    average_daily_duration = total_duration / 7

    print(f"Average daily duration for {activity_name}: {average_daily_duration} minutes")  # Debugging output
    return average_daily_duration


def calculate_time_left_for_learning(end_goal, current_amount, daily_average):
    difference = end_goal - current_amount
    difference_in_days = round(difference / daily_average) if daily_average > 0 else float('inf')  # Unikamy dzielenia przez zero
    years = difference_in_days // 365
    months = (difference_in_days % 365) // 30
    days = (difference_in_days % 365) % 30
    return years, months, days


def get_time_string(years, months, days):
    time_parts = []
    if years > 0:
        time_parts.append(f"{years} {'rok' if years == 1 else 'lata' if 2 <= years <= 4 else 'lat'}")
    if months > 0:
        time_parts.append(f"{months} {'miesiąc' if months == 1 else 'miesiące' if 2 <= months <= 4 else 'miesięcy'}")
    if days > 0:
        time_parts.append(f"{days} {'dzień' if days == 1 else 'dni'}")

    return ', '.join(time_parts) if time_parts else "0 dni"


def learning_dashboard(request):
    today = datetime.date.today()

    # --------------------------------------------------------
    # 1. ORYGINALNA LOGIKA (Cele, Postępy, Zmienne bazowe)
    # --------------------------------------------------------
    progress_data = {
        'russian': 0,
        'english': 0,
        'reading': 0,
        'writing': 0,
        'criticism': 0,
    }

    descriptions = {
        'russian': '',
        'english': '',
        'reading': '',
        'writing': '',
        'criticism': '',
    }

    category_mapping = {
        'Język rosyjski': 'russian',
        'Język angielski': 'english',
        'Czytanie': 'reading',
        'Pisanie': 'writing',
        'Krytyka literacka': 'criticism'
    }

    active_goals = ActivityGoal.objects.filter(
        start_date__lte=today, 
        end_date__gte=today
    )

    for goal in active_goals:
        category_name = goal.activity.name  
     
        if category_name in category_mapping:
            dict_key = category_mapping[category_name]
            descriptions[dict_key] = goal.description
            
            activities_sum = Activity.objects.filter(
                name=goal.activity,
                date__range=(goal.start_date, goal.end_date)
            ).aggregate(total=Sum('duration'))['total'] or 0
            
            if dict_key in ['reading', 'writing', 'criticism']:
                activities_sum = floor(activities_sum / 60)
                progress_data[dict_key] = activities_sum
            else:
                if goal.goal_duration > 0:
                    percent = int((activities_sum / goal.goal_duration) * 100)
                    progress_data[dict_key] = min(percent, 100)

    recent_activities = Activity.objects.select_related('name').order_by('-date', '-id')[:5]

    streak = calculate_streak()
    streak_active = streak > 0
    print(f"Streak: {streak}, Active: {streak_active}") 

    time_left_english = calculate_time_left_for_learning(
        end_goal=ActivityGoal.objects.filter(activity__name='Język angielski').first().goal_duration if ActivityGoal.objects.filter(activity__name='Język angielski').exists() else 0,
        current_amount=Activity.objects.filter(name__name='Język angielski').aggregate(total=Sum('duration'))['total'] or 0,
        daily_average=calculate_learning_daily_7d_average('Język angielski')
    )
    print(f"Time left for English: {time_left_english}")
    time_left_english_string = get_time_string(*time_left_english)

    time_left_russian = calculate_time_left_for_learning(
        end_goal=ActivityGoal.objects.filter(activity__name='Język rosyjski').first().goal_duration if ActivityGoal.objects.filter(activity__name='Język rosyjski').exists() else 0,
        current_amount=Activity.objects.filter(name__name='Język rosyjski').aggregate(total=Sum('duration'))['total'] or 0,
        daily_average=calculate_learning_daily_7d_average('Język rosyjski')
    )
    time_left_russian_string = get_time_string(*time_left_russian)

    # --------------------------------------------------------
    # 2. NOWA LOGIKA: DANE DO WYKRESU CHART.JS
    # --------------------------------------------------------
    
    # a) Wygenerowanie ostatnich 30 dni chronologicznie (od najstarszego do dziś)
    last_30_days = [today - datetime.timedelta(days=i) for i in range(29, -1, -1)]
    chart_labels = [day.strftime("%d.%m") for day in last_30_days]
    
    # Słownik do szybkiego wyszukiwania indeksu dnia w liście
    date_to_index = {day: index for index, day in enumerate(last_30_days)}
    
    # Lista przedmiotów do uwzględnienia na wykresie
    chart_subjects = list(category_mapping.keys())
    
    # Przygotowanie pustej struktury danych: każdy przedmiot ma listę 30 zer
    chart_data_by_subject = {subject: [0] * 30 for subject in chart_subjects}
    
    # b) Pobranie pogrupowanych danych z bazy (tylko 1 zapytanie!)
    # Pobieramy datę, nazwę kategorii i sumę czasu, a następnie filtrujemy z ostatnich 30 dni
    start_date_chart = last_30_days[0]
    grouped_activities = Activity.objects.filter(
        date__gte=start_date_chart,
        date__lte=today,
        name__name__in=chart_subjects
    ).values('date', 'name__name').annotate(total_duration=Sum('duration'))
    
    # c) Wypełnienie struktury pobranymi danymi
    for entry in grouped_activities:
        activity_date = entry['date']
        subject_name = entry['name__name']
        total_time = entry['total_duration'] or 0
        
        # Jeśli data mieści się w naszym zakresie 30 dni i kategoria nas interesuje
        if activity_date in date_to_index and subject_name in chart_data_by_subject:
            day_index = date_to_index[activity_date]
            # Przypisujemy czas nauki (w minutach) do odpowiedniego indeksu (dnia) dla danej kategorii
            chart_data_by_subject[subject_name][day_index] += total_time
            
    # d) Kolory dla poszczególnych przedmiotów (zmieniaj dowolnie format: HEX lub RGBA)
    subject_colors = {
        'Język angielski':   {'bg': 'rgba(53, 162, 235, 0.75)', 'border': 'rgba(53, 162, 235, 1)'},   # Wyrazisty błękit
        'Język rosyjski':    {'bg': 'rgba(255, 127, 80, 0.75)',  'border': 'rgba(255, 127, 80, 1)'},   # Ciepły koralowy / pomarańczowy (zamiast gryzącego czerwonego)
        'Czytanie':          {'bg': 'rgba(75, 192, 122, 0.75)',  'border': 'rgba(75, 192, 122, 1)'},   # Miętowa zieleń (świetnie kontrastuje z błękitem i pomarańczem)
        'Pisanie':           {'bg': 'rgba(255, 205, 86, 0.75)',  'border': 'rgba(255, 205, 86, 1)'},   # Stonowany złoty żółty (czytelny, nie oślepia)
        'Krytyka literacka': {'bg': 'rgba(168, 85, 247, 0.75)',  'border': 'rgba(168, 85, 247, 1)'}   # Głęboki fiolet / purpura
    }
    
    # e) Formatowanie datasets dla Chart.js
    chart_datasets = []
    for subject in chart_subjects:
        chart_datasets.append({
            "label": subject,
            "data": chart_data_by_subject[subject],
            "backgroundColor": subject_colors[subject]['bg'],
            "borderColor": subject_colors[subject]['border'],
            "borderWidth": 1
        })

    # --------------------------------------------------------
    # 3. ZWRACANIE KONTEKSTU DO SZABLONU
    # --------------------------------------------------------
    context = {
        'progress_russian': progress_data['russian'],
        'progress_english': progress_data['english'],
        'progress_reading': progress_data['reading'],
        'progress_writing': progress_data['writing'],
        'progress_criticism': progress_data['criticism'],
        'description_russian': descriptions['russian'],
        'description_english': descriptions['english'],
        'description_reading': descriptions['reading'],
        'description_writing': descriptions['writing'],
        'description_criticism': descriptions['criticism'],
        'streak': streak,
        'streak_active': streak_active,
        'recent_activities': recent_activities,
        'current_daily_word': config.CURRENT_DAILY_WORD.title() if getattr(config, 'CURRENT_DAILY_WORD', None) else '',
        'current_daily_word_description': getattr(config, 'CURRENT_DAILY_WORD_DESCRIPTION', ''),
        'time_left_english_string': time_left_english_string,
        'time_left_russian_string': time_left_russian_string,
        
        # Nowe zmienne przekazywane do wykresu JS
        'chart_labels': json.dumps(chart_labels),
        'chart_datasets': json.dumps(chart_datasets),
    }
    
    return render(request, 'activities/dashboard.html', context)
