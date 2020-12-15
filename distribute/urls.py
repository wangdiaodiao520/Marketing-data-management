from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^distribute/', distribute),
    url(r'^distribute_form/', distribute_form),
    url(r'^mouth_statistical/', mouth_statistical),
    url(r'^all_no_consult/', all_no_consult),
    url(r'^all_no_line/', all_no_line),
    url(r'^show_today_form/', show_today_form),
]
