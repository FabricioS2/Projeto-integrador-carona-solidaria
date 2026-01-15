# # # import json
# # # from channels.generic.websocket import AsyncWebsocketConsumer
# # # from channels.db import database_sync_to_async
# # # from .models import Usuario, MensagemChat # <--- Importe o novo modelo

# # # class ChatConsumer(AsyncWebsocketConsumer):
# # #     async def connect(self):
# # #         self.room_group_name = 'chat_global'
# # #         self.usuario_id = await self.get_session_usuario_id()

# # #         if self.usuario_id:
# # #             await self.channel_layer.group_add(
# # #                 self.room_group_name,
# # #                 self.channel_name
# # #             )
# # #             await self.accept()
# # #         else:
# # #             await self.close()

# # #     async def disconnect(self, close_code):
# # #         await self.channel_layer.group_discard(
# # #             self.room_group_name,
# # #             self.channel_name
# # #         )

# # #     async def receive(self, text_data):
# # #         text_data_json = json.loads(text_data)
# # #         mensagem = text_data_json['message']

# # #         # 1. Busca usuário
# # #         usuario = await self.get_usuario(self.usuario_id)

# # #         if usuario:
# # #             # 2. SALVA NO BANCO DE DADOS
# # #             await self.salvar_mensagem(usuario, mensagem)

# # #             # 3. Envia para o Redis (Broadcast)
# # #             await self.channel_layer.group_send(
# # #                 self.room_group_name,
# # #                 {
# # #                     'type': 'chat_message',
# # #                     'message': mensagem,
# # #                     'nome_usuario': usuario.nome,
# # #                     'foto_url': usuario.foto.url if usuario.foto else '',
# # #                     'user_id_sender': self.usuario_id
# # #                 }
# # #             )

# # #     async def chat_message(self, event):
# # #         await self.send(text_data=json.dumps({
# # #             'message': event['message'],
# # #             'nome_usuario': event['nome_usuario'],
# # #             'foto_url': event['foto_url'],
# # #             'is_me': event['user_id_sender'] == self.usuario_id
# # #         }))

# # #     # --- Métodos de Banco de Dados ---

# # #     @database_sync_to_async
# # #     def get_session_usuario_id(self):
# # #         return self.scope['session'].get('usuario_id')

# # #     @database_sync_to_async
# # #     def get_usuario(self, user_id):
# # #         try:
# # #             return Usuario.objects.get(id=user_id)
# # #         except Usuario.DoesNotExist:
# # #             return None

# # #     @database_sync_to_async
# # #     def salvar_mensagem(self, usuario, texto):
# # #         # Cria a mensagem no banco
# # #         MensagemChat.objects.create(usuario=usuario, conteudo=texto)



# # # consumers.py
# # import json
# # from channels.generic.websocket import AsyncWebsocketConsumer
# # from channels.db import database_sync_to_async
# # from .models import Usuario, MensagemChat, Carona, SolicitacaoCarona
# # from django.utils import timezone

# # class CaronaChatConsumer(AsyncWebsocketConsumer):
# #     async def connect(self):
# #         self.carona_id = self.scope['url_route']['kwargs']['carona_id']
# #         self.room_group_name = f'chat_carona_{self.carona_id}'
# #         self.usuario_id = self.scope['session'].get('usuario_id')

# #         # Verificar se o usuário tem permissão para acessar este chat
# #         autorizado = await self.verificar_permissao(self.usuario_id, self.carona_id)

# #         if autorizado:
# #             await self.channel_layer.group_add(
# #                 self.room_group_name,
# #                 self.channel_name
# #             )
# #             await self.accept()
# #         else:
# #             await self.close(code=4003)  # Código para acesso negado

# #     async def disconnect(self, close_code):
# #         await self.channel_layer.group_discard(
# #             self.room_group_name,
# #             self.channel_name
# #         )

