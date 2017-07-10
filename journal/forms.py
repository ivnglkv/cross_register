from django.forms import ModelForm, ModelChoiceField
from django.db.models import Q

from .fields import CrosspointField
from .models import (
    Location,
    PBX,
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
    source = CrosspointField(label='Откуда приходит',
                             required=False,
                             )

    class Meta:
        model = PunchBlock
        fields = ['type', 'location', 'source', 'number', 'is_station']


class PhoneForm(ModelForm):
    location = ModelChoiceField(label='Расположение',
                                queryset=Location.objects.filter(
                                    Q(room__isnull=False))
                                )
    source = CrosspointField(label='Откуда приходит',
                             required=False,
                             )

    class Meta:
        model = Phone
        fields = ['location', 'source']


class PBXPortForm(ModelForm):
    class Meta:
        model = PBXPort
        fields = [
            'pbx',
            'number',
            'type',
            'subscriber_number',
            'description',
        ]


class PBXForm(ModelForm):
    location = ModelChoiceField(label='Расположение',
                                queryset=Location.objects.filter(
                                    Q(cabinet__isnull=False) |
                                    Q(room__pbxroom__isnull=False)),
                                )

    class Meta:
        model = PBX
        fields = [
            'manufacturer',
            'model',
            'location',
            'description',
        ]
