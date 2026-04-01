from django.urls import path
from . import views
app_name = 'orders'
urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('place/', views.place_order, name='place_order'),
    path('success/<uuid:order_id>/', views.order_success, name='success'),
    path('', views.order_list, name='list'),
    path('<uuid:order_id>/', views.order_detail, name='detail'),
    path('<uuid:order_id>/cancel/', views.cancel_order, name='cancel'),
    path('<uuid:order_id>/track/', views.track_order, name='track'),
    path('<uuid:order_id>/reorder/', views.reorder, name='reorder'),
]
