from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from account.forms import UserChangeForm, UserCreationForm
from account.models import User


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('id', 'email', 'join_date', 'is_active', 'is_admin')

    list_display_links = ('email', )
    list_filter = ('is_admin', 'is_active', )

    fieldsets = (
        ('Personal info', {'fields': ('email', 'password', 'fullname', )}),
        ('Status', {'fields': ('is_active', )}),
        ('Permissions', {'fields': ('is_admin', )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_admin', )}
         ),
    )

    search_fields = ('email', 'fullname', )
    ordering = ('-id',)

    filter_horizontal = []

    inlines = []

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('email', 'join_date', )
        else:
            return ('join_date', )


admin.site.register(User, UserAdmin)

# unregister default group
admin.site.unregister(Group)
