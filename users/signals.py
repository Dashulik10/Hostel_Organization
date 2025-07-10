from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import User


@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, created, **kwargs):
    if instance.role == User.Role.WORKER:
        workers_group, _ = Group.objects.get_or_create(name='Работники')
        workers_group.user_set.add(instance)
    elif instance.role == User.Role.STUDENT:
        students_group, _ = Group.objects.get_or_create(name='Студенты')
        students_group.user_set.add(instance)

