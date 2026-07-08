from django.shortcuts import render, redirect  # type: ignore[import]
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.conf import settings
import google.generativeai as genai
import re

def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(
        request,
        "registration/signup.html",
        {"form": form}
    )

def task_list(request):
    if not request.user.is_authenticated:
        return render(request, "todo/landing.html")

    if request.method == "POST":

        form = TaskForm(request.POST)

        if form.is_valid():

            task = form.save(commit=False)

            task.user = request.user

            task.save()

            return redirect("/")

    else:

        form = TaskForm()

    tasks = Task.objects.filter(
        user=request.user
    )

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

@login_required
def ai_breakdown(request):
    generated_tasks = []
    goal = ""
    error = ""

    if request.method == "POST":
        goal = request.POST.get("goal", "").strip()

        if goal:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel("gemini-2.5-flash")

                prompt = f"""Break this goal into 5-8 clear, actionable tasks.
Return ONLY a numbered list, one task per line, no explanations.
Goal: {goal}"""

                response = model.generate_content(prompt)
                lines = response.text.strip().split('\n')

                for line in lines:
                    line = line.strip()
                    if line:
                        # Remove leading numbers like "1. " or "1) "
                        clean = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
                        if clean:
                            generated_tasks.append(clean)

            except Exception as e:
                error = f"AI error: {str(e)}"

        # If user clicked "Save All Tasks"
        if "save_tasks" in request.POST:
            task_titles = request.POST.getlist("task_titles")
            for title in task_titles:
                title = title.strip()
                if title:
                    Task.objects.create(user=request.user, title=title)
            return redirect('/')

    return render(request, "todo/ai_breakdown.html", {
        "generated_tasks": generated_tasks,
        "goal": goal,
        "error": error,
    })
