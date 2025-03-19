# Install Django using pip first:
# pip install django
from django.urls import path

from .views import chatbot_view

urlpatterns = [
    path("/chat", chatbot_view, name="chat"),
]
