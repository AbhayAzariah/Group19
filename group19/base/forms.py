from django import forms
from .models import Message, Profile


class ProfileForm(forms.ModelForm):
    campus_rank_1 = forms.ChoiceField(choices=Profile.CAMPUS_CHOICES, required=True)
    campus_rank_2 = forms.ChoiceField(choices=Profile.CAMPUS_CHOICES, required=True)
    campus_rank_3 = forms.ChoiceField(choices=Profile.CAMPUS_CHOICES, required=True)

    class Meta:
        model = Profile
        fields = [
            'gre_score', 'gmat_score', 'undergrad_gpa', 
            'desired_field_of_study', 'recommendation_letters', 
            'campus_rank_1', 'campus_rank_2', 'campus_rank_3'
        ]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Enter mesage here...',
                'class': 'form-control'
            })
        }