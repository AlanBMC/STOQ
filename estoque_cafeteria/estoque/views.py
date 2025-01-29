from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .models import Loja,Categoria,Fornecedor, Produto, MovimentoEstoque, UserLoja  
from django.contrib.auth import logout,authenticate, update_session_auth_hash
from django.contrib.auth import login as login_django
from datetime import date, timedelta,datetime
from django.http import HttpResponseNotAllowed, HttpResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, connection
from django.db import connection
from django.apps import apps
from django.core.serializers import serialize

def obter_dados(request):
    '''
    Obter dados para o dashboard
    '''
    # Pegar todas as categorias
    loja = Loja.objects.get(id=request.user.loja.id)
    categorias = Categoria.objects.filter(loja=loja)
    fornecedores = Fornecedor.objects.filter(loja=loja)
    produtos = Produto.objects.filter(loja=loja)
    movimentodeestoque = MovimentoEstoque.objects.filter(loja=loja)

    # Dados para movimentações
    

    total_mov_categoria = {
        categoria.nome: {

        "soma":sum(mov.quantidade for mov in movimentodeestoque if mov.produto.categoria == categoria),
        "contagem": sum(1 for mov in movimentodeestoque if mov.produto.categoria == categoria)
        }
        
        for categoria in categorias
    }
    total_mov_fornecedor = {
        fornecedor.nome: sum(
            1 for mov in movimentodeestoque if mov.produto.fornecedor == fornecedor
        )
        for fornecedor in fornecedores
    }

    contagemporproduto = {
        produto.nome: {
            "quantidade_mov": sum(1 for mov in movimentodeestoque if mov.produto == produto),
            "quantidade_total": sum(mov.quantidade for mov in movimentodeestoque if mov.produto == produto)
        }
        for produto in produtos
    }
    total_mov_produto = {
        produto.nome: sum(
            mov.quantidade for mov in movimentodeestoque if mov.produto == produto
        )
        for produto in produtos
    }
    
    # Retornar como JSON
    return JsonResponse({
        "total_mov_categoria": total_mov_categoria,
        "total_mov_fornecedor": total_mov_fornecedor,
        "total_mov_produto": total_mov_produto,
        "contagemproduto": contagemporproduto
    })

def tour_site(request):
    """
    Verifica se o tour deve ser mostrado para o usuário com base no último login.
    """
    
    
    user = request.user
    if user.last_name == '':
        user.last_name = 'tour 1'
        user.save()
        return True
    elif user.last_name == 'tour 1': 
        user.last_name = 'tour 2'
        user.save()
        return True
    else:
        user.last_name = 'tour 3'
        user.save()
        return False

def verifica_last_name(request):
    user =  request.user
    if user.last_name == 'tour 1':
        return True
    elif user.last_name == 'tour 2':
        return True
    else:
        return False

@login_required(login_url='/')
def dashboard(request):
    show_tour = verifica_last_name(request)
    return render(request, 'dashboard.html', {'show_tour': show_tour})

def login(request):
    """
    Função de view para autenticação de usuários.
    Args:
        request (HttpRequest): Objeto de requisição HTTP.
    Returns:
        HttpResponse: Resposta HTTP com status apropriado ou redirecionamento.
    Métodos HTTP suportados:
        - HEAD: Retorna status 200 para verificar a disponibilidade do serviço.
        - POST: Processa a autenticação do usuário com base no nome e senha fornecidos.
        - GET: Renderiza a página de login.
    Fluxo de POST:
        - Obtém 'nome' e 'senha' do request.POST.
        - Autentica o usuário com authenticate().
        - Se autenticado, realiza login com login_django(), notifica vencimento e redireciona para 'produtoview'.
        - Se falhar, exibe mensagem de erro e redireciona para a página de login.
    Retorna:
        - HttpResponseNotAllowed: Se o método HTTP não for GET, POST ou HEAD.
    """

     
    if request.method == 'HEAD':
        return HttpResponse(status=200) 
    # Lógica de autenticação
    if request.method == 'POST':
        nome = request.POST.get('nome')
        senha = request.POST.get('senha')
        
        user = authenticate(username=nome, password=senha)
        if user:
            login_django(request, user)
            tour_site(request)
            func_notifica_vencimento(request)
            return redirect('produtoview')
        else:
            messages.error(request, 'Nome ou senha inválidos')
            return redirect('login')
    
    if request.method == 'GET':
        return render(request, 'login.html')
    
    return HttpResponseNotAllowed(['GET', 'POST'])

