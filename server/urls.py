from django.urls import path
from . import views

urlpatterns = [
    path('couriers/<int:courier_id>', views.redirect_courier_request),
    path('couriers', views.couriers_post_request),
    path('orders/assign', views.orders_assign_request),
    path('orders/complete', views.orders_complete_request),
    path('orders', views.orders_post_request)
]
