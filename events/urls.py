from django.urls import path
from events.views import AddEventAPI, ListEventsAPI, UpdateEventAPI, EventDetailAPI, DeleteEventAPI, \
    AddStudentAPI, MarkSuwEventAPI, ManageStudentSuwAPI, EnrollInEventAPI

app_name='events'

urlpatterns = [

    path('api/add-event/', AddEventAPI.as_view(), name='add_event_api'),
    path('api/', ListEventsAPI.as_view(), name='list_events_api'),
    path('api/edit-event/<slug:event_slug>', UpdateEventAPI.as_view(), name='udate_event_api'),
    path('api/event/<slug:event_slug>', EventDetailAPI.as_view(), name='event_detail_api'),
    path('api/delete-event/<slug:event_slug>', DeleteEventAPI.as_view(), name='delete_event_api'),
    path('api/event/<slug:event_slug>/add-students/', AddStudentAPI.as_view(), name='add_students_api'),
    path('api/<slug:event_slug>/enroll/', EnrollInEventAPI.as_view(), name='enroll_in_event_api'),
    path('api/<slug:event_slug>/mark-suw/', MarkSuwEventAPI.as_view(), name='mark_suw_event_api'),
    path('api/manage-student-suw/', ManageStudentSuwAPI.as_view(), name='manage_student_suw_api'),

]