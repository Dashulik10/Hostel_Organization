from django import forms
from events.models import Event


class AddEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'start_date', 'description', 'number_of_places', 'number_of_suw_hours']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
            'start_date': forms.TextInput(attrs={'class': 'datetime-picker'})
        }