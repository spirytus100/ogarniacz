from django.contrib import admin
from .models import Task, Activity, ActivityCategory, ActivityGoal


admin.site.register(Task)
admin.site.register(ActivityCategory)
admin.site.register(ActivityGoal)

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'duration')
    list_filter = ('name', 'date')
    search_fields = ('name__name',)  # Wyszukiwanie po nazwie kategorii aktywności
