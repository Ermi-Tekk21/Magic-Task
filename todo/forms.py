from django import forms  # type: ignore[import]
from .models import Task


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ["title"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "task-input",
                    "placeholder": "What needs to be done?"
                }
            )
        }

    def clean_title(self):

        title = self.cleaned_data.get("title")

        if not title:

            raise forms.ValidationError("Title cannot be empty")

        if Task.objects.filter(title=title).exists():

            raise forms.ValidationError("This task already exists")

        return title