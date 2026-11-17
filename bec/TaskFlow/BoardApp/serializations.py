from rest_framework import serializers

from .models import Board, Column, Task


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ('id', 'title', 'date_created')
        read_only_fields = ('date_created',)


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ('id', 'board', 'title', 'order')
        read_only_fields = ('board',)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'id',
            'column',
            'title',
            'description',
            'priority',
            'due_date',
            'order',
            'assignee',
        )
        read_only_fields = ('column',)


class ColumnWithTasksSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Column
        fields = ('id', 'title', 'order', 'tasks')


class BoardItemSerializer(serializers.ModelSerializer):
    columns = ColumnWithTasksSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ('id', 'title', 'date_created', 'columns', )
        read_only_fields = ('date_created',)