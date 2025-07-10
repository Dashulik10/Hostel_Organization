from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, F
from django.urls import reverse
from django.utils.text import slugify

from users.models import Worker, Student

def translit_to_eng(s: str) -> str:
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 'э': 'r', 'ю': 'yu', 'я': 'ya'}

    return "".join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))

class Active(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            participant_count = Count('participants')
        ).filter(
            number_of_places__gt = F('participant_count')
        )

class Event(models.Model):

    class SUW(models.IntegerChoices):
        ZERO = 0, '0'
        TWO = 2, '2'
        FOUR = 4, '4'
        SIX = 6, '6'
        EIGHT = 8, '8'
        TEN = 10, '10'
        TWELVE = 12, '12'

    name = models.CharField(verbose_name="Название", max_length=100)
    start_date = models.DateTimeField(verbose_name="Дата начала", blank=False)
    description = models.TextField(verbose_name="Описание", blank=True)
    slug = models.SlugField(verbose_name="Слаг", max_length=100, unique=True)
    number_of_places = models.PositiveIntegerField(verbose_name="Количество мест", default=0)
    number_of_suw_hours = models.IntegerField(verbose_name="Количество ОПТ", choices=SUW.choices, default=SUW.ZERO)

    author = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name="Автор", related_name="events")
    participants = models.ManyToManyField(Student, through="EventAttendance", related_name="participated_events", verbose_name="Участники", blank=True)

    class Meta:
        db_table = 'events'
        verbose_name='Мероприятие'
        verbose_name_plural='Мероприятия'
        ordering = ['start_date']

    def save(self, *args, **kwargs):
        if not self.slug:
            day = self.start_date.day
            month = self.start_date.month
            self.slug = slugify(translit_to_eng(f"{self.name}-{day:02d}-{month:02d}"))

        super().save(*args, **kwargs)

    def has_change(self, fields):
        if self._state.adding:
            return True
        old = Event.objects.get(id=self.id)
        return any(getattr(old, field) != getattr(self, fields) for field in fields)

    def get_absolute_url(self):
        return reverse('events:event_info', kwargs={'event_slug': self.slug})

    def __str__(self):
        return self.name

    def has_available_slots(self):
        return self.participants.count() < self.number_of_places

    objects = models.Manager()
    active = Active()



class EventAttendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances", verbose_name="Студент", limit_choices_to={'user__role' : 'ST'})
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendances", verbose_name="Мероприятия")
    attended = models.BooleanField(verbose_name="Посетил", default=False)

    class Meta:
        unique_together = ('student', 'event')
        verbose_name = "Посещение мероприятия"
        verbose_name_plural = "Посещения мероприятий"
        ordering = ['student__user__last_name', 'student__user__first_name']

    def save(self, *args, **kwargs):
        if self.event.participants.count() >= self.event.number_of_places:
            raise ValidationError("Невозможно записать студента: все места заняты.")
        super().save(*args, **kwargs)

