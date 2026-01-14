# usuario_app/context_processors.py
from .models import Notificacao

def notificacoes_context(request):
    if request.session.get('usuario_id'):
        try:
            usuario_id = request.session['usuario_id']
            notificacoes = Notificacao.objects.filter(
                usuario_id=usuario_id,
                lida=False
            ).order_by('-data_criacao')[:10]
            
            # Contar notificações não lidas
            contador_nao_lidas = Notificacao.objects.filter(
                usuario_id=usuario_id,
                lida=False
            ).count()
            
            return {
                'notificacoes_usuario': notificacoes,
                'contador_notificacoes': contador_nao_lidas
            }
        except:
            pass
    
    return {
        'notificacoes_usuario': [],
        'contador_notificacoes': 0
    }