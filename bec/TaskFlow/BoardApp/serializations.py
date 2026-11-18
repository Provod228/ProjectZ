from rest_framework import serializers

from .models import Board, Column, Comment, Membership, Task


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
    def validate_assignee(self, assignee):
        if assignee is None:
            return None

        column = self.instance.column if self.instance is not None else self.context['column']
        if not Membership.objects.filter(board_id=column.board_id, user=assignee).exists():
            raise serializers.ValidationError('Исполнитель должен быть участником доски.')
        return assignee

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


class TaskUpdateSerializer(TaskSerializer):
    column = serializers.PrimaryKeyRelatedField(
        queryset=Column.objects.none(),
        required=False,
        error_messages={'does_not_exist': 'Выбери существующую колонку этой доски.'},
    )

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            fields['column'].queryset = Column.objects.filter(
                board_id=self.instance.column.board_id,
            )
        return fields


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'task', 'author', 'text', 'date_created')
        read_only_fields = ('task', 'author', 'date_created')


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
