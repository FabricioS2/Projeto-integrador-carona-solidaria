import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Usuario, MensagemChat # <--- Importe o novo modelo

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'chat_global'
        self.usuario_id = await self.get_session_usuario_id()

        if self.usuario_id:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        mensagem = text_data_json['message']

        # 1. Busca usuário
        usuario = await self.get_usuario(self.usuario_id)

        if usuario:
            # 2. SALVA NO BANCO DE DADOS
            await self.salvar_mensagem(usuario, mensagem)

            # 3. Envia para o Redis (Broadcast)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': mensagem,
                    'nome_usuario': usuario.nome,
                    'foto_url': usuario.foto.url if usuario.foto else '',
                    'user_id_sender': self.usuario_id
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'nome_usuario': event['nome_usuario'],
            'foto_url': event['foto_url'],
            'is_me': event['user_id_sender'] == self.usuario_id
        }))

    # --- Métodos de Banco de Dados ---

    @database_sync_to_async
    def get_session_usuario_id(self):
        return self.scope['session'].get('usuario_id')

    @database_sync_to_async
    def get_usuario(self, user_id):
        try:
            return Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return None

    @database_sync_to_async
    def salvar_mensagem(self, usuario, texto):
        # Cria a mensagem no banco
        MensagemChat.objects.create(usuario=usuario, conteudo=texto)