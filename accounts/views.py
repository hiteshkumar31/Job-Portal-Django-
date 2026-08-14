from django.shortcuts import render, redirect
from .forms import CustomCreationForm, ProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile

def signup(request):
    if request.method == 'POST':
        form = CustomCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomCreationForm()
    return render(request, 'signup.html', {'form': form})


def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance = profile)

        if form.is_valid():
            form.save()

            messages.success(request, "Profile updated successfully")

            return redirect('profile')
    
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'profile.html', {'form':form, 'profile':profile})
    


