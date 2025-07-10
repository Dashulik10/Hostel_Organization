from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms

from Hostel import settings
from users.models import Student, Worker, Block


class RegisterStudentForm(UserCreationForm):
    photo = forms.ImageField(label="Фотография", widget=forms.FileInput(), required=False)
    first_name = forms.CharField(label="Имя", max_length=30, required=True, widget=forms.TextInput())
    last_name = forms.CharField(label="Фамилия", max_length=30, required=True, widget=forms.TextInput())
    middle_name = forms.CharField(label="Отчество", max_length=30, required=False, widget=forms.TextInput())
    this_year = date.today().year
    date_birth = forms.DateField(label="Дата Рождения", required=True, widget=forms.SelectDateWidget(years=tuple(range(this_year - 80, this_year - 5))))
    block = forms.ModelChoiceField(label="Блок", queryset=Block.objects.all(), required=True, widget=forms.Select())
    room = forms.ChoiceField(label="Комната", required=True, choices=Student.Room.choices)


    username = forms.CharField(label="Логин", widget=forms.TextInput())
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput())
    email = forms.EmailField(label="Почта", max_length=30, required=True, widget=forms.TextInput())

    class Meta:
        model = get_user_model()
        fields = [
            'first_name', 'last_name', 'middle_name',
            'email',
            'username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = user.Role.STUDENT

        if commit:
            user.save()
            Student.objects.create(user=user,
                                   block=self.cleaned_data['block'],
                                   room=self.cleaned_data['room'],
                                   suw=0,
                                   date_birth=self.cleaned_data['date_birth'],
                                   photo=self.cleaned_data['photo'] or settings.DEFAULT_STUDENT_IMAGE)
        return user


class StudentProfileForm(forms.ModelForm):
    photo = forms.ImageField(label="Фотография", required=False, widget=forms.FileInput())
    first_name = forms.CharField(disabled=True, label="Имя", max_length=30, required=False, widget=forms.TextInput())
    last_name = forms.CharField(disabled=True, label="Фамилия", max_length=30, required=False, widget=forms.TextInput())
    middle_name = forms.CharField(label="Отчество", max_length=30, required=False, widget=forms.TextInput())
    date_birth = forms.DateField(disabled=True, label="Дата Рождения", required=False)
    block = forms.ModelChoiceField(disabled=True, label="Блок", required=False, queryset=Block.objects.all(), widget=forms.Select())
    room = forms.ChoiceField(disabled=True, label="Комната", required=False, choices=Student.Room.choices)

    username = forms.CharField(disabled=True, label="Логин", required=False, widget=forms.TextInput())
    email = forms.EmailField(label="Почта", max_length=30, required=False, widget=forms.TextInput())

    suw = forms.IntegerField(disabled=True, label="ОПТ", required=False, widget=forms.NumberInput())

    class Meta:
        model = Student
        fields = ['photo', 'block', 'room', 'suw', 'date_birth']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if not user:
            raise ValueError("Для создания формы требуется указать `user`.")

        student = user.student

        super().__init__(*args, **kwargs)

        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['middle_name'].initial = user.middle_name
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

            self.fields['photo'].initial = student.photo
            self.fields['block'].initial = student.block
            self.fields['room'].initial = student.room
            self.fields['suw'].initial = student.suw
            self.fields['date_birth'].initial = student.date_birth

    def save(self, commit=True):
        student = super().save(commit=False)
        user = student.user
        if self.cleaned_data['middle_name']:
            user.middle_name = self.cleaned_data['middle_name']
        if self.cleaned_data['email']:
            user.email = self.cleaned_data['email']
        if self.cleaned_data['photo']:
            student.photo = self.cleaned_data['photo']

        if commit:
            user.save()
            student.save()

        return student


class RegisterWorkerForm(UserCreationForm):
    photo = forms.ImageField(label="Фотография", widget=forms.FileInput(), required=False)
    first_name = forms.CharField(label="Имя", max_length=30, required=True, widget=forms.TextInput())
    last_name = forms.CharField(label="Фамилия", max_length=30, required=True, widget=forms.TextInput())
    middle_name = forms.CharField(label="Отчество", max_length=30, required=False, widget=forms.TextInput())
    this_year = date.today().year
    date_birth = forms.DateField(label="Дата Рождения", required=True,
                                 widget=forms.SelectDateWidget(years=tuple(range(this_year - 80, this_year - 5))))

    post = forms.ChoiceField(label="Должность", required=True, choices=Worker.Post.choices)

    username = forms.CharField(label="Логин", widget=forms.TextInput())
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput())
    email = forms.EmailField(label="Почта", max_length=50, widget=forms.TextInput())

    class Meta:
        model = get_user_model()
        fields = [
            'first_name', 'last_name', 'middle_name',
            'email',
            'username', 'password1', 'password2'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = user.Role.WORKER

        if commit:
            user.save()
            Worker.objects.create(user=user,
                                  post=self.cleaned_data['post'],
                                  date_birth=self.cleaned_data['date_birth'],
                                  photo=self.cleaned_data['photo'] or settings.DEFAULT_WORKER_IMAGE
                                  )

        return user

class WorkerProfileForm(forms.ModelForm):
    photo = forms.ImageField(label="Фотография", required=False, widget=forms.FileInput())
    first_name = forms.CharField(disabled=True, label="Имя", max_length=30, required=False, widget=forms.TextInput())
    last_name = forms.CharField(disabled=True, label="Фамилия", max_length=30, required=False, widget=forms.TextInput())
    middle_name = forms.CharField(label="Отчество", max_length=30, required=False, widget=forms.TextInput())
    date_birth = forms.DateField(disabled=True, label="Дата Рождения", required=False)
    post = forms.ChoiceField(disabled=True, label="Должность", required=False, choices=Worker.Post.choices)

    username = forms.CharField(disabled=True, label="Логин", required=False, widget=forms.TextInput())
    email = forms.EmailField(label="Почта", max_length=30, required=False, widget=forms.TextInput())

    class Meta:
        model = Worker
        fields = ['photo', 'date_birth', 'post']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if not user:
            raise ValueError("Для создания формы требуется указать `user`.")

        worker = user.worker

        super().__init__(*args, **kwargs)

        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['middle_name'].initial = user.middle_name
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

            self.fields['photo'].initial = worker.photo
            self.fields['date_birth'].initial = worker.date_birth
            self.fields['post'].initial = worker.post

    def save(self, commit=True):
        worker = super().save(commit=False)
        user = worker.user
        if self.cleaned_data['middle_name']:
            user.middle_name = self.cleaned_data['middle_name']
        if self.cleaned_data['email']:
            user.email = self.cleaned_data['email']
        if self.cleaned_data['photo']:
            worker.photo = self.cleaned_data['photo']

        if commit:
            user.save()
            worker.save()

        return worker


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", max_length=50, widget=forms.PasswordInput())
    new_password1 = forms.CharField(label="Новый пароль", max_length=50, widget=forms.PasswordInput())
    new_password2 = forms.CharField(label="Подтвердить пароль", max_length=50, widget=forms.PasswordInput())



