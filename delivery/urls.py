from django.urls import path
from . import views
app_name = 'delivery'
urlpatterns = [
    path('track/<uuid:order_id>/', views.track_live, name='live_track'),
    path('api/eta/', views.get_eta, name='eta'),
]
