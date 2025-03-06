from django.urls import path
from .views import chat_home

urlpatterns = [
    path('', chat_home, name='chat_home'),
]
