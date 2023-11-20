from django import forms
from .models import Mark


class MarkForm(forms.Form):
    mark = forms.ModelChoiceField(
        queryset=Mark.objects.all(),
        empty_label=None,
        label='Выберите марку машины',
    )
