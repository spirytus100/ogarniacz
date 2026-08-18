import datetime

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
def activities(request):
    activities = Activity.objects.all().order_by('-date', '-id')
    paginator = Paginator(activities, 20)  # Pokaż 20 aktywności na stronie
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "activities/index.html", {'page_obj': page_obj})


def edit_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if request.method == "POST":
        form = ActivityForm(request.POST, instance=activity)

        if form.is_valid():
            a = form.save()
            return redirect('activities')
        else:
            add_errors_to_messages(request, form)
    else:
        form = ActivityForm(instance=activity)

    context = {'form': form}
    return render(request, "activities/edit_activity.html", context)


def new_activity(request):
    if request.method == "POST":
        form = ActivityForm(request.POST)

        if form.is_valid():
            activity = form.save()
            return redirect('activities')
        else:
            add_errors_to_messages(request, form)
    else:
        form = ActivityForm()

    context = {'form': form}
    return render(request, "activities/new_activity.html", context)


def delete_activity(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if request.method == "POST":
        activity.delete()
        return redirect('activities')

    context = {'activity': activity}
    return render(request, "activities/confirm_delete.html", context)


def activity_details(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    context = {'activity': activity}
    return render(request, "activities/activity_details.html", context)


def activity_dashboard(request):
    today = datetime.date.today()

    # 1. Inicjalizacja domyślnych wartości postępu na 0%
    progress_data = {
        'russian': 0,
        'reading': 0,
        'writing': 0,
        'criticism': 0,
    }

    descriptions = {
        'russian': '',
        'reading': '',
        'writing': '',
        'criticism': '',
    }

    # Mapowanie nazw kategorii z bazy na klucze w słowniku
    # Dopasuj stringi do tego, jak dokładnie nazywają się w bazie!
    category_mapping = {
        'Język rosyjski': 'russian',
        'Czytanie': 'reading',
        'Pisanie': 'writing',
        'Krytyka literacka': 'criticism'
    }

    # 2. Pobieramy tylko aktualne cele (gdzie dzisiaj mieści się w dacie celu)
    active_goals = ActivityGoal.objects.filter(
        start_date__lte=today, 
        end_date__gte=today
    )

    # 3. Obliczanie procentów dla każdej kategorii
    for goal in active_goals:
        # Zakładam, że kategoria ma pole tekstowe, które przechowuje nazwę (np. kategoria.name)
        category_name = goal.activity.name  
     
        if category_name in category_mapping:
            dict_key = category_mapping[category_name]

            descriptions[dict_key] = goal.description
            
            # Sumujemy czas trwania aktywności z danego okresu
            # Uwaga: w Twoim modelu Activity klucz obcy nazywa się 'name' (zamiast np. category)
            activities_sum = Activity.objects.filter(
                name=goal.activity,
                date__range=(goal.start_date, goal.end_date)
            ).aggregate(total=Sum('duration'))['total'] or 0
            
            # Wyliczamy procent (unikamy dzielenia przez zero)
            if goal.goal_duration > 0:
                percent = int((activities_sum / goal.goal_duration) * 100)
                progress_data[dict_key] = min(percent, 100)  # Max 100%

    # 4. Pobieranie ostatnich aktywności do Timeline'u (np. najnowsze 5)
    recent_activities = Activity.objects.select_related('name').order_by('-date', '-id')[:5]

    # 5. Obliczanie streaku
    streak = calculate_streak()  # Używamy funkcji z utils.py do obliczenia streaku
    streak_active = streak > 0  # True jeśli streak jest większy niż 0, False w przeciwnym razie
    print(f"Streak: {streak}, Active: {streak_active}")  # Debugging output


    # Przekazanie kontekstu do szablonu
    context = {
        'progress_russian': progress_data['russian'],
        'progress_reading': progress_data['reading'],
        'progress_writing': progress_data['writing'],
        'progress_criticism': progress_data['criticism'],
        'description_russian': descriptions['russian'],
        'description_reading': descriptions['reading'],
        'description_writing': descriptions['writing'],
        'description_criticism': descriptions['criticism'],
        'streak': streak,
        'streak_active': streak_active,
        'recent_activities': recent_activities,
        'current_daily_word': config.CURRENT_DAILY_WORD.title() if config.CURRENT_DAILY_WORD else '',
        'current_daily_word_description': config.CURRENT_DAILY_WORD_DESCRIPTION,
    }
    
    return render(request, 'activities/dashboard.html', context)
