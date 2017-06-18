from django.db import models
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords


class BaseHistoryTrackerModel(models.Model):
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class Building(BaseHistoryTrackerModel):
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
    destination = models.ForeignKey('self',
                                    verbose_name='направление',
                                    related_name='incoming',
                                    null=True,
                                    blank=True,
                                    )

    def get_subclass(self):
        """
        Метод необходим для случаев, когда мы оперируем объектами класса
        CrossPoint, но необходимо знать подкласс объекта, например, для
        формирования строкового представления, специфичного для этого подкласса
        """

        result = None

        for cp_subclass in CrossPoint.__subclasses__():
            try:
                cp_subclass.objects.get(crosspoint_ptr=self.pk)
                result = cp_subclass
            except models.ObjectDoesNotExist as e:
                pass
        return result

    def get_parent(self):
        """
        Функция находит родительскую точку кросса для текущей точки,
        предполагая, что у всех точек родительской является порт АТС
        """
        from django.db import connection
        src = None

        with connection.cursor() as cursor:
            from os import path
            from django.conf import settings

            sqlfile = open(path.join(settings.BASE_DIR,
                                     'journal',
                                     'sql',
                                     'get_crosspoint_parent.sql',
                                     ),
                           'r')
            sql = sqlfile.read().replace('/n', ' ')

            cursor.execute(sql.format(self.pk))

            row = cursor.fetchone()
            try:
                src = PBXPort.objects.get(pk=row[0])
            except:
                pass

        return src

    def clean(self):
        if self.pk and self.destination:
            if self.destination.pk == self.pk:
                raise ValidationError({'destination': 'Нельзя составлять кольцевые связи'})

    def journal_str(self):
        return self.get_subclass().objects.get(crosspoint_ptr=self.pk).journal_str()

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
    json_path = models.TextField(verbose_name='маршрут в формате JSON',
                                 blank=True,
                                 editable=False)

    def __str__(self):
        return '{}: {} (порт {}, {})'.format(self.pbx,
                                             self.subscriber_number,
                                             self.number,
                                             self.get_type_display())

    def journal_str(self):
        return '{}'.format(self.subscriber_number)

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

    def journal_str(self):
        return str(self)

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
            result = result + '{}/{}'.format(self.number, self.location.cabinet.number)

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

    class Meta:
        verbose_name = 'телефон'
        verbose_name_plural = 'телефоны'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Subscriber(BaseHistoryTrackerModel):
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