@login_required(login_url='/')
def produtoview(request):
  
    """
      Renderiza a página de visualização de produtos com a lista de categorias, fornecedores, nome da loja e a data de hoje.
        request (HttpRequest): O objeto de requisição HTTP.
        HttpResponse: A página de visualização de produtos renderizada.
    """
    
    show_tour = verifica_last_name(request)
    categorias =  listar_categorias(request)
    fornecedores = listar_fornecedores(request)
    loja_name = request.user.loja.nome
    lojas = UserLoja.objects.filter(user=request.user)
    lojasDoUser = [user.loja for user in lojas]
    is_proprietario = request.user.groups.filter(name="Proprietario").exists()
    print(is_proprietario)
    hoje = date.today()
    return render(request, 'produtoview.html', {'is_proprietario':is_proprietario,'lojasDoUser': lojasDoUser,'show_tour': show_tour, 'loja': loja_name, 'categorias': categorias, 'fornecedores': fornecedores, 'today': hoje})

@login_required(login_url='/')
def update_loja_user(request):
    if request.method == 'POST':
        loja_atual = request.POST.get('lojas')
        usuario = request.user
        loja = get_object_or_404(Loja, id=loja_atual)
        usuario.loja = loja
        usuario.save()
        messages.success(request, 'salvo')
        return redirect('produtoview')

@login_required(login_url='/')
def estoqueview(request):
    '''
    Renderiza a página de estoque com a lista de produtos, categorias, fornecedores e a data de hoje.
    Argumentos: request (HttpRequest): O objeto de requisição HTTP.
    Retorna: HttpResponse: estoque.html com os seguites parâmetros: categorias, fornecedores, produtos e today.
    '''
    produtos =  listar_produtos(request)
    categorias =  listar_categorias(request)
    lojas = Loja.objects.all()
    lojas2 = UserLoja.objects.filter(user=request.user)
    lojasDoUser = [user.loja for user in lojas2]
    #Criar um novo Grupo
    for lo in lojasDoUser:
        print(lo.nome)
    fornecedores = listar_fornecedores(request)
    hoje = date.today()
    show_tour = verifica_last_name(request)
    return render(request, 'estoque.html', {'show_tour': show_tour,'categorias': categorias, 'fornecedores': fornecedores,'produtos': produtos, 'today': hoje,'lojas':lojasDoUser})

def offline(request):
    return render(request, 'offline.html')


@login_required(login_url='/')
def configuracaoview(request):
    '''
    Função para renderizar a página de configuração.
    Argumentos: request (HttpRequest): O objeto de requisição HTTP.
    Retorna: HttpResponse: A página de configuração renderizada com os seguintes parâmetros: usuários e is_proprietario.
    '''
    usuarios =listar_usuarios_da_loja_atual(request)
    is_proprietario = request.user.groups.filter(name='Proprietario').exists()   
    show_tour = verifica_last_name(request)
    return render(request, 'configuracao.html', {'show_tour': show_tour,'usuarios': usuarios, 'is_proprietario': is_proprietario})


@login_required(login_url='/')
def logout_view(request):
    """
    Funcionalidade:
    Realiza o logout do usuário e redireciona para a página de login.
    Argumento:
    request: Objeto HttpRequest que contém os dados da requisição.
    Retorno:
    Redireciona o usuário para a URL de login.
    """

    logout(request)
    return redirect('login')



@login_required(login_url='/')
def cria_usuario(request):
    """
    Funcionalidade: Cria um novo usuário se o nome não existir e o usuário tiver permissão.
    Argumentos: request - objeto HttpRequest contendo dados da requisição.
    Retorno: Redireciona para 'configuracaoview' com mensagem de sucesso ou erro.
    """
    
    if not request.user.has_perm('auth.add_user'):
        messages.error(request, 'Você não tem permissão para criar usuários.')
        return redirect('configuracaoview')  # Redireciona para uma página de erro ou home

    if request.method == 'POST':
        loja = Loja.objects.get(id=request.user.loja.id)
        nome = request.POST.get('nome')
        grupo_funcionario = Group.objects.get(name='Funcionario')
        if not User.objects.filter(username=nome).exists():
                user = User.objects.create_user(username= nome, password= '123', loja=loja)
                user.groups.add(grupo_funcionario)
                user.save()

                messages.success(request, f'Usuario {nome} criado com sucesso')
                return redirect('configuracaoview')
        else:
                messages.error(request, f'Usuario com o nome {nome} Ja existe')
                return  redirect('configuracaoview')

