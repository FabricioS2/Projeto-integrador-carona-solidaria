# # # from django.urls import re_path
# # # from . import consumers

# # # websocket_urlpatterns = [
# # #     re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
# # # ]


# # # routing.py
# # from django.urls import re_path
# # from . import consumers

# # websocket_urlpatterns = [
# #     re_path(r'ws/chat/(?P<carona_id>\w+)/$', consumers.CaronaChatConsumer.as_asgi()),
# # ]


# # routing.py
# from django.urls import re_path
# from . import consumers

# websocket_urlpatterns = [
#     re_path(r'ws/chat/(?P<carona_id>\d+)/$', consumers.CaronaChatConsumer.as_asgi()),
# ]


# routing.py - Deve estar assim:

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<carona_id>\d+)/$', consumers.CaronaChatConsumer.as_asgi()),
]