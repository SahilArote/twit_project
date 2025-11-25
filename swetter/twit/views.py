from django.shortcuts import render
from .models import twit
from .forms import twitForm , UserRegistrationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User


def index(request):
    return render(request, 'index.html')

@login_required
def twit_list(request):
    twits = twit.objects.all().order_by('-created_at')
    return render(request , 'twit_list.html', {'twits':twits})

@login_required
def twit_create(request):
    if request.method == "POST":
      form = twitForm(request.POST,request.FILES)
      if form.is_valid():
          twit =form.save(commit=False)
          twit.user = request.user
          twit.save()
          return redirect('twit_list')
    else:
        form = twitForm()
    return render(request , 'twit_form.html', {'form': form})

@login_required
def twit_edit(request, twit_id):
    twit_obj = get_object_or_404(twit, pk=twit_id, user=request.user)
    if request.method == 'POST':
        form = twitForm(request.POST, request.FILES, instance=twit_obj)
        if form.is_valid():
            updated_twit = form.save(commit=False)
            updated_twit.user = request.user
            updated_twit.save()
            return redirect('twit_list')
    else:
        form = twitForm(instance=twit_obj)
    return render(request, 'twit_form.html', {'form': form})
    



@login_required
def twit_delete(request, twit_id):
    twit_obj = get_object_or_404(twit, pk=twit_id, user=request.user)

    if request.method == 'POST':
        twit_obj.delete()
        return redirect('twit_list')

    return render(request, 'twit_delete.html', {'twit': twit_obj})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('twit_list')
    else:
        form = UserRegistrationForm()



    return render(request, 'registration/register.html', {'form': form})

@login_required
def search_user(request):
    query = request.GET.get('q')
    user_profile = None
    user_twits = []

    if query:
        user_profile = User.objects.filter(username__iexact=query).first()
        if user_profile:
            user_twits = twit.objects.filter(user=user_profile).order_by('-created_at')

    return render(request, 'search_result.html', {
        'user_profile': user_profile,
        'user_twits': user_twits,
        'query': query
    })