@login_required(login_url='/')
def muda_senha(request):
    """
    Funcionalidade: Altera a senha do usuário autenticado.
    Argumento: request - objeto HttpRequest contendo os dados da requisição.
    Retorno: Redireciona para 'configuracaoview' com mensagem de sucesso ou erro.
    """
    
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
    

@login_required(login_url='/')
def editar_nome_user(request):
    """
    Funcionalidade: Edita o nome de usuário do usuário logado.
    Argumento: request (HttpRequest) - Requisição HTTP contendo o novo nome de usuário.
    Retorno: Redireciona para 'configuracaoview' com mensagem de sucesso ou erro.
    """

    if request.method ==  'POST':
        nome = request.POST.get('nome')
        if User.objects.filter(username=nome).exclude(id=request.user.id).exists():
            messages.error(request, 'Ja existe usuário com este nome')
            return redirect('configuracaoview')
        else:
            user = request.user
            user.username = nome
            user.save()
            messages.success(request, 'Nome alterado com sucesso')
            return redirect('configuracaoview')

@login_required(login_url='/')
def delete_usuario(request, user_id):
    '''
    Deleta usuario, recebe id do usuario a ser deletado
    '''
    if request.user.groups.filter(name='Proprietario').exists():
        try:
            user = User.objects.get(id=user_id)
            if user != request.user:
                user.delete()
                messages.success(request, 'Usuário excluido com sucesso')
            else:
                messages.error(request, 'Você não pode excluir a si mesmo')
        except User.DoesNotExist:
            messages.error(request, 'Usuario nao encontrado')
    else:
        messages.error(request, 'Voce não tem permissão para excluir usuários')
    return redirect('configuracaoview')

@login_required(login_url='/')
def listar_usuarios_da_loja_atual(request):
    '''
    Lista usuarios da loja 1
    '''
    loja_do_usuario = request.user.loja  # Loja do usuário logado
    
    usuarios = User.objects.filter(loja=loja_do_usuario)  # Filtra usuários da mesma loja
    return usuarios

@login_required(login_url='/')
def criar_categoria(request):
    """
    Funcionalidade: Cria uma nova categoria para a loja do usuário logado.
    Argumento: request - Objeto HttpRequest contendo os dados da requisição.
    Retorno: Redireciona para a visualização de produtos.
    """

    if request.method == 'POST':
        nome = request.POST.get('nomeCategoria')
        
        # Verifica se a categoria já existe para a loja do usuário logado
        if Categoria.objects.filter(nome=nome, loja=request.user.loja).exists():
            messages.error(request, 'Categoria com esse nome já existe.')
            return redirect('produtoview')
        
        # Criação da nova categoria
        Categoria.objects.create(nome=nome, loja=request.user.loja)
        messages.success(request, 'Categoria criada com sucesso.')
        return redirect('produtoview')
    return redirect('produtoview')


@login_required(login_url='/')
def editar_categoria(request, pk):
    """
    Edita uma categoria existente.
    Argumentos:
    - request: Objeto HttpRequest contendo dados da requisição.
    - pk: ID da categoria a ser editada.
    Retorno:
    Redireciona para a lista de categorias ou para a visualização do produto.
    """

    categoria = get_object_or_404(Categoria, pk=pk, loja=request.user.loja)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        
        # Evita duplicação ao editar (exclui a própria categoria da verificação)
        if Categoria.objects.filter(nome=nome, loja=request.user.loja).exclude(pk=pk).exists():
            messages.error(request, 'Já existe uma categoria com esse nome.')
            return redirect('listar_categorias')

        categoria.nome = nome
        categoria.save()
        messages.success(request, 'Categoria atualizada com sucesso.')
        return redirect('listar_categorias')
    return redirect('produtoview')


@login_required(login_url='/')
def excluir_categoria(request, pk):
    """
    Exclui uma categoria específica.
    Argumentos:
    - request: Objeto HttpRequest.
    - pk: ID da categoria a ser excluída.
    Retorno:
    - Redireciona para 'produtoview'.
    """

    categoria = get_object_or_404(Categoria, pk=pk, loja=request.user.loja)

    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso.')
        return redirect('produtoview')

    return redirect('produtoview')


@login_required(login_url='/')
def listar_categorias(request):
    """
    Funcionalidade: Lista as categorias da loja do usuário.
    Argumento: request - Objeto de requisição HTTP.
    Retorno: QuerySet de categorias filtradas pela loja do usuário.
    """

    categorias = Categoria.objects.filter(loja=request.user.loja)
    return categorias

