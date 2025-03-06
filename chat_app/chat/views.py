
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatSession, Message
from users.models import CustomUser

@login_required
def chat_home(request):
    # Fetch all chat sessions where the logged-in user is either user1 or user2
    chat_sessions = ChatSession.objects.filter(user1=request.user) | ChatSession.objects.filter(user2=request.user)
    chat_sessions = chat_sessions.order_by('-created_at')  # Order by most recent chat
    return render(request, 'chat/home.html', {'chat_sessions': chat_sessions})

@login_required
def chat_detail(request, chat_id):
    # Get the chat session with the provided chat_id
    chat_session = ChatSession.objects.get(id=chat_id)

    # Ensure the logged-in user is part of the chat session
    if request.user not in [chat_session.user1, chat_session.user2]:
        return redirect('chat_home')

    # Get all messages for the chat session
    messages = Message.objects.filter(chat=chat_session).order_by('timestamp')

    return render(request, 'chat/chat_detail.html', {'chat_session': chat_session, 'messages': messages})

@login_required
def start_chat(request, user_id):
    # Start a new chat with the user who has the given user_id
    other_user = CustomUser.objects.get(id=user_id)

    # Ensure the user is not trying to chat with themselves
    if request.user == other_user:
        return redirect('chat_home')

    # Create a new chat session if it doesn't exist already
    chat_session, created = ChatSession.objects.get_or_create(
        user1=request.user,
        user2=other_user
    )

    return redirect('chat_detail', chat_id=chat_session.id)
