from django.db import models


class Board(models.Model):
    title = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['date_created']
        verbose_name = "Доска"
        verbose_name_plural = "Доски"


class Membership(models.Model):
    class Role(models.IntegerChoices):
        GUEST = 1, 'Гость'
        MODERATOR = 2, 'Модератор'
        OWNER = 3, 'Создатель'

    user = models.ForeignKey('UserApp.User', on_delete=models.CASCADE)
    board = models.ForeignKey('Board', on_delete=models.CASCADE)
    role = models.IntegerField(choices=Role.choices, default=Role.GUEST)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"
        constraints = [
            models.UniqueConstraint(fields=['user', 'board'], name='unique_board_member'),
        ]


class Column(models.Model):

    board = models.ForeignKey('Board', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']
        verbose_name = "Колонка"
        verbose_name_plural = "Колонки"


class Task(models.Model):
    class Priority(models.IntegerChoices):
        LOW = 1, 'Низкий'
        MEDIUM = 2, 'Средний'
        HIGH = 3, 'Высокий'

    column = models.ForeignKey('Column', on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    due_date = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    assignee = models.ForeignKey(
        'UserApp.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class Comment(models.Model):

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    author = models.ForeignKey('UserApp.User', on_delete=models.CASCADE)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:30]

    class Meta:
        ordering = ['date_created']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

