from django.db import models
from django.core.exceptions import ValidationError


class Building(models.Model):
    number = models.CharField(verbose_name='номер', max_length=5, unique=True)
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


class Room(models.Model):
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


class Cabinet(models.Model):
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


class Location(models.Model):
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


class CrossPoint(models.Model):
    location = models.ForeignKey(Location,
                                 verbose_name='расположение')
    destination = models.ForeignKey('self',
                                    verbose_name='направление',
                                    related_name='incoming',
                                    null=True,
                                    blank=True,
                                    )

    def __str__(self):
        try:
            pbxport = PBXPort.objects.get(crosspoint_ptr=self.pk)
        except models.ObjectDoesNotExist as e:
            pbxport = None
        try:
            punch_block = PunchBlock.objects.get(crosspoint_ptr=self.pk)
        except models.ObjectDoesNotExist as e:
            punch_block = None
        try:
            phone = Phone.objects.get(crosspoint_ptr=self.pk)
        except models.ObjectDoesNotExist as e:
            phone = None

        if pbxport:
            return str(pbxport)
        elif punch_block:
            return str(punch_block)
        elif phone:
            return str(phone)


class PBX(models.Model):
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

    def __str__(self):
        return '{} {}'.format(self.get_manufacturer_display(), self.model)

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
    subscriber_number = models.PositiveSmallIntegerField(verbose_name='абонентский номер',
                                                         blank=True,
                                                         null=True,
                                                         unique=True)
    description = models.CharField(verbose_name='описание', max_length=150, blank=True)

    def __str__(self):
        return '{}: {} (порт {}, {})'.format(self.pbx,
                                             self.subscriber_number,
                                             self.number,
                                             self.get_type_display())

    class Meta:
        verbose_name = 'порт АТС'
        verbose_name_plural = 'порты АТС'


class PunchBlock(CrossPoint):
    PUNCHBLOCK_TYPES = (
        ('city', 'Гром-полоса'),
        ('extension', 'Распределение'),
        ('trunk', 'Магистраль'),
    )

    number = models.SmallIntegerField(verbose_name='номер')
    type = models.CharField(verbose_name='тип',
                            choices=PUNCHBLOCK_TYPES,
                            default='trunk',
                            max_length=9)
    is_station = models.BooleanField(verbose_name='станционная (-ое)',
                                     blank=True)

    def __str__(self):
        result = ''

        if self.type == 'city':
            result = 'Гр'
        elif self.type == 'extension':
            result = 'Р'
        elif self.type == 'trunk':
            result = 'М'

        if self.is_station:
            result = result + 'с{}'.format(self.number)
        else:
            result = result + '{}/{}'.format(self.number, self.location.cabinet)

        return result

    def __init__(self, *args, **kwargs):
        super(PunchBlock, self).__init__(*args, **kwargs)
        self._meta.get_field('location').limit_choices_to = {
                                            'cabinet__isnull': False,
                                        }

    class Meta:
        verbose_name = 'плинт'
        verbose_name_plural = 'плинты'


class Phone(CrossPoint):
    def __str__(self):
        return 'Телефон'

    class Meta:
        verbose_name = 'телефон'
        verbose_name_plural = 'телефоны'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._meta.get_field('location').limit_choices_to = {
                                            'room__isnull': False,
                                        }


class Subscriber(models.Model):
    first_name = models.CharField(verbose_name='имя', max_length=30)
    last_name = models.CharField(verbose_name='фамилия', max_length=40)
    patronymic = models.CharField(verbose_name='отчество', max_length=35, blank=True)
    phone = models.ManyToManyField(Phone,
                                   verbose_name='телефоны',
                                   related_name='subscribers',
                                   blank=True)

    class Meta:
        verbose_name = 'абонент'
        verbose_name_plural = 'абоненты'

    def __str__(self):
        return '{} {}.{}.'.format(self.last_name,
                                  self.first_name[0],
                                  self.patronymic[0]
                                  )