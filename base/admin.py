from django.contrib import admin
from .models import Room, Message


# Customize Room admin display
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')


# Customize Message admin display
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'content', 'timestamp')
    search_fields = ('content', 'user__username', 'room__name')
    list_filter = ('timestamp', 'room')