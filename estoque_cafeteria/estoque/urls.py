from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('logout/', views.logout_view, name='logout_view'),
    path('produtoview/', views.produtoview, name='produtoview'),
    path('estoqueview/', views.estoqueview, name='estoqueview'),
    path('configuracaoview/', views.configuracaoview, name='configuracaoview'),

    # ROTA USER 
    path('cria_usuario/', views.cria_usuario, name='cria_usuario'),
    path('muda_senha/', views.muda_senha, name='muda_senha'),


    path('offline/', views.offline, name='offline'),

]
 