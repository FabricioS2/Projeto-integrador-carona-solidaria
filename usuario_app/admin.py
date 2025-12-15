from django.contrib import admin
from .models import Usuario, Veiculo, Carona, SolicitacaoCarona, MensagemChat

# Registro básico dos modelos
admin.site.register(Usuario)
admin.site.register(Veiculo)
admin.site.register(Carona)
admin.site.register(SolicitacaoCarona)
admin.site.register(MensagemChat)