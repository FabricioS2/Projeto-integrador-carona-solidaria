# """
# ASGI config for carona_solidadria_project project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carona_solidadria_project.settings')

# application = get_asgi_application()


# import os
# import django
# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nome_do_seu_projeto.settings') # Verifique o nome
# django.setup()

# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.sessions import SessionMiddlewareStack
# import usuario_app.routing

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     # Envolvemos as rotas com SessionMiddlewareStack para acessar request.session no consumer
#     "websocket": SessionMiddlewareStack(
#         URLRouter(
#             usuario_app.routing.websocket_urlpatterns
#         )
#     ),
# })



# carona_solidadria_project/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import usuario_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carona_solidadria_project.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            usuario_app.routing.websocket_urlpatterns
        )
    ),
})