from django.contrib import admin
from .models import Room, Message, Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gre_score', 'gmat_score', 'undergrad_gpa', 'desired_field_of_study', 'recommendation_letters')
    search_fields = ('user__username', 'gre_score', 'gmat_score', 'desired_field_of_study')
    list_filter = ('campus_rank_1', 'campus_rank_2', 'campus_rank_3')


admin.site.register(Profile, ProfileAdmin)

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