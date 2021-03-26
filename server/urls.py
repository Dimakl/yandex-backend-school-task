from django.urls import path
from . import views

urlpatterns = [
    path('couriers', views.couriers_post_request),
    #path('write_msg', views.write_log),
]
