from django.forms import ModelForm, ModelChoiceField
from django.db.models import Q
from .models import (
    CrossPoint,
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

    class Meta:
        model = PunchBlock
        fields = ['location', 'destination', 'number', 'type', 'is_station']


class PhoneForm(ModelForm):
    location = ModelChoiceField(label='Расположение',
                                queryset=Location.objects.filter(
                                    Q(room__isnull=False))
                                )
    destination = ModelChoiceField(label='Откуда приходит',
                                   queryset=CrossPoint.objects.filter(
                                        Q(punchblock__type='extension'))
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
