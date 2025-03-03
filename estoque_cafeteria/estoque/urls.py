from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import handler404, handler500
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login, name='login'),
    path('logout/', views.logout_view, name='logout_view'),

    path('produtoview/', views.produtoview, name='produtoview'),

    path('estoqueview/', views.estoqueview, name='estoqueview'),
    path('configuracaoview/', views.configuracaoview, name='configuracaoview'),

    #ROTAS TESTES
    path('update_loja_user/', views.update_loja_user, name='update_loja_user'),
    #DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),
    path('obter-dados/', views.obter_dados, name='obter_dados'),

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



    #ROTA PRODUTO
    path('produtos/', views.listar_produtos, name='listar_produtos'),
    path('produtos/novo/', views.criar_produto, name='criar_produto'),
    path('produtos/editar/', views.editar_produto, name='editar_produto'),
    path('produtos_excluir/<int:id_produto>/', views.excluir_produto, name='excluir_produto'),

    path('cria_movimento_de_estoque_em_lote/', views.cria_movimento_de_estoque_em_lote, name='cria_movimento_de_estoque_em_lote'),

    path('offline/', views.offline, name='offline'),


    #BACKUP
    path('backup/', views.retornadados, name='backup'),
    path('api/importar-dados/', views.importar_dados_json, name='importar_dados_json'),
    path('api/backup/download/dados', views.download_json, name='downloadJson'),

    path('cadastra_user_loja/', views.cadastroUserLoja, name='cadastra-user-loja'),
    path('criaLoja/', views.criaLoja, name='criaLoja'),
    path('atualizaLoja/', views.atualizaLoja, name='atualizaLoja'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = views.error_404_view
handler500 = views.error_500_view
handler401 = views.error_401_view