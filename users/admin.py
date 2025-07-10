from django.contrib import admin

from users.models import User, Student, Block, Worker


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'date_joined')
    prepopulated_fields = {"slug": ("first_name", "last_name", "role")}

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_first_name', 'get_user_last_name', 'get_user_middle_name',
                    'block', 'room', 'suw')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'block__number')
    list_filter = ('block', 'room')
    ordering = ['user__last_name', 'user__first_name']

    def get_user_first_name(self, obj):
        return obj.user.first_name

    def get_user_last_name(self, obj):
        return obj.user.last_name

    def get_user_middle_name(self, obj):
        return obj.user.middle_name

    get_user_first_name.short_description = 'Имя'
    get_user_last_name.short_description = 'Фамилия'
    get_user_middle_name.short_description = 'Отчество'

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('get_user_username', 'get_user_first_name', 'get_user_last_name', 'post', 'date_birth')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'post')
    list_filter = ('post',)
    ordering = ['user__last_name', 'user__first_name']

    def get_user_username(self, obj):
        return obj.user.username

    def get_user_first_name(self, obj):
        return obj.user.first_name

    def get_user_last_name(self, obj):
        return obj.user.last_name

    get_user_username.short_description = 'Логин'
    get_user_first_name.short_description = 'Имя'
    get_user_last_name.short_description = 'Фамилия'

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('number',)
    search_fields = ('number',)
    ordering = ['number']
    prepopulated_fields = {"slug": ("number",)}
