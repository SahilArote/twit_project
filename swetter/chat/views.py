from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q
from django.http import HttpResponse
from datetime import datetime
from django.utils.timezone import make_aware




from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Max

def chat_home(request):
    users = User.objects.all().order_by('username')
    users_with_messages = []

    for user in users:
        latest_msg = Message.objects.filter(sender=user).order_by('-timestamp').first()
        users_with_messages.append({
            'user': user,
            'message': latest_msg,
        })

    return render(request, 'chat/chat_home.html', {'users_with_messages': users_with_messages})


@login_required
def chat_room(request, room_name):
    search_query = request.GET.get('search', '') 
    users = User.objects.exclude(id=request.user.id) 
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))  

    chats = chats.order_by('timestamp') 
    user_last_messages = []

    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # Sort user_last_messages by the timestamp of the last_message in descending order
    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else make_aware(datetime.min),
        reverse=True
    )

    return render(request, 'chat/chat.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query 
    })
