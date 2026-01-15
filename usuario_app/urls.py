from django.urls import path
from . import views

urlpatterns = [
   path('', views.login, name="login"),
   path('chat/', views.chat, name="chat"),
   path('perfil/', views.perfil, name="perfil"),
   path('historico/', views.historico, name="historico"),
   path('cadastrar_caronas/', views.cadastrar_carona, name="cadastrar_caronas"),
   path('caronas/<int:carona_id>/iniciar/', views.iniciar_carona, name='iniciar_carona'),
   path('caronas/<int:carona_id>/finalizar/', views.finalizar_carona, name='finalizar_carona'),
   path('caronas/<int:carona_id>/remover/', views.remover_carona, name='remover_carona'),

   path('solicitar_carona/', views.solicitar_carona, name="solicitar_carona"),

   path('cadastro/', views.cadastro, name="cadastro"),
   path('solicitar_carona/', views.solicitar_carona, name="solicitar_carona"),
]
