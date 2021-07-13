from django import forms
from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group")
        labels = {"text": "текст", "group'": "группа"}
        help_texts = {
            "text": ("Напишете любой текст без мата"),
            "group": ("А тут можно и с матом")
        }

    def clean_text(self):
        data = self.cleaned_data["text"]
        if not data:
            raise forms.ValidationError("Введите текст")
        return data
