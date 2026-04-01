from django.urls import path
from . import views

app_name = 'store'
urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('products/<slug:slug>/review/', views.add_review, name='add_review'),
    path('categories/', views.all_categories, name='categories'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('search/', views.search, name='search'),
    path('api/autocomplete/', views.search_autocomplete, name='autocomplete'),
]
