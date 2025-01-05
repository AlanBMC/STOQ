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
    path('editar_nome_user/', views.editar_nome_user, name='editar_nome_user'),
    path('delete_usuario/<int:user_id>/', views.delete_usuario, name='delete_usuario'),

    #ROTA CATEGORIA
    path('categorias/', views.listar_categorias, name='listar_categorias'),
    path('categorias/nova/', views.criar_categoria, name='criar_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/excluir/<int:pk>/', views.excluir_categoria, name='excluir_categoria'),

    
    path('offline/', views.offline, name='offline'),

]
 