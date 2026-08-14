from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser, Profile


class CustomCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'role'
        ]


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile

        fields = ['phone','skills','education','experience','github','linkedin','resume','profile_pic']

        widgets = {
            'github': forms.TextInput(
                attrs={
                    'type': 'text',
                    'placeholder': 'https://github.com/username'
                }
            ),
            'linkedin': forms.TextInput(
                attrs={
                    'type': 'text',
                    'placeholder': 'https://linkedin.com/in/username'
                }
            ),
            'skills': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Python, Django, SQL, Machine Learning'
                }
            ),

            'education': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'B.Tech AI & ML'
                }
            ),

            'experience': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Fresher / Internship details'
                }
            ),

            'resume': forms.FileInput(
                attrs={
                    'accept': '.pdf'
                }
            ),

            'profile_pic': forms.FileInput(
                attrs={
                    'accept': 'image/*'
                }
            ),
        }