@login_required(login_url='/')
def listar_fornecedores(request):
    """
    Funcionalidade: Lista os fornecedores da loja do usuário.
    Argumento: request - objeto de requisição HTTP.
    Retorno: QuerySet de fornecedores filtrados pela loja do usuário.
    """

    fornecedores = Fornecedor.objects.filter(loja=request.user.loja)
    return fornecedores

@login_required(login_url='/')
def criar_fornecedor(request):
    """
    Funcionalidade: Cria um novo fornecedor se o método for POST e não houver duplicidade.
    Argumento: request - objeto HttpRequest contendo dados da requisição.
    Retorno: Redireciona para 'produtoview' com mensagem de sucesso ou erro.
    """

    if request.method == 'POST':
        nome = request.POST.get('nome')
        contato = request.POST.get('contato')
        
        # Verifica duplicidade para a loja do usuário logado
        if Fornecedor.objects.filter(nome=nome, loja=request.user.loja).exists():
            messages.error(request, 'Fornecedor com esse nome já existe.')
            return redirect('produtoview')
        
        # Criação do novo fornecedor
        Fornecedor.objects.create(nome=nome, contato=contato, loja=request.user.loja)
        messages.success(request, 'Fornecedor criado com sucesso.')
        return redirect('produtoview')

    return redirect('produtoview')


@login_required(login_url='/')
def editar_fornecedor(request, pk):
    """
    Edita um fornecedor existente.
    Args:
        request (HttpRequest): O objeto de solicitação HTTP.
        pk (int): O ID primário do fornecedor a ser editado.
    Returns:
        HttpResponse: Redireciona para a visualização do produto.
    """
    
    fornecedor = get_object_or_404(Fornecedor, pk=pk, loja=request.user.loja)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        contato = request.POST.get('contato')
        
        # Evita duplicação ao editar (exclui o próprio fornecedor da verificação)
        if Fornecedor.objects.filter(nome=nome, loja=request.user.loja).exclude(pk=pk).exists():
            messages.error(request, 'Já existe um fornecedor com esse nome.')
            return redirect('produtoview')

        fornecedor.nome = nome
        fornecedor.contato = contato
        fornecedor.save()
        messages.success(request, 'Fornecedor atualizado com sucesso.')
        return redirect('produtoview')

    return redirect('produtoview')

@login_required(login_url='/')
def excluir_fornecedor(request, pk):
    """
    Exclui um fornecedor específico.
    Funcionalidade:
    - Obtém o fornecedor pelo ID (pk) e verifica se pertence à loja do usuário.
    - Se o método da requisição for POST, exclui o fornecedor e redireciona para a visualização de produtos com uma mensagem de sucesso.
    - Se o método não for POST, apenas redireciona para a visualização de produtos.
    Argumentos:
    - request: Objeto HttpRequest contendo os dados da requisição.
    - pk: ID do fornecedor a ser excluído.
    Retorno:
    - Redireciona para a visualização de produtos.
    """

    fornecedor = get_object_or_404(Fornecedor, pk=pk, loja=request.user.loja)
    
    if request.method == 'POST':
        fornecedor.delete()
        messages.success(request, 'Fornecedor excluído com sucesso.')
        return redirect('produtoview')

    return redirect('produtoview')


@login_required(login_url='/')
def listar_produtos(request):
    """
    Funcionalidade:
    Lista os produtos disponíveis na loja do usuário logado.
    Argumento:
    request (HttpRequest): Objeto de requisição HTTP que contém informações sobre a solicitação.
    Retorno:
    QuerySet: Conjunto de produtos filtrados pela loja do usuário.
    """

    produtos = Produto.objects.filter(loja=request.user.loja)
    return produtos


