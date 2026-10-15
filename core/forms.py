
from django import forms
from .models import Taxi


class TaxiForm(forms.ModelForm):
    class Meta:
        model = Taxi
        fields = [
            'number',
            'type',
            'source',
            'destination',
            'price',
            'availability',
            'driver',
        ]

        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. GJ01AB1234',
            }),
            'type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Sedan, SUV, Hatchback',
            }),
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter starting location',
            }),
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter destination',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter fare',
                'min': '0.01',
                'step': '0.01',
            }),
            'availability': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'driver': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

    def clean_number(self):
        number = self.cleaned_data['number'].strip()
        if Taxi.objects.filter(number__iexact=number).exists():
            raise forms.ValidationError(
                'A taxi with this number already exists.'
            )
        return number




def clean_number(self):
    number = self.cleaned_data['number'].strip()

    existing_taxis = Taxi.objects.filter(number__iexact=number)

    if self.instance and self.instance.pk:
        existing_taxis = existing_taxis.exclude(pk=self.instance.pk)

    if existing_taxis.exists():
        raise forms.ValidationError(
            'A taxi with this number already exists.'
        )

    return number
