from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import *

# Register your models here.
admin.site.register(Log)


def export_as_csv(self, request, queryset):
    meta = self.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv; charset=windows-1251')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response, delimiter=';')

    writer.writerow(field_names)
    for obj in queryset:
        row = [getattr(obj, field) for field in field_names]
        writer.writerow(row)
    return response
export_as_csv.short_description = "Экспортировать в CSV выбранные"

class ItemAdmin(admin.ModelAdmin):
    list_display = ('address', 'name', 'model', 'system_id', 'date', 'time_in', 'time_out', 'vendor', 'state', 'rfid')
    actions = [export_as_csv]


admin.site.register(Item, ItemAdmin)