@login_required(login_url='/')
def criar_produto(request):
    """
    Funcionalidade: Cria um novo produto se não existir na loja do usuário.
    Argumentos: request (HttpRequest) - Requisição HTTP contendo dados do produto.
    Retorno: Redireciona para 'produtoview' com mensagem de sucesso ou erro.
    """

    if request.method == 'POST':
        nome = request.POST.get('nome')
        quantidade = request.POST.get('quantidade')
        tipo_quantidade = request.POST.get('tipo_quantidade')
        codigo_de_barras = request.POST.get('codigo_de_barras')
        validade = request.POST.get('validade')
        fornecedor_id = request.POST.get('Fornecedor')
        categoria_id = request.POST.get('Categoria')
        estoque_min = request.POST.get('estoque_min')
        # Verifica se o produto já existe na mesma loja
        if Produto.objects.filter(nome=nome, loja=request.user.loja).exists():
            messages.error(request, 'Produto com esse nome já existe.')
            return redirect('produtoview')
        elif Produto.objects.filter(codigo_de_barras=codigo_de_barras, loja=request.user.loja).exists():
            messages.error(request, 'Produto com este codigo de barras ja existe.')
            return redirect('produtoview')
        # Criação do novo produto
        Produto.objects.create(
            nome=nome,
            quantidade=quantidade,
            tipo_quantidade=tipo_quantidade,
            codigo_de_barras=codigo_de_barras,
            validade=validade,
            fornecedor_id=fornecedor_id,
            categoria_id=categoria_id,
            estoque_minimo=estoque_min,
            loja=request.user.loja
        )
        messages.success(request, 'Produto criado com sucesso.')
        return redirect('produtoview')

    return redirect('produtoview')


@login_required(login_url='/')
def editar_produto(request):
    """
    Edita um produto existente no estoque.
    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo os dados do produto a ser editado.
    Returns:
        HttpResponse: Redireciona para a visualização do estoque com mensagens de sucesso ou erro.
    """

    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        
        if not produto_id:
            messages.error(request, 'Produto não encontrado.')
            return redirect('estoqueview')

        produto = get_object_or_404(Produto, id=produto_id, loja=request.user.loja)
        
        nome = request.POST.get('nome')
        quantidade = request.POST.get('quantidade')
        tipo_quantidade = request.POST.get('tipo_quantidade')
        codigo_de_barras = request.POST.get('codigo_de_barras')
        validade = request.POST.get('validade')
        fornecedor_id = request.POST.get('Fornecedor')
        categoria_id = request.POST.get('Categoria')
        estoquemin = request.POST.get('estoque_min')
        # Evita duplicidade ao editar (exclui o próprio produto da verificação)
        if Produto.objects.filter(nome=nome, loja=request.user.loja).exclude(pk=produto_id).exists():
            messages.error(request, 'Já existe um produto com esse nome.')
            return redirect('estoqueview')
        elif Produto.objects.filter(codigo_de_barras=codigo_de_barras, loja=request.user.loja).exclude(pk=produto_id).exists():
            messages.error(request, 'Produto com este código de barras já existe.')
            return redirect('estoqueview')

        if 'notificacoes' in request.session:
            del request.session['notificacoes']
            del request.session['total_notificacoes']
        func_notifica_vencimento(request)
        # Atualização do produto
        produto.nome = nome
        produto.quantidade = quantidade
        produto.tipo_quantidade = tipo_quantidade
        produto.codigo_de_barras = codigo_de_barras
        if validade:
            produto.validade = validade
        if estoquemin:
            
            produto.estoque_minimo = estoquemin
        produto.fornecedor_id = fornecedor_id
        produto.categoria_id = categoria_id
        produto.save()

        messages.success(request, 'Produto atualizado com sucesso.')
        return redirect('estoqueview')

    return redirect('estoqueview')


@login_required(login_url='/')
def excluir_produto(request,id_produto):    
    if request.method == 'POST':
        pk = id_produto
        produto = get_object_or_404(Produto, pk=pk, loja=request.user.loja)

        produto.delete()
        messages.success(request, 'Produto excluído com sucesso.')
        return redirect('estoqueview')

    return redirect('estoqueview')


