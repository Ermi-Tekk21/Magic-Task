from django.shortcuts import render, redirect  # type: ignore[import]
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import login_required

@login_required
def task_list(request):

    if request.method == "POST":

        form = TaskForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("/")

    else:

        form = TaskForm()

    tasks = Task.objects.all()

    return render(
        request,
        "todo/task_list.html",
        {
            "tasks": tasks,
            "form": form
        }
    )
    
def complete_task(request, id):

    task = Task.objects.get(id=id)

    task.completed = True

    task.save()

    return redirect("/")

def delete_task(request, id):

    task = Task.objects.get(id=id)

    task.delete()

    return redirect("/")

def toggle_task(request, id):

    task = Task.objects.get(id=id)

    task.completed = not task.completed

    task.save()

    return redirect('/')