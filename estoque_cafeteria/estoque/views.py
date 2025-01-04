from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json


# Create your views here.
def login(request):
    return render(request,  'login.html')

def produtoview(request):
    return render(request, 'produtoview.html')

def estoqueview(request):
    return render(request, 'estoque.html')

def offline(request):
    return render(request, 'offline.html')

def configuracaoview(request):
    return render(request, 'configuracao.html')

def cria_usuario(request):
    
    pass