def func_notifica_vencimento(request):

    '''
        Função para notificar sobre produtos próximos ao vencimento e com baixo estoque.
    Args:
        request (HttpRequest): Objeto de requisição HTTP.
    Descrição:
        Esta função lista todos os produtos e verifica suas datas de validade e quantidades em estoque.
        Notificações são geradas para produtos que estão próximos ao vencimento (em 14, 30 ou 60 dias)
        e para produtos com quantidade em estoque abaixo de um limite mínimo definido por unidade de medida.
    Notificações:
        - Produtos com validade em menos de 14 dias são marcados como 'urgente'.
        - Produtos com validade entre 15 e 30 dias são marcados como 'moderado'.
        - Produtos com validade entre 31 e 60 dias são marcados como 'baixo'.
        - Produtos com quantidade em estoque abaixo do limite mínimo são marcados como 'estoque'.
    Sessão:
        request.session['notificacoes']: Lista de dicionários contendo as notificações geradas.
        request.session['total_notificacoes']: Número total de notificações geradas.
    '''
    all_produtos = listar_produtos(request)
    hoje = date.today()

    # Categorias de alerta para validade
    alerta_60 = []
    alerta_30 = []
    alerta_14 = []

    # Lista para armazenar notificações
    notificacoes = []

    # Verificação de validade dos produtos
    for produto in all_produtos:
        if produto.validade:
            diferenca = produto.validade - hoje

            if timedelta(days=0) <= diferenca <= timedelta(days=14):
                alerta_14.append(produto)
            elif timedelta(days=15) <= diferenca <= timedelta(days=30):
                alerta_30.append(produto)
            elif timedelta(days=31) <= diferenca <= timedelta(days=60):
                alerta_60.append(produto)

    # Adicionando notificações de validade
    for produto in alerta_14:
        notificacoes.append({
            'tipo': 'urgente',
            'icone': 'fas fa-exclamation-circle text-red-500',
            'mensagem': f'O produto {produto.nome} está a menos de 14 dias de vencer.',
        })
    for produto in alerta_30:
        notificacoes.append({
            'tipo': 'moderado',
            'icone': 'fas fa-info-circle text-blue-500',
            'mensagem': f'O produto {produto.nome} vence em menos de 30 dias.',
        })
    for produto in alerta_60:
        notificacoes.append({
            'tipo': 'baixo',
            'icone': 'fas fa-check-circle text-green-500',
            'mensagem': f'O produto {produto.nome} vence em menos de 60 dias.',
        })

    # Verificação de estoque mínimo
    for produto in all_produtos:
        if produto.quantidade is not None and produto.estoque_minimo is not None:
            if produto.quantidade < produto.estoque_minimo:
                notificacoes.append({
                    'tipo': 'estoque',
                    'icone': 'fas fa-box text-yellow-500',
                    'mensagem': f'O produto {produto.nome} está com baixo estoque \n Quantidade atual: ({produto.quantidade} {produto.tipo_quantidade.upper()}).',
                })
            elif produto.quantidade <= produto.estoque_minimo + 1 or (produto.tipo_quantidade.upper() == 'G' and produto.quantidade <= produto.estoque_minimo + 500):
                notificacoes.append({
                    'tipo': 'estoque_perto',
                    'icone': 'fas fa-exclamation-circle text-orange-500',
                    'mensagem': f'O produto {produto.nome} está perto de atingir o estoque mínimo  \n Quantidade atual: ({produto.quantidade} {produto.tipo_quantidade.upper()}) \n Quantidade minima {produto.estoque_minimo} .',
                })
    # Salvando notificações na sessão
    request.session['notificacoes'] = notificacoes
    request.session['total_notificacoes'] = len(notificacoes)


