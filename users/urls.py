from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import path, reverse_lazy
from users.views import LoginUser, RoleRegister, RegisterStudent, UserPasswordChange, UserPasswordChangeDone, \
    RegisterWorker, StudentProfile, WorkerProfile

app_name = 'users'
urlpatterns = [
    path('role-register/', RoleRegister.as_view(), name='role_register'),
    path('register-student/', RegisterStudent.as_view(), name='register_student'),
    path('register-worker/', RegisterWorker.as_view(), name='register_worker'),

    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password-change/', UserPasswordChange.as_view(), name='password_change'),
    path('password-change/done/', UserPasswordChangeDone.as_view(), name='password_change_done'),

    path('password-reset/',
         PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="users/password_reset_email.html",
            success_url=reverse_lazy("users:password_reset_done")
         ),
         name='password_reset'),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete")
         ),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
         name='password_reset_complete'),


    path('student/<slug:slug>/', StudentProfile.as_view(), name='student_profile'),
    path('worker/<slug:slug>/', WorkerProfile.as_view(), name='worker_profile'),

]