# #     async def receive(self, text_data):
# #         text_data_json = json.loads(text_data)
# #         mensagem = text_data_json['message']
# #         carona_id = text_data_json.get('carona_id')

# #         # Verificar se a carona ainda está ativa
# #         carona_ativa = await self.verificar_carona_ativa(carona_id)
        
# #         if not carona_ativa:
# #             await self.send(text_data=json.dumps({
# #                 'carona_finalizada': True,
# #                 'message': 'Esta carona foi finalizada. O chat não está mais disponível.'
# #             }))
# #             return

# #         usuario = await self.get_usuario(self.usuario_id)
# #         carona = await self.get_carona(carona_id)

# #         if usuario and carona:
# #             # Salvar mensagem no banco
# #             await self.salvar_mensagem(usuario, carona, mensagem)

# #             # Enviar para o grupo
# #             await self.channel_layer.group_send(
# #                 self.room_group_name,
# #                 {
# #                     'type': 'chat_message',
# #                     'message': mensagem,
# #                     'nome_usuario': usuario.nome,
# #                     'foto_url': usuario.foto.url if usuario.foto else '',
# #                     'user_id_sender': self.usuario_id
# #                 }
# #             )

# #     async def chat_message(self, event):
# #         # Enviar mensagem para o WebSocket
# #         await self.send(text_data=json.dumps({
# #             'message': event['message'],
# #             'nome_usuario': event['nome_usuario'],
# #             'foto_url': event['foto_url'],
# #             'is_me': event['user_id_sender'] == self.usuario_id
# #         }))

# #     # Métodos de banco de dados
# #     @database_sync_to_async
# #     def verificar_permissao(self, usuario_id, carona_id):
# #         try:
# #             usuario = Usuario.objects.get(id=usuario_id)
# #             carona = Carona.objects.get(id=carona_id)
            
# #             # Verificar se a carona está ativa
# #             if carona.status in ['Finalizada', 'Removida']:
# #                 return False
            
# #             # Verificar se o motorista aceitou pelo menos uma pessoa
# #             if not SolicitacaoCarona.objects.filter(carona=carona, status='Aceita').exists():
# #                 return False
            
# #             # Verificar se usuário é motorista
# #             if carona.motorista == usuario:
# #                 return True
            
# #             # Verificar se usuário é passageiro aceito
# #             if SolicitacaoCarona.objects.filter(
# #                 carona=carona, 
# #                 passageiro=usuario, 
# #                 status='Aceita'
# #             ).exists():
# #                 return True
            
# #             return False
# #         except:
# #             return False

# #     @database_sync_to_async
# #     def verificar_carona_ativa(self, carona_id):
# #         try:
# #             carona = Carona.objects.get(id=carona_id)
# #             return carona.status in ['Agendada', 'Em Andamento']
# #         except:
# #             return False

# #     @database_sync_to_async
# #     def get_usuario(self, user_id):
# #         try:
# #             return Usuario.objects.get(id=user_id)
# #         except Usuario.DoesNotExist:
# #             return None

# #     @database_sync_to_async
# #     def get_carona(self, carona_id):
# #         try:
# #             return Carona.objects.get(id=carona_id)
# #         except Carona.DoesNotExist:
# #             return None

# #     @database_sync_to_async
# #     def salvar_mensagem(self, usuario, carona, texto):
# #         MensagemChat.objects.create(
# #             usuario=usuario,
# #             carona=carona,
# #             conteudo=texto,
# #             carona_ativa=True
# #         )


# # consumers.py - Certifique-se que está assim

# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from .models import Usuario, MensagemChat, Carona, SolicitacaoCarona
# from django.utils import timezone
# import logging

# logger = logging.getLogger(__name__)

# class CaronaChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.carona_id = self.scope['url_route']['kwargs']['carona_id']
#         self.room_group_name = f'chat_carona_{self.carona_id}'
        
#         # Tentar obter o usuário da sessão
#         session = self.scope.get('session')
#         if session:
#             self.usuario_id = session.get('usuario_id')
#         else:
#             self.usuario_id = None
        
