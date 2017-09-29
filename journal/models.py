"""
Release: 0.2.2
Author: Golikov Ivan
Date: 29.09.2017
"""

from json import dumps, loads

from django.db import models
from django.db.models import F, Q
from django.core.exceptions import ValidationError
from polymorphic.models import PolymorphicModel
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


class CrossPoint(BaseHistoryTrackerModel, PolymorphicModel):
    """Общее описание точки кросса

    От CrossPoint должен наследоваться любой класс, представляющий пункт маршрута
    линии от АТС до КРТ и розетки

    Args:
        location (obj): расположение точки. Подклассы CrossPoint могут накладывать ограничения на
            возможные расположения точки
        source (obj, optional): точка кросса, с которой приходит линия
        main_source (obj, optional): точка кросса, являющаяся "головной" для текущей. В большинстве
            случаев это будет PBXPort
        level(int): уровень расположения относительно main_source
    """
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

    def get_parent(self):
        """
        Функция находит родительскую точку кросса для текущей точки,
        предполагая, что у всех точек родительской является порт АТС
        """
        main_source = self.main_source

        return main_source if isinstance(main_source, PBXPort) else None

    def clean(self):
        if self.pk and self.source:
            if self.source.pk == self.pk:
                raise ValidationError({'source': 'Нельзя составлять кольцевые связи'})

    def save(self, *args, **kwargs):
        """Выполняется обновление полей level и main_source в объекте и его точках назначения

        В обработчике сигнала post_save выставляется значение поля main_source = self,
        если объект был только что создан без источника
        """
        try:
            old_self = CrossPoint.objects.get(pk=self.pk)
        except:
            old_self = None

        new_main_source = self.main_source
        new_level = self.level
        new_level_change = 0

        if not self.source and self.main_source != self:
            new_main_source = self
            new_level = 0
            new_level_change = new_level - self.level
        elif self.source and self.main_source != self.source.main_source:
            new_main_source = self.source.main_source
            new_level = self.source.level + 1
            new_level_change = new_level - self.level
        elif (old_self and
                not isinstance(self, PBXPort) and
                old_self.main_source == self.source.main_source and
                old_self.source != self.source):
            new_main_source = self.main_source
            new_level = self.source.level + 1
            new_level_change = new_level - self.level

        if not self.pk and new_main_source == self:
            # При создании main_source будет выставлен в post_save
            pass
        else:
            self.main_source = new_main_source
        self.level = new_level

        if old_self:
            old_self.get_all_point_childs().update(main_source=new_main_source,
                                                   level=F('level') + new_level_change)

        super().save(*args, **kwargs)

    def get_all_point_childs(self, include_self=False):
        """Рекурсивное получение всех точек, следующих за этой

        Параметры
        ---------
        include_self: bool
            Определяет, будет ли включена текущая точка в результирующий QuerySet

        Возвращаемое значение
        ---------------------
        QuerySet
            Запрос на получение всех точек, следующих за этой
        """
        res_qs = CrossPoint.objects.filter(pk=self.pk)

        if not include_self:
            res_qs = res_qs.exclude(pk=self.pk)

        direct_childs_qs = self.destinations.all()
        for child in direct_childs_qs:
            res_qs |= child.get_all_point_childs(include_self=True)

        return res_qs


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
                              max_length=7,
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

        if add_phone:
            parent_port = self.main_source

            if isinstance(parent_port, PBXPort):
                result += ' (тел. {})'.format(parent_port.subscriber_number)

        return result

    def clean(self):
        # Так как нельзя привязать unique_together к полю
        # в неабстрактной родительской модели, нужно
        # провести валидацию, эмулирующую
        # unique_together = ('type', 'number', 'location')
        qs = PunchBlock.objects.filter(
            Q(type=self.type) &
            Q(number=self.number) &
            Q(location=self.location)
        )

        if self.pk is not None:
            qs = qs.exclude(pk=self)

        if qs.count() > 0:
            raise ValidationError(
                '{} с таким номером и расположением уже существует!'.format(self.type)
            )

        try:
            if self.location.room.pbxroom and not self.is_station:
                raise ValidationError(
                    'Нельзя создать не станционный плинт в станционном помещении')
        except AttributeError:
            pass

    class Meta:
        verbose_name = 'плинт'
        verbose_name_plural = 'плинты'


class ExtensionBox(CrossPoint):
    """КРТ -- коробка распределительная телефонная

    Выделена отдельно от плинтов, потому что:
    1) находится не в шкафах, или станционных помещениях,
    2) номер коробки+пары уникален для расположения источника, а не собственного

    Attributes
    ----------
    box_number : CharField
        Номер коробки, например "03а".
    pair_number : PositiveSmallIntegerField
        Номер пары в коробке
    """

    box_number = models.CharField(verbose_name='номер коробки',
                                  max_length=5)
    pair_number = models.PositiveSmallIntegerField(verbose_name='номер плинта')

    class Meta:
        verbose_name = 'КРТ'
        verbose_name_plural = 'КРТ'

    def __str__(self):
        result = 'КРТ {} п.{}'.format(self.box_number, self.pair_number)

        return result

    def journal_str(self):
        return str(self)

    def changes_str(self):
        return str(self)


class Phone(CrossPoint):
    jack = models.PositiveSmallIntegerField(verbose_name='номер розетки',
                                            blank=True,
                                            null=True)

    def __str__(self):
        parent_port = self.main_source

        result = ''
        if isinstance(parent_port, PBXPort) and isinstance(self.source, CrossPoint):
            result = '{} ({})'.format(str(parent_port.subscriber_number),
                                      self.source.journal_str())
            if self.jack:
                result += ', роз. {}'.format(self.jack)
        else:
            result = 'Телефон'

        return result

    def journal_str(self):
        res = '{location}'
        subscribers = self.subscribers.all()

        if self.jack:
            res += ', роз. {jack}'

        if subscribers:

            res += ' ('
            subscribers_count = len(subscribers)
            for i, s in enumerate(subscribers):
                if i == subscribers_count - 1:
                    res += str(s)
                else:
                    res += '{subscribers}, '.format(subscribers=s)
            res += ')'

        res = res.format(location=self.location,
                         jack=self.jack,
                         subscribers=subscribers)

        return res

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
