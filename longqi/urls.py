from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^get_phone_result/', get_phone_result),
    url(r'^search_phone/', search_phone),
    url(r'^search_phone_local/', search_phone_local),
    url(r'^check_phone_reload/', check_phone_reload),
    url(r'^up_turnover_page/', up_turnover_page),
    url(r'^up_turnover_data/', up_turnover_data),
    url(r'^up_arrive_page/', up_arrive_page),
    url(r'^up_arrive_data/', up_arrive_data),
    url(r'^up_order_page/', up_order_page),
    url(r'^up_order_data/', up_order_data),
    url(r'^longqi/', longqi),
]
