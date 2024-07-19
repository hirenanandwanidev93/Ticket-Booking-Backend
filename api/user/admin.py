from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

class UsersAdmin(UserAdmin):

    list_display = ('email','username','is_active','date_joined','is_superuser')
    list_display_links = ('email',)
    ordering = ('-date_joined',)
    readonly_fields = ["date_joined"]


admin.site.register(User, UsersAdmin)
admin.site.unregister(Group)
