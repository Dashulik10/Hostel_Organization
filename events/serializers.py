from rest_framework import serializers
from events.models import Event
from users.models import Student


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'name',
            'start_date',
            'description',
            'number_of_places',
            'number_of_suw_hours'
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class StudentSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'user', 'block']


class StudentSuwSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    block = serializers.StringRelatedField()

    class Meta:
        model = Student
        fields = ['id', 'name', 'block', 'suw']

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class MarkSuwEventSerializer(serializers.ModelSerializer):
    students_hours = serializers.DictField(child=serializers.IntegerField(min_value=0),
                                           help_text="Ключ: ID студента, Значение: часы ОПТ")

    def validate_students_hours(self, value):
        students_ids = value.keys()
        existing_students = Student.objects.filter(id__in=students_ids)

        if len(existing_students) != len(value):
            raise serializers.ValidationError("Один или несколько студентов отсутствуют в базе данных.")
        return value

    def update_suw_hours(self, event_slug):
        validated_data = self.validated_data['students_hours']
        updated_students = []

        for student_id, additional_hours in validated_data.items():
            try:
                student = Student.objects.get(id=student_id)
                student.suw += additional_hours
                student.save()

                updated_students.append(student)
            except Student.DoesNotExist:
                continue

        return updated_students

    class Meta:
        model = Event
        fields = ['students_hours']