from django.contrib.admin import site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import CustomUser, Follow

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('email', 'first_name')
    search_fields = ('username', 'email')
    # add_fieldsets = (
    #     (None, {'fields': ('username',)}),
    #     ('Personal info', {'fields': ('first_name', 'last_name', 'email')})
    # )
    empty_value_display = '--пусто--'

site.unregister(Group)
site.register(CustomUser, CustomUserAdmin)
site.register(Follow)
