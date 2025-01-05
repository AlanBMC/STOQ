from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .models import Loja
from django.contrib.auth import logout,authenticate, update_session_auth_hash
from django.contrib.auth import login as login_django

def login(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        senha = request.POST.get('senha')
        print(nome, senha)
        user = authenticate(username=nome, password=senha)
        if user:
           
            login_django(request, user)
            return redirect('produtoview')
        else:
            print('entrou no erro')
            messages.error(request, 'Nome ou senha invalidas')
            return redirect('login')

    if request.method == 'GET':
        print('entroui no get')
        return render(request,  'login.html')
    

@login_required(login_url='/')
def produtoview(request):
    return render(request, 'produtoview.html')

@login_required(login_url='/')
def estoqueview(request):
    return render(request, 'estoque.html')

def offline(request):
    return render(request, 'offline.html')


@login_required(login_url='/')
def configuracaoview(request):
    print(request.user.username)
    return render(request, 'configuracao.html')


@login_required(login_url='/')
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/')
def cria_usuario(request):
    '''
    Cria ususario com senha padrao 123
    '''
    if not request.user.has_perm('auth.add_user'):
        messages.error(request, 'Você não tem permissão para criar usuários.')
        return redirect('configuracaoview')  # Redireciona para uma página de erro ou home

    if request.method == 'POST':
        nome = request.POST.get('nome')
        if not User.objects.filter(username=nome).exists():
                user = User.objects.create_user(username= nome, password= '123')
                user.save()
                messages.success(request, f'Usuario {nome} criado com sucesso')
                return redirect('configuracaoview')
        else:
                messages.error(request, f'Usuario com o nome {nome} Ja existe')
                return  redirect('configuracaoview')

@login_required(login_url='/')
def muda_senha(request):
    '''
    Recebe senha antiga e senha nova
    atualiza senha
    '''
    if request.method == 'POST':
        senha_antiga = request.POST.get('senha_antiga')
        senha_nova = request.POST.get('senha_nova')
        user = request.user
        if not user.check_password(senha_antiga):
            messages.error(request, f'Senha antiga invalida')
            return redirect('configuracaoview')
        user.set_password(senha_nova)
        user.save()
        update_session_auth_hash(request,user)
        messages.success(request, f'Senha alterada com sucesso')
        return redirect('configuracaoview')
    
