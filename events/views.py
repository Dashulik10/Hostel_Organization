from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from events.models import Event
from events.permissions import IsWorker, IsStudent
from events.serializers import EventSerializer, EventDetailSerializer, StudentSelectSerializer, MarkSuwEventSerializer, StudentSuwSerializer
from users.models import Student

from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView

from django_filters.rest_framework import DjangoFilterBackend

class AddEventAPI(CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsWorker]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.worker)

class ListEventsAPI(ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventDetailSerializer
    filter_backends = [
        OrderingFilter,
        SearchFilter,
        DjangoFilterBackend,
    ]

    search_fields = ['name', 'start_date']
    filterset_fields = ['start_date']
    ordering_fields = ['start_date']
    ordering = ['-start_date']

class UpdateEventAPI(UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'event_slug'
    permission_classes = [IsAuthenticated, IsWorker]

class EventDetailAPI(RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventDetailSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'event_slug'

class DeleteEventAPI(DestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'event_slug'
    permission_classes = [IsAuthenticated, IsWorker]

class AddStudentAPI(APIView):
    permission_classes = [IsAuthenticated, IsWorker]

    def get(self, request, *args, **kwargs):
        event_slug = kwargs.get('event_slug')
        event = get_object_or_404(Event, slug=event_slug)

        available_students = Student.objects.exclude(participated_events=event)

        serializer = StudentSelectSerializer(available_students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        event_slug = kwargs.get('event_slug')
        event = get_object_or_404(Event, slug=event_slug)

        students_ids = request.data.get('students', [])

        if not isinstance(students_ids, list) or not all(isinstance(id, int) for id in students_ids):
            return Response({'error':'Invalid student id list'}, status=status.HTTP_400_BAD_REQUEST)

        students = Student.objects.filter(id__in=students_ids)

        if not students.exists():
            return Response({'error':'No valid students found'}, status=status.HTTP_404_NOT_FOUND)

        for student in students:
            if event.has_available_slots() and student not in event.participants.all():
                event.participants.add(student)
            else:
                return Response({'error':'No available slots!'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success':'Students added successfully!'}, status=status.HTTP_200_OK)

class EnrollInEventAPI(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, *args, **kwargs):
        event_slug = kwargs.get('event_slug')
        if not kwargs.get('event_slug'):
            return Response({'error': 'Event slug is required!'}, status=status.HTTP_400_BAD_REQUEST)

        event = get_object_or_404(Event, slug=event_slug)

        if not request.user.student:
            return Response({'error':'Only students!'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.student in event.participants.all():
            return Response ({'error':'Already enrolled!'}, status=status.HTTP_400_BAD_REQUEST)

        if event.has_available_slots():
            event.participants.add(request.user.student)
            return Response ({'success':'Student enrolled successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'No available slots!'}, status=status.HTTP_400_BAD_REQUEST)

class MarkSuwEventAPI(APIView):
    permission = [IsAuthenticated, IsWorker]

    def get(self, request, *args, **kwargs):
        event_slug = kwargs.get('event_slug')
        event = get_object_or_404(Event, slug=event_slug)

        students = event.participants.all()

        serializer = StudentSuwSerializer(students, many=True)
        return Response({
            'event': {
                "name" : event.name,
                "slug" : event.slug
            },
            'students': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, event_slug, *args, **kwargs):
        serializer = MarkSuwEventSerializer(data=request.data)

        if serializer.is_valid():
            updated_students = serializer.update_suw_hours(event_slug=event_slug)
            event = get_object_or_404(Event, slug=event_slug)

            response_data = {
                "event" : {
                    'name' : event.name,
                    'slug' : event.slug
                },
                "students" : StudentSuwSerializer(updated_students, many=True).data
            }

            return Response ({
                'success' : "Часы ОПТ успешно обновлены.",
                'details' : response_data},
                status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManageStudentSuwAPI(APIView):
    permission_classes = [IsAuthenticated, IsWorker]

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        students = Student.objects.all()

        if query:
            students = students.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(block__number__icontains=query)
            )

        serializer = StudentSuwSerializer(students, many=True)
        return Response({
            'students' : serializer.data
        },
        status=status.HTTP_200_OK
        )


    def post(self, request, *args, **kwargs):
        student_id = request.data.get('student_id')
        operation = request.data.get('operation', '').strip()
        suw_hours = request.data.get('suw_hours', 0)

        if not student_id or not operation or not str(suw_hours).isdigit():
            return Response(
                {'error' : 'Неправильные данные запроса.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            suw_hours = int (suw_hours)
            if suw_hours < 0:
                return Response(
                    {'error' : 'Количество часов должно быть положительным.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error' : 'Количество часов должно быть числом.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            student = Student.objects.get(id=student_id)
            if operation == '+':
                student.suw += suw_hours
            elif operation == '-':
                student.suw -= suw_hours
                if student.suw < 0:
                    student.suw = 0
            else:
                return Response(
                    {'error': 'Неправильная операция. Используйте "+" или "-".'},
                    status=status.HTTP_400_BAD_REQUEST)
            student.save()

        except Student.DoesNotExist:
            return Response(
                {'error': 'Студент не найден.'},
                status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSuwSerializer(student)
        return Response(
            {'message': 'Часы ОПТ успешно обновлены.', 'student': serializer.data},
            status=status.HTTP_200_OK)





