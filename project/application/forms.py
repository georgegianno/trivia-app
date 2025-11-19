from django import forms
from django.conf import settings
from .models import Category

from django import forms
from .models import Category, Question

# A simple form to filter questions. Nothing great here.
class FilteringForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='Any category',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    difficulty = forms.ChoiceField(
        choices=[('', 'Any difficulty')] + Question.DIFFICULTY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    type = forms.ChoiceField(
        label='Question Type',
        choices=[('', 'Any type')] + Question.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    text = forms.CharField(
        label='Search Term',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search in question text'})
    )

    # Optional, just in case.
    def __init__(self, *arg, **kwarg):
        super().__init__(*arg, **kwarg)
        values = Question.objects.values('difficulty', 'type', 'category')
        values_map = {'diff': set(), 'cat': set(), 'type': set()}
        diff_choices = list(self.fields['difficulty'].choices)
        cat_choices = list(self.fields['category'].choices)
        type_choices = list(self.fields['type'].choices)
        for item in values:
            values_map['diff'].add(item['difficulty'])
            values_map['type'].add(item['type'])
            values_map['cat'].add(item['category'])
        self.fields['category'].choices = [cat_choices[0]] + [c for c in cat_choices if c[0] in values_map['cat']]
        self.fields['difficulty'].choices = [diff_choices[0]]+[c for c in diff_choices if c[0] in values_map['diff']]
        self.fields['type'].choices = [type_choices[0]]+[c for c in type_choices if c[0] in values_map['type']]