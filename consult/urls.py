from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^consult/', consult),
    url(r'^submit_result/', submit_result),
    url(r'^talk_work/', talk_work),
    url(r'^add_talk/', add_talk),
    url(r'^sale_statistical/(\w+)', sale_statistical, name='sale_statistical'),
    url(r'^no_consult/', no_consult),
    url(r'^no_line/', no_line),
]
