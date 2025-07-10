from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from events.models import Event
from users.models import User, Student


def setup_groups_and_permissions(sender, **kwargs):
    workers_group, _ = Group.objects.get_or_create(name='Работники')
    students_group, _ = Group.objects.get_or_create(name='Студенты')

    try:
        event_content_type = ContentType.objects.get_for_model(Event)
        student_content_type = ContentType.objects.get_for_model(Student)
    except ContentType.DoesNotExist:
        return

    worker_permission = Permission.objects.filter(content_type=event_content_type, codename__in=[
        'add_event', 'change_event', 'delete_event', 'view_event',
    ])
    stud_permissions_for_workers = Permission.objects.filter(content_type=student_content_type, codename__in=[
        'change_student', 'delete_student',
    ])

    workers_group.permissions.set(worker_permission)
    workers_group.permissions.add(*stud_permissions_for_workers)

    student_permissions = Permission.objects.filter(content_type=event_content_type, codename__in=[
        'view_event'
    ])
    students_group.permissions.set(student_permissions)



