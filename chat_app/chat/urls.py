from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('start-chat/<int:user_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chat/<int:chat_id>/send/', views.send_message, name='send_message'),


]
