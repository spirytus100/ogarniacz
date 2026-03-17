from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



class TaskPriority(models.IntegerChoices):
    LOW = 1, "Niski"
    MEDIUM = 2, "Średni"
    HIGH = 3, "Wysoki"


class Task(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.SmallIntegerField(choices=TaskPriority.choices, validators=[MinValueValidator(1), MaxValueValidator(3)])
    completion_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name
