from django.contrib import admin

from event import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'city', 'start_date', 'watched', 'active')
    list_filter = ('active', 'city')
    search_fields = ('name',)


admin.site.register(models.Image)
