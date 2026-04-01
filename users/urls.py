from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/<int:pk>/edit/', views.edit_address, name='edit_address'),
    path('address/<int:pk>/delete/', views.delete_address, name='delete_address'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<uuid:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('spin/', views.spin_wheel, name='spin'),
]
