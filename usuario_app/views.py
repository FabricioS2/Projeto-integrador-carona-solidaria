from django.shortcuts import render
from django.http import HttpResponse


def chat(request):
    return render(request, 'usuario_app/chat.html')

def perfil(request):
    return render(request, 'usuario_app/perfil.html')

def historico(request):
    return render(request, 'usuario_app/historico.html')

def cadastrar_carona(request):
    return render(request, 'usuario_app/cadastrar_carona.html')

def cadastro(request):
    return render(request, 'usuario_app/cadastro.html')

def login(request):
    return render(request, 'usuario_app/login.html')

def solicitar_carona(request):
    return render(request, 'usuario_app/solicitar_carona.html')
