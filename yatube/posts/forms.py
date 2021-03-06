# posts/forms.py
from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        widgets = {
            "group": forms.Select(attrs={"class": "custom-select md-form"}),
        }

    def clean_text(self):

        data = self.cleaned_data["text"]
        if data == " ":
            raise forms.ValidationError("Необходимо заполнить поле.")
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)

    def clean_text(self):

        data = self.cleaned_data["text"]
        if data == " ":
            raise forms.ValidationError("Комментарий пуст.")
        return data
