from django.contrib import admin

from .models import Task, Board, Column, Membership, Comment


# Register your models here.


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'column', 'priority', 'assignee', 'due_date')
    # колонки в списке
    list_filter = ('priority', 'column__board')
    # фильтры; через __ можно идти по связям
    search_fields = ('title', 'description')
    # поиск
    list_select_related = ('column', 'assignee')
    # связанные объекты одним запросом, без N+1
    list_editable = ('priority',)


class ColumnInline(admin.TabularInline):
    model = Column
    extra = 0


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_created')
    search_fields = ('title', )
    list_filter = ('date_created',)
    inlines = (ColumnInline, MembershipInline)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'board', 'role')
    list_filter = ('board', 'role')
    list_select_related = ('board', 'user')
    list_editable = ('role',)

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'order')
    list_filter = ('board', )
    list_select_related = ('board', )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'text', 'date_created')
    search_fields = ('text', 'task__title', 'author__username')
    list_filter = ('date_created',)
    list_select_related = ('task', 'author')
