from django.shortcuts import render, get_object_or_404, redirect
from .models import Task

def task_list(request):
    if request.method == "POST":

        title = request.POST.get("title")

        if title:

            Task.objects.create(
                title=title
            )
            return redirect("/")
        
    tasks = Task.objects.all()

    return render(
        request,
        "todo/task_list.html",
        {"tasks": tasks}
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