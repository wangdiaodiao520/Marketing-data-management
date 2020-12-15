from django.contrib import admin
from .models import ArriveData, OrderData, Turnover
from login.models import User


users = User.objects.all().values()
users = {i['id']: i['user_name'] for i in users}


class ArriveAdmin(admin.ModelAdmin):
    def show_name(self, obj):
        if obj.consult:
            return users[obj.consult]
        else:
            return '无名'
    list_display = ('phone', 'show_name', 'time')
    list_filter = ('time',)


admin.site.register(ArriveData, ArriveAdmin)


class OrderAdmin(admin.ModelAdmin):
    def show_name(self, obj):
        if obj.consult:
            return users[obj.consult]
        else:
            return '无名'
    list_display = ('phone', 'show_name', 'time')
    list_filter = ('time',)


admin.site.register(OrderData, OrderAdmin)


class TurnoverAdmin(admin.ModelAdmin):
    def show_name(self, obj):
        if obj.consult:
            return users[obj.consult]
        else:
            return '无名'
    list_display = ('phone', 'turnover', 'show_name', 'time')
    list_filter = ('time',)


admin.site.register(Turnover, TurnoverAdmin)
# Register your models here.
