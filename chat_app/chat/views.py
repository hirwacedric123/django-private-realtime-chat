from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import CustomUser

def chat_home(request):
    users = CustomUser.objects.exclude(id=request.user.id)  # Exclude current user
    return render(request, 'chat/home.html', {'users': users})
