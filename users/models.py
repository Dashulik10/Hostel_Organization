from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from Hostel import settings

def translit_to_eng(s: str) -> str:
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 'э': 'r', 'ю': 'yu', 'я': 'ya'}

    return "".join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))

class User(AbstractUser):

    class Role(models.TextChoices):
        WORKER = 'WR', 'Работник'
        STUDENT = 'ST', 'Студент'

    middle_name = models.CharField(verbose_name="Отчество", max_length=20, blank=True, null=True)
    role = models.CharField(verbose_name="Тип", max_length=20, choices=Role.choices)
    slug = models.SlugField(verbose_name="Слаг", unique=True, max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'users'
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['username']

    def save(self, *args, **kwargs):
        if self.first_name and self.last_name and self.role:
            self.slug = slugify(translit_to_eng(f"{self.first_name}-{self.last_name}-{self.role}"))
        else:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)



class Student(models.Model):

    class Room(models.TextChoices):
        ROOM_A = 'A', 'Комната А'
        ROOM_B = 'B', 'Комната Б'

    user = models.OneToOneField('User', on_delete=models.CASCADE, verbose_name='Пользователь', related_name='student')
    date_birth = models.DateField(verbose_name="Дата рождения", blank=False)
    block = models.ForeignKey('Block', on_delete=models.SET_DEFAULT, related_name='blooks', verbose_name='Блок', blank=False, default=0)
    room = models.CharField(verbose_name='Комната', max_length=1, choices=Room.choices, blank=False, null=False)
    photo = models.ImageField(verbose_name="Фотография", upload_to="users/%Y/%m/%d/", blank=True, null=True, default=settings.DEFAULT_STUDENT_IMAGE)

    suw = models.IntegerField(verbose_name='ОПТ', null=True, default=0, editable=True)

    class Meta:
        db_table = 'students'
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return self.user.username + ' ' + self.user.last_name

    def get_absolute_url(self):
        return reverse('users:student_profile', kwargs={'slug': self.user.slug})

class Worker(models.Model):

    class Post(models.TextChoices):
        ADMIN = 'ADMIN', 'Администарация'
        STUD_COUNCIL = 'COUNCIL', 'Студенческий совет'

    user = models.OneToOneField('User', on_delete=models.CASCADE, verbose_name='Пользователь', related_name='worker')
    post = models.CharField(verbose_name='Должность', max_length=20, choices=Post.choices, blank=False, null=False, default=Post.STUD_COUNCIL)
    date_birth = models.DateField(verbose_name="Дата рождения", blank=False)
    photo = models.ImageField(verbose_name="Фотография", upload_to="users/%Y/%m/%d/", blank=True, null=True, default=settings.DEFAULT_WORKER_IMAGE)

    class Meta:
        db_table = 'workers'
        verbose_name = "Работник"
        verbose_name_plural = "Работники"

    def __str__(self):
        return self.user.username + ' ' + self.user.last_name

    def get_absolute_url(self):
        return reverse('users:worker_profile', kwargs={'slug': self.user.slug})

class Block(models.Model):
    number = models.PositiveIntegerField(verbose_name="Номер")
    slug = models.SlugField(verbose_name="Слаг", max_length=5, unique=True)

    class Meta:
        db_table = 'blocks'
        verbose_name='Блок'
        verbose_name_plural='Блоки'
        ordering = ['number']

    def __str__(self):
        return str(self.number)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"block-{self.number}")

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('users:block_detail', args=[self.slug])
