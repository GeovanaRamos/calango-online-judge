from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from accounts import models

admin.site.register(models.Student)
admin.site.register(models.Professor)


@admin.register(models.User)
class CustomUserAdmin(BaseUserAdmin):
    # exclude = ('username',)
    fieldsets = (
        (None, {'fields': ('password',)}),
        ('Personal info', {'fields': ('full_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'email', 'password1', 'password2', 'is_active', 'is_superuser'),
        }),
    )
    list_display = ('full_name', 'email', 'is_superuser')
    search_fields = ('email',)
    ordering = ('email',)
