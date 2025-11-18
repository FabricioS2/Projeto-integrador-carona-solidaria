from django.urls import path
from . import views

urlpatterns = [
   path('', views.index, name="index"),
   path('chat/', views.chat, name="chat"),
   path('perfil/', views.perfil, name="perfil"),
   path('cadastro/', views.cadastro, name="cadastro"),
   path('login/', views.login, name="login"),
   path('solicitar_carona/', views.solicitar_carona, name="solicitar_carona"),
]
