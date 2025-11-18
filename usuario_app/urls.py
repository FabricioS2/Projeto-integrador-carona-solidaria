from django.urls import path
from . import views

urlpatterns = [
   path('', views.login, name="login"),
   path('chat/', views.chat, name="chat"),
   path('perfil/', views.perfil, name="perfil"),
   path('historico/', views.historico, name="historico"),
   path('cadastrar_caronas/', views.cadastrar_carona, name="cadastrar_caronas"),
   path('cadastro/', views.cadastro, name="cadastro"),
   path('solicitar_carona/', views.solicitar_carona, name="solicitar_carona"),
]
