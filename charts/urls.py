from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^get_charts/', get_charts),
]
