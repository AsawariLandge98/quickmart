from django.urls import path
from . import views
app_name = 'admin_panel'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.products, name='products'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<uuid:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<uuid:product_id>/delete/', views.product_delete, name='product_delete'),
    path('orders/', views.orders_list, name='orders'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('users/', views.users_list, name='users'),
    path('users/<uuid:user_id>/', views.user_detail, name='user_detail'),
    path('users/<uuid:user_id>/toggle/', views.toggle_user_active, name='toggle_user'),
    path('inventory/', views.inventory, name='inventory'),
    path('inventory/<int:variant_id>/stock/', views.update_stock, name='update_stock'),
    path('analytics/', views.analytics, name='analytics'),
    path('coupons/', views.coupons, name='coupons'),
    path('coupons/add/', views.coupon_add, name='coupon_add'),
    path('categories/', views.categories_manage, name='categories'),
    path('reviews/', views.reviews_list, name='reviews'),
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('banners/', views.banners_manage, name='banners'),
]
