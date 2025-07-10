from django.contrib.auth.mixins import PermissionRequiredMixin

menu = [
    {'title': "Главная", 'url_name': 'main:home'},
        ]


class WorkerPermissionMixin(PermissionRequiredMixin):
    def has_permission(self):
        if self.request.user.is_superuser:
            return True
        return super().has_permission() and self.request.user.groups.filter(name="Работники").exists()
