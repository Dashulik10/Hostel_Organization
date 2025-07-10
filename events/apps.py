from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events'

    def ready(self):
        from events.signals import setup_groups_and_permissions
        from django.db.models.signals import post_migrate
        post_migrate.connect(setup_groups_and_permissions, sender=self)
        print(
            'Events signals connected'
        )