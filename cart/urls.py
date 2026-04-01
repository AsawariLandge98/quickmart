from django.urls import path
from . import views
app_name = 'cart'
urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('add/', views.add_to_cart, name='add'),
    path('update/<int:item_id>/', views.update_cart, name='update'),
    path('coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('coupon/remove/', views.remove_coupon, name='remove_coupon'),
    path('api/count/', views.cart_count_api, name='count_api'),
    path('voice-search/', views.voice_search, name='voice_search'),
    path('voice-add/', views.voice_add_to_cart, name='voice_add'),
]
