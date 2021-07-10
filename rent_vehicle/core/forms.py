from django import forms
from django.forms import ValidationError
from core.models import Rent, Vehicle
from core.core import rent_vehicle, StatusError, CollisionError


class CreateRentForm(forms.ModelForm):
    class Meta:
        model = Rent
        fields = ['vehicle', 'started_at', 'finished_at']

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['vehicle'].queryset = (Vehicle.objects
                                           .filter(status=Vehicle.STATUS_AVAILABLE)
                                           .order_by('kind'))

    def clean(self):
        try:
            vehicle = self.cleaned_data['vehicle']
            started_at = self.cleaned_data['started_at']
            finished_at = self.cleaned_data['finished_at']
        except KeyError:
            return

        try:
            rent_vehicle(vehicle, self.user, started_at, finished_at)
        except StatusError:
            raise ValidationError("Selected vehicle is not available")
        except CollisionError:
            raise ValidationError("The vehicle is not available in selected time")
        except ValueError as error:
            raise ValidationError(str(error))

    def save(self, commit=True):
        pass