@login_required(login_url='/')
def cria_movimento_de_estoque_em_lote(request):

    """
    Cria movimentos de estoque em lote (entrada, saída e transferência) para produtos.
    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo dados do formulário.
    Returns:
        HttpResponse: Redireciona para a visualização do estoque com mensagens de sucesso ou erro.
    """
    
    if request.method == 'POST':

        quantidades = request.POST.getlist('quantidades')
        movimentos = request.POST.getlist('movimentos')
        produto_ids = request.POST.getlist('produto_ids')
        loja_destino_id = request.POST.getlist('loja_destino_id')  # ID da loja que receberá os produtos
        produtos_alterados = []
        mensagem = []

        for indice in range(0, len(quantidades)):
            if quantidades[indice] == '':
                continue
            produto = get_object_or_404(Produto, id=produto_ids[indice], loja=request.user.loja)
            
            if movimentos[indice] == 'Saida':
                if produto.quantidade < float(quantidades[indice]):
                    mensagem.append(f'Quantidade insuficiente: {produto.nome}.\n')
                    continue
                else:
                    produto.quantidade -= float(quantidades[indice])
                    produto.save()
                    MovimentoEstoque.objects.create(
                        produto=produto,
                        tipo_movimento='saida',
                        quantidade=float(quantidades[indice]),
                        responsavel=request.user,
                        loja=request.user.loja
                    )
                    produtos_alterados.append(produto.nome)
            elif movimentos[indice] == 'Entrada':

                produto.quantidade += float(quantidades[indice])
                produto.save()
                MovimentoEstoque.objects.create(
                    produto=produto,
                    tipo_movimento='entrada',
                    quantidade=float(quantidades[indice]),
                    responsavel=request.user,
                    loja=request.user.loja
                )
                produtos_alterados.append(f'\n{produto.nome}')


            elif movimentos[indice] == 'Transferencia':
                if produto.quantidade < float(quantidades[indice]):
                    mensagem.append(f'Quantidade insuficiente para transferência: {produto.nome}.')
                    continue
                if not loja_destino_id[indice]:
                    mensagem.append(f'Loja destino não selecionada. Produto {produto.nome} não transferido.')
                    continue
                loja_destino = Loja.objects.get(id=loja_destino_id[indice])
                if not loja_destino:
                    mensagem.append(f'Loja destino não encontrada. Produto {produto.nome} não transferido.')
                    continue

                # Verificar se o produto já existe na loja de destino
                produto_destino = Produto.objects.filter(
                    codigo_de_barras=produto.codigo_de_barras, loja=loja_destino
                ).first()

                if not produto_destino:
                    # Criar categoria e fornecedor, se necessário
                    categoria, _ = Categoria.objects.get_or_create(nome=produto.categoria.nome, loja=loja_destino)
                    fornecedor, _ = Fornecedor.objects.get_or_create(nome=produto.fornecedor.nome, loja=loja_destino)
                    # Criar o produto na loja de destino
                    produto_destino = Produto.objects.create(
                        nome=produto.nome,
                        quantidade=0,  # Inicialmente zero, pois será atualizado depois
                        tipo_quantidade=produto.tipo_quantidade,
                        codigo_de_barras=produto.codigo_de_barras,
                        validade=produto.validade,
                        fornecedor=fornecedor,
                        categoria=categoria,
                        estoque_minimo=produto.estoque_minimo,
                        loja=loja_destino
                    )

                # Atualizar a quantidade no produto da loja de destino
                produto_destino.quantidade += float(quantidades[indice])
                produto_destino.save()

                # Criar movimentos de entrada na loja de destino e saída na loja de origem
                MovimentoEstoque.objects.create(
                    produto=produto_destino,
                    tipo_movimento='entrada',
                    quantidade=float(quantidades[indice]),
                    responsavel=request.user,
                    loja=loja_destino
                )
                MovimentoEstoque.objects.create(
                    produto=produto,
                    tipo_movimento='saida',
                    quantidade=float(quantidades[indice]),
                    responsavel=request.user,
                    loja=request.user.loja
                )

                # Atualizar a quantidade do produto na loja de origem
                produto.quantidade -= float(quantidades[indice])
                produto.save()
                produtos_alterados.append(f'{produto.nome}')
            
        if produtos_alterados:
            messages.success(request, f'Movimento de estoque registrado com sucesso para os produtos: {", ".join(produtos_alterados)}.')    
        elif mensagem:
            messages.error(request, f'{" ".join(mensagem)}')
        return redirect('estoqueview')
    



