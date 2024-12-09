from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    CAMPUS_CHOICES = [
        (1, 'Rural'),
        (2, 'Suburban'),
        (3, 'Urban'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gre_score = models.IntegerField(null=True, blank=True, help_text="Enter your GRE score.")
    gmat_score = models.IntegerField(null=True, blank=True, help_text="Enter your GMAT score.")
    undergrad_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    desired_field_of_study = models.CharField(max_length=100, null=True, blank=True)
    recommendation_letters = models.IntegerField(null=True, blank=True)
    campus_rank_1 = models.IntegerField(choices=CAMPUS_CHOICES, null=True, blank=True)
    campus_rank_2 = models.IntegerField(choices=CAMPUS_CHOICES, null=True, blank=True)
    campus_rank_3 = models.IntegerField(choices=CAMPUS_CHOICES, null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} Profile"

class Room(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms_created")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content[:30]}'