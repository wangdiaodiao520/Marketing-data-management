from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^up_load/', up_load),
    url(r'^up_data/', up_data),
    url(r'^form_quality/', form_quality),
    url(r'^get_today_form',  get_today_form),
    url(r'^delete_form',  delete_form),
    url(r'^get_actives_form/(\w+)(.+)(.+)(.+)', get_actives_form, name='get_actives_form'),
]
