from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    search_fields = ['email', 'name'],
    sortable_by = ['email', 'name']
    fieldsets = (
        (('Authentication'), {
            'fields': ('email', 'name', 'password'),
            'description': ('Information used to authenticate users')
        }),
        (('Additional Information'), {
            'fields': ('is_active', 'is_superuser', 'is_staff', 'last_login'),
            'classes': ('collapse',),
            'description': ('Information about user\'s status on the site')
        }),
    )
    add_fieldsets = (
        (('Authentication'), {
            'fields': (('email', 'name'), ('password1', 'password2')),
            'description': ('Registration Information')
        }),
        (('Additional Information'), {
            'fields': ('is_active', 'is_superuser', 'is_staff',),
            'classes': ('collapse',),
            'description': ('User\'s status'),
        }),
    )
