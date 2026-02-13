from django import forms
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import StoryRating, StoryReport


class RatingForm(forms.ModelForm):
    class Meta:
        model = StoryRating
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Optional comment..."}),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = StoryReport
        fields = ["reason", "message"]
        widgets = {
            "reason": forms.Select(),
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe the problem..."}),
        }

STATUS_CHOICES = [
    ("draft", "draft"),
    ("published", "published"),
    ("suspended", "suspended"),
]


class StoryForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 3}))
    status = forms.ChoiceField(choices=STATUS_CHOICES)
    start_page_id = forms.IntegerField(required=False)


class PageForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))
    is_ending = forms.BooleanField(required=False)
    ending_label = forms.CharField(required=False, max_length=120)


class ChoiceForm(forms.Form):
    page_id = forms.IntegerField(help_text="From which page?")
    text = forms.CharField(max_length=200)
    next_page_id = forms.IntegerField(help_text="To which page?")
