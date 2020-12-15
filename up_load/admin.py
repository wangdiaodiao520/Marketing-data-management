from django.contrib import admin
from .models import Channel, Form
from login.models import User


channels = Channel.objects.all().values()
channels = {i['id']: i['name'] for i in channels}
users = User.objects.all().values()
users = {i['id']: i['user_name'] for i in users}


class ChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'channel_main')


admin.site.register(Channel, ChannelAdmin)


class FormAdmin(admin.ModelAdmin):
    def show_channel(self, obj):
        return channels[obj.channel]

    def show_name(self, obj):
        if obj.consult:
            return users[obj.consult]
        else:
            return '无'
    list_display = ('phone', 'show_channel', 'show_name', 'submit_time', 'up_time')
    list_filter = ('submit_time',)


admin.site.register(Form, FormAdmin)
# Register your models here.
