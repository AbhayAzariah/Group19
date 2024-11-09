from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('room/', views.room, name="room"),
    path('find/', views.find, name="find"),
    path('compare/', views.compare, name="compare"),
]