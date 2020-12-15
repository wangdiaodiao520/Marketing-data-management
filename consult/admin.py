from django.contrib import admin
from .models import Active


class ActiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'active')


admin.site.register(Active, ActiveAdmin)

# Register your models here.
