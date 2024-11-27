from django.views.generic.edit import FormView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse_lazy, reverse
from .forms import *
from django.contrib.auth.models import User, auth
from .models import Company_Profile
from django.contrib.auth.forms import UserChangeForm
from django.views import generic
# Create your views here.


@login_required
def dashboard(request):
    return render(request, 'registration/dashboard.html', {'section': 'dashboard'})



def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            #create new user object
            new_user = user_form.save(commit=False)
            #set the choosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            #Save the user object
            new_user.save()
            
            return render(request, 'registration/register_done.html', {'new_user':new_user})
        
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})
    


@login_required
def company_profile(request):
   form = CompanyForm(instance=request.user.company_profile)
   context = {'form':form}
   if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=request.user.company_profile)
        #company_profile = request.user.company_profile
        if form.is_valid():
            form.save()
            print(form.errors.as_data())
            return redirect('company_profile')
        
            #return redirect('main_dashboard')
            #print(form.errors.as_data()
        else:
        #form = CompanyForm(instance =request.user.company_profile)
            return render(request, 'registration/company_profile.html', context)
   else:
       return render(request, 'registration/company_profile.html', context)

    
@login_required
def user_profile(request):
    form = UserProfileForm(instance=request.user)
    context = {'form': form}

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        
        if form.is_valid:
            form.save()
            return redirect('user_profile')
    
    else : 
        return render(request, 'registration/user_profile.html', context)

    return render(request, 'registration/user_profile.html', context)