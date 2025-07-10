from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, CreateView, UpdateView

from users.forms import RegisterStudentForm, UserPasswordChangeForm, RegisterWorkerForm, StudentProfileForm, WorkerProfileForm
from users.models import Student, Worker


class RoleRegister(TemplateView):
    template_name = 'users/register_role.html'

    def get(self, request, *args, **kwargs):
        is_student = request.GET.get('is_student')

        if is_student == "true":
            return redirect(reverse_lazy('users:register_student'))
        elif is_student == "false":
            return redirect(reverse_lazy('users:register_worker'))

        return self.render_to_response(self.get_context_data())

class LoginUser(LoginView):
    template_name = 'users/login.html'


class UserPasswordChange(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:password_change_done')
    form_class = UserPasswordChangeForm

class UserPasswordChangeDone(PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'


class RegisterStudent(CreateView):
    template_name = 'users/register_student.html'
    form_class = RegisterStudentForm
    success_url = reverse_lazy('users:login')
    extra_context = {
        'default_image': settings.DEFAULT_STUDENT_IMAGE,
    }

class RegisterWorker(CreateView):
    template_name = 'users/register_worker.html'
    form_class = RegisterWorkerForm
    success_url = reverse_lazy('users:login')
    extra_context = {
        'default_image': settings.DEFAULT_WORKER_IMAGE,
    }

class StudentProfile(LoginRequiredMixin, UpdateView):
    form_class = StudentProfileForm
    template_name = 'users/student_profile.html'
    extra_context = {
        'default_image': settings.DEFAULT_STUDENT_IMAGE,
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_absolute_url(self):
        return reverse('users:student_profile')

    def get_object(self):
        return get_object_or_404(Student, user__slug=self.kwargs.get('slug'))

class WorkerProfile(LoginRequiredMixin, UpdateView):
    form_class  = WorkerProfileForm
    template_name = 'users/worker_profile.html'
    extra_context = {
        'default_image': settings.DEFAULT_WORKER_IMAGE,
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self):
        return get_object_or_404(Worker, user__slug=self.kwargs.get('slug'))

    def get_absolute_url(self):
        return reverse('users:worker_profile')
