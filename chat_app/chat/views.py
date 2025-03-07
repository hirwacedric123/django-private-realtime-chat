
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
from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.http import require_POST
import os

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
    # Get the user we want to chat with
    other_user = get_object_or_404(CustomUser, id=user_id)

    # Ensure the user is not trying to chat with themselves
    if request.user == other_user:
        return redirect('chat_home')

    # Check if a chat already exists in either order
    chat_session = ChatSession.objects.filter(
        models.Q(user1=request.user, user2=other_user) |
        models.Q(user1=other_user, user2=request.user)
    ).first()

    # If no existing chat session, create a new one
    if not chat_session:
        chat_session = ChatSession.objects.create(user1=request.user, user2=other_user)

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


@csrf_exempt  # For testing; in production, handle CSRF appropriately
@require_POST
def upload_file(request):
    file_obj = request.FILES.get("file")
    chat_id = request.POST.get("chat_id")
    if not file_obj:
        return JsonResponse({"success": False, "error": "No file provided."})
    
    # Create a file path; e.g., "chat_uploads/{chat_id}/filename.ext"
    upload_path = os.path.join("chat_uploads", chat_id, file_obj.name)
    saved_path = default_storage.save(upload_path, ContentFile(file_obj.read()))
    file_url = default_storage.url(saved_path)
    file_type = file_obj.content_type

    return JsonResponse({
        "success": True,
        "file_url": file_url,
        "file_type": file_type
    })