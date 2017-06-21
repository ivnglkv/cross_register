from django.forms import ModelForm, ModelChoiceField
from django.db.models import Q

from .fields import CrosspointField
from .models import (
    Location,
    PBXPort,
    Phone,
    PunchBlock,
)


class PunchBlockForm(ModelForm):
    location = ModelChoiceField(label='Расположение',
                                queryset=Location.objects.filter(
                                    Q(cabinet__isnull=False) |
                                    Q(room__pbxroom__isnull=False)),
                                )
    destination = CrosspointField(label='Откуда приходит',
                                  required=False,
                                  )

    class Meta:
        model = PunchBlock
        fields = ['type', 'location', 'destination', 'number', 'is_station']


class PhoneForm(ModelForm):
    location = ModelChoiceField(label='Расположение',
                                queryset=Location.objects.filter(
                                    Q(room__isnull=False))
                                )
    destination = CrosspointField(label='Откуда приходит',
                                  required=False,
                                  )

    class Meta:
        model = Phone
        fields = ['location', 'destination']


class PBXPortForm(ModelForm):
    location = ModelChoiceField(label='Расположение',
                                queryset=Location.objects.filter(
                                    Q(cabinet__isnull=False) |
                                    Q(room__pbxroom__isnull=False)),
                                )

    class Meta:
        model = PBXPort
        fields = [
            'location',
            'pbx',
            'number',
            'type',
            'subscriber_number',
            'description',
        ]
