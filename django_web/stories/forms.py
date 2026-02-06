from django import forms

STATUS_CHOICES = [
    ("draft", "draft"),
    ("published", "published"),
    ("suspended", "suspended"),
]


class StoryForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
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
