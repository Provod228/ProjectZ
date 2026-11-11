from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Колонки в списке пользователей
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    # Фильтры справа
    list_filter = ('is_staff', 'is_active')
    # Поиск по этим полям
    search_fields = ('username', 'email')
    # Сортировка по умолчанию
    ordering = ('-date_joined',)