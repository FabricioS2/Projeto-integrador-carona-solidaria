from django.urls import path
from . import views

urlpatterns = [
   path('', views.login, name="login"),
   path('logout/', views.logout, name="logout"),
   path('chat/', views.chat, name="chat"),
   path('perfil/', views.perfil, name="perfil"),
   path('historico/', views.historico, name="historico"),
   path('cadastrar_caronas/', views.cadastrar_carona, name="cadastrar_caronas"),
   path('caronas/<int:carona_id>/iniciar/', views.iniciar_carona, name='iniciar_carona'),
   path('caronas/<int:carona_id>/finalizar/', views.finalizar_carona, name='finalizar_carona'),
   path('caronas/<int:carona_id>/remover/', views.remover_carona, name='remover_carona'),

   path('solicitar_carona/', views.solicitar_carona, name="solicitar_carona"),

   path('caronas/<int:carona_id>/iniciar/', views.iniciar_carona, name='iniciar_carona'),
   path('caronas/<int:carona_id>/finalizar/', views.finalizar_carona, name='finalizar_carona'),
   path('caronas/<int:carona_id>/remover/', views.remover_carona, name='remover_carona'),

   path('solicitar_carona/', views.solicitar_carona, name="solicitar_carona"),

   path('cadastro/', views.cadastro, name="cadastro"),
   path('solicitar_carona/', views.solicitar_carona, name="solicitar_carona"),


   # Novas URLs para notificações
   path('solicitar-carona/<int:carona_id>/', views.solicitar_carona_action, name='solicitar_carona_action'),
   path('notificacoes/aceitar/<int:notificacao_id>/', views.aceitar_solicitacao_notificacao, name='aceitar_solicitacao_notificacao'),
   path('notificacoes/recusar/<int:notificacao_id>/', views.recusar_solicitacao_notificacao, name='recusar_solicitacao_notificacao'),
   path('notificacoes/passageiro-recusar/<int:notificacao_id>/', views.passageiro_recusar_carona, name='passageiro_recusar_carona'),
   path('notificacoes/marcar-lida/<int:notificacao_id>/', views.marcar_notificacao_lida, name='marcar_notificacao_lida'),
   path('notificacoes/contador/', views.contador_notificacoes, name='contador_notificacoes'),
   path('notificacoes/motorista-remover/<int:notificacao_id>/', views.motorista_remover_passageiro, name='motorista_remover_passageiro'),

   # Adicione esta linha ao final do urlpatterns
   path('solicitacoes/cancelar/<int:solicitacao_id>/', views.cancelar_solicitacao, name='cancelar_solicitacao'),
]
