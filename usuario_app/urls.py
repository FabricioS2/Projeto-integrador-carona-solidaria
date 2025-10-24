from django.urls import path
from . import views

urlpatterns = [
   path('', views.index, name="index"),
   path('chat/', views.chat, name="chat"),
   path('perfil/', views.perfil, name="perfil"),
]
