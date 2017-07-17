"""
Release: 0.1.5
Author: Golikov Ivan
Date: 10.07.2017
"""

import sys
from json import dumps, loads

from django.db import models
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords


class BaseHistoryTrackerModel(models.Model):
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class Building(BaseHistoryTrackerModel):
    number = models.CharField(verbose_name='номер', max_length=5)
    letter = models.CharField(verbose_name='литера', max_length=2, blank=True)

    def __str__(self):
        if self.letter:
            result = 'Корпус {} (литера {})'.format(self.number, self.letter)
        else:
            result = 'Корпус {}'.format(self.number)

        return result

    class Meta:
        verbose_name = 'корпус'
        verbose_name_plural = 'корпуса'

        unique_together = ('number', 'letter')


class Room(BaseHistoryTrackerModel):
    building = models.ForeignKey(Building,
                                 verbose_name='корпус',
                                 related_name='rooms')
    room = models.CharField(verbose_name='помещение', max_length=45)

    class Meta:
        verbose_name = "помещение"
        verbose_name_plural = "помещения"

        unique_together = ('building', 'room',)

    def __str__(self):
        return '{}, {}'.format(self.building, self.room)


class PBXRoom(BaseHistoryTrackerModel):
    room = models.OneToOneField(Room, verbose_name='помещение')

    class Meta:
        verbose_name = 'станционное помещение'
        verbose_name_plural = 'станционные помещения'


class Cabinet(BaseHistoryTrackerModel):
    room = models.ForeignKey(
        Room,
        verbose_name='расположение',
        on_delete=models.CASCADE,
    )
    number = models.CharField(verbose_name='номер', max_length=15, unique=True)

    def __str__(self):
        return 'Шкаф {}, {}'.format(self.number, self.room)

    class Meta:
        verbose_name = 'шкаф'
        verbose_name_plural = 'шкафы'


class Location(BaseHistoryTrackerModel):
    cabinet = models.OneToOneField(Cabinet,
                                   verbose_name='шкаф',
                                   blank=True,
                                   null=True,
                                   unique=True)
    room = models.OneToOneField(Room,
                                verbose_name='помещение',
                                blank=True,
                                null=True,
                                unique=True)

    def __str__(self):
        result = self.cabinet if self.cabinet else self.room

        return str(result)

    def clean(self):
        if self.cabinet and self.room:
            raise ValidationError('Нельзя выбирать и шкаф, и помещение одновременно')
        elif not self.cabinet and not self.room:
            raise ValidationError('Выберите либо шкаф, либо помещение')

    class Meta:
        verbose_name = 'расположение'
        verbose_name_plural = 'расположения'


class CrossPoint(BaseHistoryTrackerModel):
    location = models.ForeignKey(Location,
                                 verbose_name='расположение')
    source = models.ForeignKey('self',
                               verbose_name='откуда приходит',
                               related_name='destinations',
                               null=True,
                               blank=True,
                               )
    main_source = models.ForeignKey('self',
                                    verbose_name='порт-источник',
                                    related_name='childs',
                                    null=True,
                                    blank=True,
                                    editable=False,
                                    )
    level = models.PositiveSmallIntegerField(verbose_name='уровень',
                                             default=0,
                                             editable=False,
                                             )
    child_class = models.CharField(verbose_name='дочерний класс',
                                   max_length=100,
                                   blank=True,
                                   editable=False)

    def get_subclass(self):
        """
        Метод необходим для случаев, когда мы оперируем объектами класса
        CrossPoint, но необходимо знать подкласс объекта, например, для
        формирования строкового представления, специфичного для этого подкласса
        """

        return getattr(sys.modules[self.__module__], self.child_class)

    def get_parent(self):
        """
        Функция находит родительскую точку кросса для текущей точки,
        предполагая, что у всех точек родительской является порт АТС
        """
        result = None

        try:
            result = PBXPort.objects.get(pk=self.main_source_id)
        except:
            pass

        return result

    def clean(self):
        if self.pk and self.source:
            if self.source.pk == self.pk:
                raise ValidationError({'source': 'Нельзя составлять кольцевые связи'})

    def journal_str(self):
        return self.get_subclass().objects.get(crosspoint_ptr=self.pk).journal_str()

    def changes_str(self):
        return self.get_subclass().objects.get(crosspoint_ptr=self.pk).changes_str()

    def save(self, *args, **kwargs):
        self.child_class = self.__class__.__name__

        if self.child_class != 'PBXPort' and self.source is not None:
            self.main_source = self.source.main_source
            self.level = self.source.level + 1
        else:
            self.main_source = self

        super().save(*args, **kwargs)

    def __str__(self):
        return(str(self.get_subclass().objects.get(crosspoint_ptr=self.pk)))


class PBX(BaseHistoryTrackerModel):
    MANUFACTURERS = (
        ('asterisk', 'Asterisk'),
        ('avaya', 'Avaya'),
        ('m-200', 'М-200'),
        ('multicom', 'Мультиком'),
        ('panasonic', 'Panasonic'),
    )

    manufacturer = models.CharField(verbose_name='производитель',
                                    choices=MANUFACTURERS,
                                    max_length=10)
    model = models.CharField(verbose_name='модель', max_length=40)
    location = models.ForeignKey(Location,
                                 verbose_name='расположение')
    description = models.CharField(verbose_name='примечание',
                                   help_text='Подразделение, которое обслуживает АТС',
                                   max_length=30,
                                   blank=True)

    def __str__(self):
        result = '{} {}'.format(self.get_manufacturer_display(), self.model)

        if len(self.description) > 0:
            result += ' ({})'.format(self.description)

        return result

    class Meta:
        verbose_name = 'АТС'
        verbose_name_plural = 'АТС'


