from django.shortcuts import render
from django.http import HttpResponse


def index(request):
   return render(request, 'usuario_app/index.html')
