from django.contrib.admin import site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import CustomUser, Follow


class CustomUserAdmin(UserAdmin):
    """Кастомное отображение модели User а админке."""
    list_display = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('email', 'first_name')
    search_fields = ('username', 'email')
    empty_value_display = '--пусто--'


site.unregister(Group)
site.register(CustomUser, CustomUserAdmin)
site.register(Follow)