class PBXPort(CrossPoint):
    PORT_TYPES = (
        ('sip', 'SIP'),
        ('analog', 'Аналоговый'),
        ('pri', 'E1'),
    )
    pbx = models.ForeignKey(PBX, verbose_name='АТС')
    number = models.CharField(verbose_name='номер порта', max_length=20, blank=True)
    type = models.CharField(verbose_name='тип порта',
                            choices=PORT_TYPES,
                            default='analog',
                            max_length=10)
    subscriber_number = models.PositiveIntegerField(verbose_name='абонентский номер',
                                                    blank=True,
                                                    null=True,
                                                    unique=True)
    description = models.CharField(verbose_name='описание', max_length=150, blank=True)
    json_path = models.TextField(verbose_name='маршрут в формате JSON',
                                 blank=True,
                                 editable=False)

    def __str__(self):
        return '{}: {} (порт {}, {})'.format(self.pbx,
                                             self.subscriber_number,
                                             self.number,
                                             self.get_type_display())

    def save(self, *args, **kwargs):
        self.location = self.pbx.location

        if self.pk:
            from .utils import (
                CrosspathPointEncoder,
                CrosspathPointDecoder,
                get_crosspath,
            )

            last_self = PBXPort.objects.get(pk=self.pk)
            if last_self.subscriber_number != self.subscriber_number:

                if len(self.json_path) > 0:
                    cp = loads(self.json_path, cls=CrosspathPointDecoder)
                else:
                    cp = get_crosspath(self.pk)

                cp.journal_str = self.journal_str()
                self.json_path = dumps(cp, cls=CrosspathPointEncoder)

        super().save(*args, **kwargs)

    def journal_str(self):
        return '{}'.format(self.subscriber_number)

    def update_json(self, save_without_historical_record=False):
        from .utils import CrosspathPointEncoder, get_crosspath

        cp = get_crosspath(self.pk)
        self.json_path = dumps(cp, cls=CrosspathPointEncoder)

        if not save_without_historical_record:
            self.save()
        else:
            self.save_without_historical_record()

    class Meta:
        verbose_name = 'порт АТС'
        verbose_name_plural = 'порты АТС'
        ordering = ['subscriber_number']


class PunchBlockType(BaseHistoryTrackerModel):
    long_name = models.CharField(verbose_name='название',
                                 max_length=50,
                                 unique=True)
    short_name = models.CharField(verbose_name='сокращение',
                                  max_length=3,
                                  unique=True)
    regexp = models.CharField(verbose_name='регулярное выражение',
                              max_length=255)
    is_station_group = models.PositiveSmallIntegerField(
        verbose_name='группа станционного расположения',
        blank=True,
        null=True)
    number_group = models.PositiveSmallIntegerField(
        verbose_name='группа номера')
    location_group = models.PositiveSmallIntegerField(
        verbose_name='группа расположения',
        blank=True,
        null=True)

    class Meta:
        verbose_name = 'тип плинта'
        verbose_name_plural = 'типы плинтов'

    def __str__(self):
        return(self.long_name)


class PunchBlock(CrossPoint):
    PUNCHBLOCK_TYPES = (
        ('city', 'Гром-полоса'),
        ('extension', 'Распределение'),
        ('trunk', 'Магистраль'),
    )

    number = models.CharField(verbose_name='номер',
                              max_length=4,
                              blank=True,
                              null=True)
    type = models.ForeignKey(PunchBlockType,
                             verbose_name='тип')
    is_station = models.BooleanField(verbose_name='станционная (-ое)',
                                     blank=True)

    def journal_str(self):
        return self.__str__(add_phone=False)

    def changes_str(self):
        return str(self)

    def __str__(self, add_phone=True):
        result = self.type.short_name

        if self.is_station:
            result += 'с{}'.format(self.number)
        else:
            result += '{}/{}'.format(self.number, self.location.cabinet.number)

        parent_pbx_port = self.get_parent()

        if parent_pbx_port and add_phone:
            result += ' (тел. {})'.format(parent_pbx_port.subscriber_number)

        return result

    class Meta:
        verbose_name = 'плинт'
        verbose_name_plural = 'плинты'


class Phone(CrossPoint):
    def __str__(self):
        src = self.get_parent()

        result = ''
        if src and src.subscriber_number:
            result = str(src.subscriber_number)
        else:
            result = 'Телефон'

        return result

    def journal_str(self):
        res = '{}'
        subscribers = self.subscribers.all()

        if subscribers:
            res += ' ('
            subscribers_count = len(subscribers)
            for i, s in enumerate(subscribers):
                if i == subscribers_count - 1:
                    res += str(s)
                else:
                    res += '{}, '.format(s)
            res += ')'

        return res.format(self.location, subscribers)

    def changes_str(self):
        return 'тел. {} ({})'.format(self, self.journal_str())

    class Meta:
        verbose_name = 'телефон'
        verbose_name_plural = 'телефоны'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Subscriber(BaseHistoryTrackerModel):
    first_name = models.CharField(verbose_name='имя', max_length=30)
    last_name = models.CharField(verbose_name='фамилия', max_length=40)
    patronymic = models.CharField(verbose_name='отчество', max_length=35, blank=True)
    phones = models.ManyToManyField(Phone,
                                    verbose_name='телефоны',
                                    related_name='subscribers',
                                    blank=True)

    class Meta:
        verbose_name = 'абонент'
        verbose_name_plural = 'абоненты'

    def __str__(self):
        result = '{} {}.'.format(self.last_name,
                                 self.first_name[0],)

        if len(self.patronymic) > 0:
            result += '{}.'.format(self.patronymic[0])

        return result
