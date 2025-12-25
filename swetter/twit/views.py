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
from .forms import ProfileForm
from django.db.models import Q
from difflib import get_close_matches





def index(request):
    return render(request, 'index.html')

@login_required
def twit_list(request):
    twits = twit.objects.all().order_by('-created_at')
    following_ids = set(Follow.objects.filter(follower=request.user).values_list('following__id', flat=True))
    liked_post_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)

    return render(request, 'twit_list.html', {
        'twits': twits,
        'following_ids': following_ids,
        'liked_post_ids': list(liked_post_ids),
    })


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
        # Step 1: Direct partial match (case-insensitive)
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

        # Step 2: Fuzzy match for spelling mistakes
        if not users.exists():
            all_usernames = list(User.objects.values_list("username", flat=True))
            close_matches = get_close_matches(query, all_usernames, n=5, cutoff=0.6)
            users = User.objects.filter(username__in=close_matches)

        # Step 3: Collect user + twits
        for user_obj in users:
            user_twits = twit.objects.filter(user=user_obj).order_by('-created_at')[:10]
            user_data_list.append({
                "user": user_obj,
                "twits": user_twits,
                "score": len(user_twits)  # simple score based on activity
            })

        # Step 4: Sort by score (descending)
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

    # follower/following counts
    followers_count = user.followers.count()
    following_count = user.following.count()

    # check if current logged-in user is following this profile
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    return render(request, "profile.html", {
        "user_obj": user,
        "profile": profile,
        "twits": twits,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
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



@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

def followers_list(request, username):
    user_obj = get_object_or_404(User, username=username)
    followers = user_obj.followers.select_related('follower')
    return render(request, 'followers_list.html', {
        'user_obj': user_obj,
        'followers': followers,
    })

def following_list(request, username):
    user_obj = get_object_or_404(User, username=username)
    following = user_obj.following.select_related('following')
    return render(request, 'following_list.html', {
        'user_obj': user_obj,
        'following': following,
    })

# views.py
from django.http import JsonResponse

@login_required
def like_post(request, post_id):
    post = get_object_or_404(twit, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        status = "unliked"
    else:
        status = "liked"
    return JsonResponse({"status": status, "likes_count": post.likes.count()})

@login_required
def comment_post(request, post_id):
    post = get_object_or_404(twit, id=post_id)
    text = request.POST.get("comment")
    if text:
        comment = Comment.objects.create(user=request.user, post=post, text=text)
        return JsonResponse({
            "status": "ok",
            "user": comment.user.username,
            "text": comment.text,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M")
        })
    return JsonResponse({"status": "error"}, status=400)

@login_required
def share_post(request, post_id, recipient_id):
    post = get_object_or_404(twit, id=post_id)
    recipient = get_object_or_404(User, id=recipient_id)
    Share.objects.create(sender=request.user, recipient=recipient, post=post)
    return JsonResponse({"status": "shared", "recipient": recipient.username})

# ...existing code...


