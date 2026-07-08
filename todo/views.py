from django.shortcuts import render, redirect  # type: ignore[import]
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.conf import settings
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import re
import json

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
                client = genai.Client(api_key=settings.GEMINI_API_KEY)

                prompt = f"""Break this goal into 5-8 clear, actionable tasks.
Return ONLY a numbered list, one task per line, no explanations.
Goal: {goal}"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
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


class PrioritizedTask(BaseModel):
    id: int
    title: str
    priority_level: str = Field(description="Must be one of: Critical, High, Medium, Low")
    reason: str


class PrioritizedTaskList(BaseModel):
    tasks: list[PrioritizedTask]


@login_required
def smart_priority(request):
    tasks = Task.objects.filter(user=request.user, completed=False)
    prioritized_tasks = []
    error = ""

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "rank" and tasks.exists():
            try:
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                
                tasks_list_str = "\n".join([f"- ID: {t.id}, Title: {t.title}" for t in tasks])
                
                prompt = f"""
You are a productivity expert assistant. Analyze the following list of tasks and prioritize them.
Assign one of the following priority levels to each task: 'Critical', 'High', 'Medium', or 'Low'.
Provide a short 1-sentence explanation/reason for each task's priority.
Order the output so the most important/urgent tasks are first.

Tasks:
{tasks_list_str}
"""
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=PrioritizedTaskList,
                    ),
                )
                
                # Parse JSON output
                data = json.loads(response.text)
                raw_tasks = data.get("tasks", [])
                
                priority_order = {"critical": 1, "high": 2, "medium": 3, "low": 4}
                
                for rt in raw_tasks:
                    p_level = rt.get("priority_level", "Medium").strip()
                    p_level_lower = p_level.lower()
                    
                    if p_level_lower not in priority_order:
                        p_level = "Medium"
                        p_level_lower = "medium"
                        
                    prioritized_tasks.append({
                        "id": rt.get("id"),
                        "title": rt.get("title"),
                        "priority_level": p_level,
                        "priority_class": f"priority-{p_level_lower}",
                        "reason": rt.get("reason", ""),
                        "sort_val": priority_order.get(p_level_lower, 3)
                    })
                
                # Sort prioritized_tasks based on sorting value
                prioritized_tasks.sort(key=lambda x: x["sort_val"])
                
            except Exception as e:
                error = f"AI error: {str(e)}"
                
        elif action == "apply":
            task_ids = request.POST.getlist("task_ids")
            for index, task_id in enumerate(task_ids):
                try:
                    task = Task.objects.get(id=int(task_id), user=request.user)
                    task.order = index
                    task.save()
                except (Task.DoesNotExist, ValueError):
                    continue
            return redirect('/')

    return render(request, "todo/smart_priority.html", {
        "tasks": tasks,
        "prioritized_tasks": prioritized_tasks,
        "error": error,
    })
