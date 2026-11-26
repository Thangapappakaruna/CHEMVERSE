from django.contrib import admin

from .models import Experiment, ExperimentLog


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'category')


admin.site.register(ExperimentLog)
