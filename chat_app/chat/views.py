
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatSession, Message
from users.models import CustomUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import ChatSession, Message
import json
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def chat_home(request):
    # Fetch all chat sessions where the logged-in user is either user1 or user2
    chat_sessions = ChatSession.objects.filter(user1=request.user) | ChatSession.objects.filter(user2=request.user)
    chat_sessions = chat_sessions.order_by('-created_at')  # Order by most recent chat

    # Fetch all users except the logged-in user
    users = User.objects.exclude(id=request.user.id)

    return render(request, 'chat/home.html', {
        'chat_sessions': chat_sessions,
        'users': users  # Pass users to the template
    })

@login_required
def chat_detail(request, chat_id):
    # Get the chat session with the provided chat_id
    chat_session = get_object_or_404(ChatSession, id=chat_id)

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

@login_required
def send_message(request, chat_id):
    # Get the chat session or return a 404 if not found
    chat_session = get_object_or_404(ChatSession, id=chat_id)

    # Ensure the user is part of the chat session
    if request.user not in [chat_session.user1, chat_session.user2]:
        return JsonResponse({"error": "You are not part of this chat session."}, status=400)

    if request.method == "POST":
        # Parse the message content from the request body
        message_data = request.body.decode("utf-8")
        try:
            message_content = json.loads(message_data).get("message")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

        if message_content:
            # Save the message to the database
            message = Message.objects.create(
                chat=chat_session,
                sender=request.user,
                content=message_content,
                timestamp=timezone.now()
            )

            return JsonResponse({
                "success": True,
                "timestamp": message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return JsonResponse({"error": "Message content cannot be empty."}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)