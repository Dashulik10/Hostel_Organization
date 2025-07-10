from django.contrib import admin
from events.models import Event, EventAttendance


class EventAttendanceInline(admin.TabularInline):
    model = Event.participants.through
    extra = 1
    verbose_name = "Участник"
    verbose_name_plural = "Участники"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'number_of_places',
                    'number_of_suw_hours', 'participant_count', 'author')
    search_fields = ('name', 'author__user__last_name',
                     'author__user__first_name')
    list_filter = ('start_date', 'author', 'number_of_places',
                   'number_of_suw_hours')
    ordering = ['start_date']
    inlines = [EventAttendanceInline]

    @admin.display(description="Участники")
    def participant_count(self, obj):
        return obj.participants.count()

@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'event', 'attended')
    search_fields = ('student__user__last_name', 'event__name')
    list_filter = ('attended', 'event')
    ordering = ['event', 'student__user__last_name']