from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):

    list_display = ('id', 'user_name', 'user_limit', 'status')


admin.site.register(User, UserAdmin)
# Register your models here.
