import datetime

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator



class TaskPriority(models.IntegerChoices):
    LOW = 1, "Niski"
    MEDIUM = 2, "Średni"
    HIGH = 3, "Wysoki"


class Task(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    priority = models.SmallIntegerField(choices=TaskPriority.choices, validators=[MinValueValidator(1), MaxValueValidator(3)])
    completion_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class ActivityCategory(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class Activity(models.Model):
    name = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    duration = models.PositiveIntegerField(help_text="Czas trwania w minutach")

    def __str__(self):
        return f"{self.name} - {self.date} - {self.duration} min"
    

class ActivityGoal(models.Model):
    activity = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE)
    goal_duration = models.PositiveIntegerField(help_text="Celowany czas trwania w minutach")
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Cel dla {self.activity} od {self.start_date} do {self.end_date}"

    


