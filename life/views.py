from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Task
from .forms import TaskForm



def add_errors_to_messages(request, form):
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"Błąd w polu {field}: {error}")


def index(request):
    return HttpResponse("To jest aplikacja life")


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