@csrf_exempt  # Desabilita a verificação CSRF para facilitar testes com Postman
def importar_dados_json(request):
    """
    Recebe um JSON e insere os dados no banco de dados.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    try:
        data = json.loads(request.body)

        # Criando Lojas
        for loja_data in data.get('lojas', []):
            loja, _ = Loja.objects.get_or_create(id=loja_data.get('id'), defaults={'nome': loja_data.get('nome')})

        # Criando Usuários e Associando às Lojas
        for user_loja in data.get('users_loja', []):
            user, _ = User.objects.get_or_create(username=user_loja.get('user__username'))
            loja = Loja.objects.get(nome=user_loja.get('loja__nome'))
            UserLoja.objects.get_or_create(user=user, loja=loja)

        # Criando Fornecedores
        for fornecedor_data in data.get('fornecedores', []):
            loja = Loja.objects.get(nome=fornecedor_data.get('loja__nome'))
            Fornecedor.objects.get_or_create(
                nome=fornecedor_data.get('nome'),
                contato=fornecedor_data.get('contato'),
                loja=loja
            )

        # Criando Categorias
        for categoria_data in data.get('categorias', []):
            loja = Loja.objects.get(nome=categoria_data.get('loja__nome'))
            Categoria.objects.get_or_create(nome=categoria_data.get('nome'), loja=loja)

        # Criando Produtos
        for produto_data in data.get('produtos', []):
            loja = Loja.objects.get(nome=produto_data.get('loja__nome'))
            fornecedor = Fornecedor.objects.filter(nome=produto_data.get('fornecedor__nome')).first()
            categoria = Categoria.objects.filter(nome=produto_data.get('categoria__nome')).first()

            Produto.objects.get_or_create(
                nome=produto_data.get('nome'),
                codigo_de_barras=produto_data.get('codigo_de_barras'),
                defaults={
                    'quantidade': produto_data.get('quantidade'),
                    'tipo_quantidade': produto_data.get('tipo_quantidade'),
                    'validade': produto_data.get('validade'),
                    'fornecedor': fornecedor,
                    'categoria': categoria,
                    'estoque_minimo': produto_data.get('estoque_minimo'),
                    'loja': loja,
                    'status': produto_data.get('status')
                }
            )

        # Criando Movimentos de Estoque
        for movimento_data in data.get('movimentos_estoque', []):
            produto = Produto.objects.get(nome=movimento_data.get('produto__nome'))
            loja = Loja.objects.get(nome=movimento_data.get('loja__nome'))
            responsavel = User.objects.get(username=movimento_data.get('responsavel__username'))

            MovimentoEstoque.objects.create(
                produto=produto,
                tipo_movimento=movimento_data.get('tipo_movimento'),
                quantidade=movimento_data.get('quantidade'),
                responsavel=responsavel,
                loja=loja
            )
        for usuario in data.get('usuarios', []):
            username = usuario.get('username')
            loja_id = usuario.get('loja')
            email = usuario.get('email', '')  # Garante que email não seja None
            first_name = usuario.get('first_name', '')
            last_name = usuario.get('last_name', '')
            senha = '123'
            if not username or not loja_id:
                continue
            try: 
                loja = Loja.objects.get(id=loja_id)
            except Loja.DoesNotExist:
                print('nao existe loja')
                continue
            user, created = User.objects.get_or_create(username=username, defaults={
                            "email": email,
                            "first_name": first_name,
                            "last_name": last_name,
                            "is_active": usuario.get("is_active", True),
                            "date_joined": usuario.get("date_joined"),
                        })
            if created:  # Se o usuário foi criado agora, define a senha padrão
                user.set_password("123")
                user.save()
            if hasattr(user, 'loja'):
                user.loja = loja
                user.save()
        return JsonResponse({'success': 'Dados importados com sucesso'}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

def error_404_view(request, exception):
    return render(request, '404.html', status=404)

def error_500_view(request):
    return render(request, '500.html', status=500)


def error_401_view(request, exception=None):
    return render(request, 'errors/401.html', status=401)



def obter_dados_banco(request):
    todas_tabelas = connection.introspection.table_names()
    dados_completos = {}

    for tabela in todas_tabelas:
        try:
            modelo = None
            for model in apps.get_models():
                if model._meta.db_table == tabela:
                    modelo = model
                    break

            if modelo:
                # Serializando os modelos do Django
                objetos = modelo.objects.all()
                dados_serializados = json.loads(serialize('json', objetos))
                dados_completos[tabela] = [obj["fields"] for obj in dados_serializados]
            else:
                # Se não tem modelo, faz consulta SQL bruta
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT * FROM {tabela}")  # Busca tudo da tabela
                    colunas = [desc[0] for desc in cursor.description]
                    dados_completos[tabela] = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        
        except Exception as e:
            print(f"Erro ao buscar dados da tabela {tabela}: {str(e)}")
    
    return JsonResponse(dados_completos, safe=False)


from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group, Permission

@transaction.atomic  # Garante que a operação seja atômica
@csrf_exempt  # Permite chamadas sem CSRF (para testes)
def restore_backup(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)  # Lê o JSON enviado na requisição

        with transaction.atomic():
            # Apaga todas as tabelas antes de inserir os novos dados
            for model in apps.get_models():
                model.objects.all().delete()

            # Percorre as tabelas e insere os registros novamente
            for tabela, registros in data.items():
                modelo = None
                for model in apps.get_models():
                    if model._meta.db_table == tabela:
                        modelo = model
                        break

                if modelo:
                    for registro in registros:
                        many_to_many_fields = {}
                        
                        # Separa campos ManyToMany para tratar depois
                        for field in modelo._meta.many_to_many:
                            if field.name in registro:
                                many_to_many_fields[field.name] = registro.pop(field.name)

                        # Resolver chave estrangeira ContentType na tabela Permission
                        if modelo == Permission and "content_type" in registro:
                            content_type_id = registro.pop("content_type")
                            registro["content_type"] = ContentType.objects.get(id=content_type_id)

                        # Cria o objeto sem os campos ManyToMany
                        obj = modelo.objects.create(**registro)

                        # Agora adiciona os valores nos campos ManyToMany
                        for field_name, values in many_to_many_fields.items():
                            many_to_many_field = getattr(obj, field_name)
                            many_to_many_field.set(values)  # Usa `.set()`, como o Django exige

        return JsonResponse({"mensagem": "Banco de dados restaurado com sucesso!"})

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)