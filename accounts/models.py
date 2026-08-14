from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('employer', 'Employer'),
        ('seeker', 'Job Seeker'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='seeker')

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    skills = models.TextField(blank=True, help_text="Example: Python, Django, SQL, Machine Learning")
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pic/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
