from django.urls import path
from . import views
app_name = 'payments'
urlpatterns = [
    path('pay/<uuid:order_id>/', views.initiate_payment, name='initiate'),
    path('success/', views.payment_success, name='success'),
    path('failed/', views.payment_failed, name='failed'),
    path('refund/<uuid:order_id>/', views.request_refund, name='refund'),
]