#         logger.info(f"Tentando conectar: usuário_id={self.usuario_id}, carona_id={self.carona_id}")
        
#         # Verificar se o usuário tem permissão para acessar este chat
#         autorizado = await self.verificar_permissao(self.usuario_id, self.carona_id)
        
#         if autorizado:
#             await self.channel_layer.group_add(
#                 self.room_group_name,
#                 self.channel_name
#             )
#             await self.accept()
#             logger.info(f"Conexão aceita para carona {self.carona_id}")
#         else:
#             logger.warning(f"Acesso negado para carona {self.carona_id}")
#             await self.close(code=4003)

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#         logger.info(f"Desconectado da carona {self.carona_id}, código: {close_code}")

#     async def receive(self, text_data):
#         try:
#             text_data_json = json.loads(text_data)
#             mensagem = text_data_json.get('message', '').strip()
#             carona_id = text_data_json.get('carona_id')
            
#             logger.info(f"Recebida mensagem: {mensagem[:50]}... para carona {carona_id}")
            
#             if not mensagem:
#                 return
            
#             # Verificar se a carona ainda está ativa
#             carona_ativa = await self.verificar_carona_ativa(carona_id)
            
#             if not carona_ativa:
#                 await self.send(text_data=json.dumps({
#                     'carona_finalizada': True,
#                     'message': 'Esta carona foi finalizada. O chat não está mais disponível.'
#                 }))
#                 return

#             usuario = await self.get_usuario(self.usuario_id)
#             carona = await self.get_carona(carona_id)

#             if usuario and carona:
#                 # Salvar mensagem no banco
#                 await self.salvar_mensagem(usuario, carona, mensagem)
                
#                 # Enviar para o grupo
#                 await self.channel_layer.group_send(
#                     self.room_group_name,
#                     {
#                         'type': 'chat_message',
#                         'message': mensagem,
#                         'nome_usuario': usuario.nome,
#                         'foto_url': usuario.foto.url if usuario.foto and usuario.foto.url else '',
#                         'user_id_sender': self.usuario_id
#                     }
#                 )
#                 logger.info(f"Mensagem salva e enviada para grupo {self.room_group_name}")
                
#         except json.JSONDecodeError as e:
#             logger.error(f"Erro ao decodificar JSON: {e}")
#         except Exception as e:
#             logger.error(f"Erro no receive: {e}")

#     async def chat_message(self, event):
#         try:
#             await self.send(text_data=json.dumps({
#                 'message': event['message'],
#                 'nome_usuario': event['nome_usuario'],
#                 'foto_url': event['foto_url'],
#                 'user_id_sender': event['user_id_sender'],
#                 'is_me': str(event['user_id_sender']) == str(self.usuario_id)
#             }))
#         except Exception as e:
#             logger.error(f"Erro ao enviar mensagem: {e}")

#     # ========== MÉTODOS DE BANCO DE DADOS ==========
    
#     @database_sync_to_async
#     def verificar_permissao(self, usuario_id, carona_id):
#         try:
#             if not usuario_id:
#                 return False
                
#             usuario = Usuario.objects.get(id=usuario_id)
#             carona = Carona.objects.get(id=carona_id)
            
#             logger.info(f"Verificando permissão: usuário={usuario.nome}, carona={carona.id}, status={carona.status}")
            
#             # Verificar se a carona está ativa
#             if carona.status not in ['Agendada', 'Em Andamento']:
#                 logger.warning(f"Carona {carona_id} não está ativa, status: {carona.status}")
#                 return False
            
#             # Verificar se o motorista aceitou pelo menos uma pessoa
#             aceitas_count = SolicitacaoCarona.objects.filter(carona=carona, status='Aceita').count()
#             logger.info(f"Carona {carona_id} tem {aceitas_count} passageiros aceitos")
            
#             if aceitas_count == 0:
#                 logger.warning(f"Carona {carona_id} não tem passageiros aceitos")
#                 return False
            
