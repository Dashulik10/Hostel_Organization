from rest_framework.permissions import BasePermission

class IsWorker(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Работники').exists()

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name="Студенты ").exists()