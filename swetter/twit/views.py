from django.shortcuts import render
from .models import *
from .forms import *
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile




SEARCH_API = "http://127.0.0.1:5001/search"

def api_users(request):
    users = list(User.objects.values("username"))
    return JsonResponse(users, safe=False)



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
    query = request.GET.get("q", "").strip()
    user_data_list = []

    if query:
        try:
            response = requests.get(SEARCH_API, params={"q": query}, timeout=2)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                for user_data in results:
                    username = user_data.get("username")
                    score = user_data.get("score", 0)
                    try:
                        user_obj = User.objects.get(username=username)
                        user_twits = twit.objects.filter(user=user_obj).order_by('-created_at')[:10]
                        user_data_list.append({
                            "user": user_obj,
                            "twits": user_twits,
                            "score": score
                        })
                    except User.DoesNotExist:
                        continue
        except requests.exceptions.RequestException as e:
            print(f"Search API error: {e}")

    # sort by score descending so best matches appear first
    user_data_list.sort(key=lambda x: x.get("score", 0), reverse=True)

    return render(request, "search_result.html", {
        "user_data_list": user_data_list,
        "query": query
    })

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = getattr(user, "profile", None)  # OneToOne relation
    twits = twit.objects.filter(user=user).order_by("-created_at")

    return render(request, "profile.html", {
        "user_obj": user,
        "profile": profile,
        "twits": twits,
    })


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


# ...existing code...