#             # Verificar se usuário é motorista
#             if carona.motorista == usuario:
#                 logger.info(f"Usuário {usuario.nome} é motorista da carona")
#                 return True
            
#             # Verificar se usuário é passageiro aceito
#             is_passageiro = SolicitacaoCarona.objects.filter(
#                 carona=carona, 
#                 passageiro=usuario, 
#                 status='Aceita'
#             ).exists()
            
#             logger.info(f"Usuário {usuario.nome} é passageiro aceito: {is_passageiro}")
#             return is_passageiro
            
#         except Usuario.DoesNotExist:
#             logger.error(f"Usuário {usuario_id} não encontrado")
#             return False
#         except Carona.DoesNotExist:
#             logger.error(f"Carona {carona_id} não encontrada")
#             return False
#         except Exception as e:
#             logger.error(f"Erro na verificação de permissão: {e}")
#             return False

#     @database_sync_to_async
#     def verificar_carona_ativa(self, carona_id):
#         try:
#             carona = Carona.objects.get(id=carona_id)
#             return carona.status in ['Agendada', 'Em Andamento']
#         except Carona.DoesNotExist:
#             return False

#     @database_sync_to_async
#     def get_usuario(self, user_id):
#         try:
#             return Usuario.objects.get(id=user_id)
#         except Usuario.DoesNotExist:
#             return None

#     @database_sync_to_async
#     def get_carona(self, carona_id):
#         try:
#             return Carona.objects.get(id=carona_id)
#         except Carona.DoesNotExist:
#             return None

#     @database_sync_to_async
#     def salvar_mensagem(self, usuario, carona, texto):
#         try:
#             mensagem = MensagemChat.objects.create(
#                 usuario=usuario,
#                 carona=carona,
#                 conteudo=texto,
#                 carona_ativa=True
#             )
#             logger.info(f"Mensagem salva no BD: ID={mensagem.id}, usuário={usuario.nome}, carona={carona.id}")
#             return mensagem
#         except Exception as e:
#             logger.error(f"Erro ao salvar mensagem: {e}")
#             raise



# consumers.py - Substitua todo o conteúdo por isso:

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Usuario, MensagemChat, Carona, SolicitacaoCarona

logger = logging.getLogger(__name__)

class CaronaChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.carona_id = self.scope['url_route']['kwargs']['carona_id']
            self.room_group_name = f'chat_carona_{self.carona_id}'
            
            # Obter usuário ID da sessão usando async
            self.usuario_id = await self.get_usuario_id_from_session()
            
            logger.info(f"Tentando conectar: usuário_id={self.usuario_id}, carona_id={self.carona_id}")
            
            # Verificar permissão
            autorizado = await self.verificar_permissao(self.usuario_id, self.carona_id)
            
            if autorizado:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
                logger.info(f"Conexão aceita para carona {self.carona_id}")
            else:
                logger.warning(f"Acesso negado para carona {self.carona_id}")
                await self.close(code=4003)
                
        except Exception as e:
            logger.error(f"Erro no connect: {e}")
            await self.close(code=4000)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"Desconectado da carona {self.carona_id}, código: {close_code}")
        except Exception as e:
            logger.error(f"Erro no disconnect: {e}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            mensagem = text_data_json.get('message', '').strip()
            
            logger.info(f"Recebida mensagem: {mensagem[:50]}... para carona {self.carona_id}")
            
            if not mensagem:
                return
            
            # Verificar se a carona ainda está ativa
            carona_ativa = await self.verificar_carona_ativa(self.carona_id)
            
            if not carona_ativa:
                await self.send(text_data=json.dumps({
                    'carona_finalizada': True,
                    'message': 'Esta carona foi finalizada. O chat não está mais disponível.'
                }))
                return

            usuario = await self.get_usuario(self.usuario_id)
            carona = await self.get_carona(self.carona_id)

            if usuario and carona:
                # Salvar mensagem no banco
                await self.salvar_mensagem(usuario, carona, mensagem)
                
                # Enviar para o grupo
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': mensagem,
                        'nome_usuario': usuario.nome,
                        'foto_url': usuario.foto.url if usuario.foto else '',
                        'user_id_sender': str(self.usuario_id)
                    }
                )
                logger.info(f"Mensagem salva e enviada para grupo {self.room_group_name}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
        except Exception as e:
            logger.error(f"Erro no receive: {e}")

    async def chat_message(self, event):
        try:
            is_me = str(event['user_id_sender']) == str(self.usuario_id)
            
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'nome_usuario': event['nome_usuario'],
                'foto_url': event['foto_url'],
                'user_id_sender': event['user_id_sender'],
                'is_me': is_me
            }))
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")

    # ========== MÉTODOS DE BANCO DE DADOS ==========
    
    @database_sync_to_async
    def get_usuario_id_from_session(self):
        """Obtém o usuário ID da sessão de forma síncrona"""
        session = self.scope.get('session', {})
        if hasattr(session, 'session_key') and session.session_key:
            # Se a sessão já foi carregada
            return session.get('usuario_id')
        return None
    
    @database_sync_to_async
    def verificar_permissao(self, usuario_id, carona_id):
        try:
            if not usuario_id:
                return False
                
            usuario = Usuario.objects.get(id=usuario_id)
            carona = Carona.objects.get(id=carona_id)
            
            logger.info(f"Verificando permissão: usuário={usuario.nome}, carona={carona.id}, status={carona.status}")
            
            # Verificar se a carona está ativa
            if carona.status not in ['Agendada', 'Em Andamento']:
                logger.warning(f"Carona {carona_id} não está ativa, status: {carona.status}")
                return False
            
            # Verificar se o motorista aceitou pelo menos uma pessoa
            aceitas_count = SolicitacaoCarona.objects.filter(carona=carona, status='Aceita').count()
            logger.info(f"Carona {carona_id} tem {aceitas_count} passageiros aceitos")
            
            if aceitas_count == 0:
                logger.warning(f"Carona {carona_id} não tem passageiros aceitos")
                return False
            
            # Verificar se usuário é motorista
            if carona.motorista == usuario:
                logger.info(f"Usuário {usuario.nome} é motorista da carona")
                return True
            
            # Verificar se usuário é passageiro aceito
            is_passageiro = SolicitacaoCarona.objects.filter(
                carona=carona, 
                passageiro=usuario, 
                status='Aceita'
            ).exists()
            
            logger.info(f"Usuário {usuario.nome} é passageiro aceito: {is_passageiro}")
            return is_passageiro
            
        except Usuario.DoesNotExist:
            logger.error(f"Usuário {usuario_id} não encontrado")
            return False
        except Carona.DoesNotExist:
            logger.error(f"Carona {carona_id} não encontrada")
            return False
        except Exception as e:
            logger.error(f"Erro na verificação de permissão: {e}")
            return False

    @database_sync_to_async
    def verificar_carona_ativa(self, carona_id):
        try:
            carona = Carona.objects.get(id=carona_id)
            return carona.status in ['Agendada', 'Em Andamento']
        except Carona.DoesNotExist:
            return False

    @database_sync_to_async
    def get_usuario(self, user_id):
        try:
            return Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return None

    @database_sync_to_async
    def get_carona(self, carona_id):
        try:
            return Carona.objects.get(id=carona_id)
        except Carona.DoesNotExist:
            return None

    @database_sync_to_async
    def salvar_mensagem(self, usuario, carona, texto):
        try:
            mensagem = MensagemChat.objects.create(
                usuario=usuario,
                carona=carona,
                conteudo=texto,
                carona_ativa=True
            )
            logger.info(f"Mensagem salva no BD: ID={mensagem.id}, usuário={usuario.nome}, carona={carona.id}")
            return mensagem
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")
            raise