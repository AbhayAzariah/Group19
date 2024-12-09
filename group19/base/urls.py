from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('find/', views.find, name="find"),  # 
    path('compare/', views.compare, name="compare"),
    path('login-register/', views.login_register, name="login_register"),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_user, name='logout'),
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.create_room, name='create_room'),
    path('rooms/<int:room_id>/', views.chatroom, name='chatroom'),
    path('rooms/<int:room_id>/edit/', views.edit_room, name='edit_room'),
    path('rooms/<int:room_id>/delete/', views.delete_room, name='delete_room'),
    path('message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('add-to-comparison/', views.add_to_comparison, name='add_to_comparison'),
]
