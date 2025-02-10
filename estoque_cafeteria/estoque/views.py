from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .models import Loja,Categoria, Produto, MovimentoEstoque, UserLoja  
from django.contrib.auth import logout,authenticate, update_session_auth_hash
from django.contrib.auth import login as login_django
from datetime import date, timedelta
from django.http import HttpResponseNotAllowed, HttpResponse
from django.views.decorators.csrf import csrf_exempt



def obter_dados(request):
    '''
    Obter dados para o dashboard
    '''
    # Pegar todas as categorias
    loja = Loja.objects.get(id=request.user.loja.id)
    categorias = Categoria.objects.filter(loja=loja)
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
        "total_mov_produto": total_mov_produto,
        "contagemproduto": contagemporproduto
    })


    

    
def verifica_last_name(request):
    user =  request.user
    if user.last_name == '':
        return True
    elif user.last_name == 'tour 2':
        return True
    else:
        return False

def retira_tour(request):
    if request.method == 'POST':

        return redirect('produtoview')

@login_required(login_url='/')
def dashboard(request):
    show_tour = verifica_last_name(request)
    loja_name = request.user.loja.nome
    loja_logo = request.user.loja.logo
    
    return render(request, 'dashboard.html', {'logo': loja_logo,'loja': loja_name,'show_tour': False})

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
      Renderiza a página de visualização de produtos com a lista de categorias, nome da loja e a data de hoje.
        request (HttpRequest): O objeto de requisição HTTP.
        HttpResponse: A página de visualização de produtos renderizada.
    """
    
    show_tour = verifica_last_name(request)
    categorias =  listar_categorias(request)
    loja_name = request.user.loja.nome
    lojas = UserLoja.objects.filter(user=request.user)
    lojasDoUser = [user.loja for user in lojas]
    is_proprietario = request.user.groups.filter(name="Proprietario").exists()
    loja_logo = request.user.loja.logo
    hoje = date.today()
    return render(request, 'produtoview.html', {'logo': loja_logo,'is_proprietario':is_proprietario,'lojasDoUser': lojasDoUser,'show_tour': False, 'loja': loja_name, 'categorias': categorias,  'today': hoje})

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
    Renderiza a página de estoque com a lista de produtos, categorias e a data de hoje.
    Argumentos: request (HttpRequest): O objeto de requisição HTTP.
    Retorna: HttpResponse: estoque.html com os seguites parâmetros: categorias , produtos e today.
    '''
    produtos =  listar_produtos(request)
    categorias =  listar_categorias(request)
    loja_logo = request.user.loja.logo
    lojas2 = UserLoja.objects.filter(user=request.user)
    lojasDoUser = [user.loja for user in lojas2]
    loja_name = request.user.loja.nome
    #Criar um novo Grupo
   
    
    hoje = date.today()
    
    return render(request, 'estoque.html', {'logo': loja_logo,'loja': loja_name,'show_tour': False,'categorias': categorias,'produtos': produtos, 'today': hoje,'lojas':lojasDoUser})

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
    loja_name = request.user.loja.nome
    loja_logo = request.user.loja.logo
    is_proprietario = request.user.groups.filter(name="Proprietario").exists()
    
    return render(request, 'configuracao.html', {'is_proprietario':is_proprietario,'logo': loja_logo,'loja': loja_name,'show_tour': False,'usuarios': usuarios, 'is_proprietario': is_proprietario})


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
                userloja = UserLoja.objects.create(user=user, loja=loja)
                userloja.save()
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
        validade = request.POST.get('validade')
        categoria_id = request.POST.get('Categoria')
        estoque_min = request.POST.get('estoque_min')
        
        # Verifica se o produto já existe na mesma loja
        if Produto.objects.filter(nome=nome, loja=request.user.loja).exists():
            messages.error(request, 'Produto com esse nome já existe.')
            return redirect('produtoview')
      
        # Criação do novo produto
        Produto.objects.create(
            nome=nome,
            quantidade=quantidade,
            tipo_quantidade=tipo_quantidade,
            validade=validade,
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
        validade = request.POST.get('validade')
        categoria_id = request.POST.get('Categoria')
        estoquemin = request.POST.get('estoque_min')
        # Evita duplicidade ao editar (exclui o próprio produto da verificação)
        if Produto.objects.filter(nome=nome, loja=request.user.loja).exclude(pk=produto_id).exists():
            messages.error(request, 'Já existe um produto com esse nome.')
            return redirect('estoqueview')
        elif Produto.objects.filter(loja=request.user.loja).exclude(pk=produto_id).exists():
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
        if validade:
            produto.validade = validade
        if estoquemin:
            
            produto.estoque_minimo = estoquemin
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
            if movimentos[indice] == 'Estoque_atual':
                quantidade_atual =  float(quantidades[indice]) - produto.quantidade 
                if quantidade_atual > 0:
                    print('entrada - ',quantidade_atual)
                    produto.quantidade = float(quantidades[indice])
                    produto.save()
                    MovimentoEstoque.objects.create(
                        produto=produto,
                        tipo_movimento='entrada',
                        quantidade=quantidade_atual,
                        responsavel=request.user,
                        loja=request.user.loja
                    )
                    produtos_alterados.append(f'\n{produto.nome}')

                elif quantidade_atual < 0:
                    print('saida - ', quantidade_atual)
                    if produto.quantidade < float(quantidades[indice]):
                        mensagem.append(f'Quantidade insuficiente: {produto.nome}.\n')
                        continue
                    else:
                        produto.quantidade += quantidade_atual
                        produto.save()
                        
                        MovimentoEstoque.objects.create(
                            produto=produto,
                            tipo_movimento='saida',
                            quantidade=quantidade_atual * -1 ,
                            responsavel=request.user,
                            loja=request.user.loja
                        )
                        produtos_alterados.append(produto.nome)
                
                
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
                produto_destino = Produto.objects.filter(nome=produto.nome, loja=loja_destino).first()

                if not produto_destino:
                    # Criar categoria, se necessário
                    categoria, _ = Categoria.objects.get_or_create(nome=produto.categoria.nome, loja=loja_destino)
                    # Criar o produto na loja de destino
                    produto_destino = Produto.objects.create(
                        nome=produto.nome,
                        quantidade=0,  # Inicialmente zero, pois será atualizado depois
                        tipo_quantidade=produto.tipo_quantidade,
                        validade=produto.validade,
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
    

def error_404_view(request, exception):
    return render(request, '404.html', status=404)

def error_500_view(request):
    return render(request, '500.html', status=500)


def error_401_view(request, exception=None):
    return render(request, 'errors/401.html', status=401)


@login_required(login_url='/')
def retornadados(request):
    """
    Retorna os dados do banco de dados em formato JSON.
    """
    lojas = Loja.objects.all().values()
    users_loja = UserLoja.objects.select_related('user', 'loja').values('user__username', 'loja__nome')
    categorias = Categoria.objects.select_related('loja').values('nome', 'loja__nome')
    produtos = Produto.objects.select_related( 'categoria', 'loja').values(
        'nome', 'quantidade', 'tipo_quantidade', 'validade'
        , 'categoria__nome', 'estoque_minimo', 'loja__nome', 
    )
    movimentos = MovimentoEstoque.objects.select_related('produto', 'responsavel', 'loja').values(
        'produto__nome', 'tipo_movimento', 'quantidade', 'data_movimento', 'responsavel__username', 'loja__nome'
    )
    data = {
        'lojas': list(lojas),
        'users_loja': list(users_loja),
        'categorias': list(categorias),
        'produtos': list(produtos),
        'movimentos_estoque': list(movimentos),
    }
    return JsonResponse(data, safe=False)

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
   
        # Criando Categorias
        for categoria_data in data.get('categorias', []):
            loja = Loja.objects.get(nome=categoria_data.get('loja__nome'))
            Categoria.objects.get_or_create(nome=categoria_data.get('nome'), loja=loja)
        # Criando Produtos
        for produto_data in data.get('produtos', []):
            loja = Loja.objects.get(nome=produto_data.get('loja__nome'))
            categoria = Categoria.objects.filter(nome=produto_data.get('categoria__nome')).first()
            Produto.objects.get_or_create(
                nome=produto_data.get('nome'),
              
                defaults={
                    'quantidade': produto_data.get('quantidade'),
                    'tipo_quantidade': produto_data.get('tipo_quantidade'),
                    'validade': produto_data.get('validade'),
                 
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
        return JsonResponse({'success': 'Dados importados com sucesso'}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required(login_url='/')
def download_json(request):
    """
    Gera  um arquivo JSON para download com os dados retornados por `retornadados`.
    """
    if request.user.groups.filter(name='Desenvolvedor').exists():
        response_data = retornadados(request).content  # Obtém os dados da função retornadados
        response = HttpResponse(response_data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="dados.json"'
        return response
    else:
        messages.error(request, 'Voce precisa ser desenvolvedor')
        return redirect('produtoview')

def cadastroUserLoja(request):
    """
    Função para cadastrar um usuário proprietário de uma loja.
    Args:
        request (HttpRequest): Objeto HttpRequest que contém os dados da requisição.
    Returns:
        HttpResponse: Redireciona para a página de login em caso de sucesso ou para a página de cadastro em caso de erro.
    Fluxo:
        - Se o método da requisição for POST:
            - Obtém os dados do formulário (nome, email, senha, confirmação de senha, nome da loja e logo da loja).
            - Verifica se a senha e a confirmação de senha coincidem.
            - Verifica se o arquivo enviado é uma imagem.
            - Verifica se o nome de usuário já existe.
            - Cria a loja e o usuário, associa o usuário ao grupo 'Proprietario' e salva os dados.
            - Exibe uma mensagem de sucesso e redireciona para a página de login.
            - Em caso de erro, exibe uma mensagem de erro e redireciona para a página de cadastro.
        - Se o método da requisição for GET:
            - Renderiza a página de cadastro de usuário.
    """

    if request.method == 'POST':
        nome =  request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        senha_confirma = request.POST.get('confirmasenha')
        loja_nome = request.POST.get('loja')
        logo_loja =  request.FILES.get('logo-loja')
        if senha == senha_confirma:
            
            if logo_loja:
                # Verifica se o arquivo é uma imagem
                if not logo_loja.content_type.startswith('image/'):
                    messages.error(request, 'O arquivo enviado não é uma imagem ou um arquivo valido')
                    return redirect('cadastra-user-loja')
                else:
                    grupo_proprietario = Group.objects.get(name='Proprietario')
                    if not User.objects.filter(username=nome).exists():
                        loja = Loja.objects.create(nome=loja_nome, logo=logo_loja)
                        user = User.objects.create_user(username= nome,email=email, password= senha, loja=loja)

                        user.groups.add(grupo_proprietario)
                        user.save()
                        userloja = UserLoja.objects.create(user=user, loja=loja)
                        userloja.save()
                        messages.success(request,'Cadastro concluido')
                        return redirect('login')
            else:
                messages.error(request, 'Loja sem logo')
                return redirect('cadastra-user-loja')
        else:
            messages.error(request, 'Senhas não coincidem')
            return redirect('cadastra-user-loja')
        return redirect('cadastra-user-loja')
    if request.method == 'GET':
        return render(request,'cadastra_user.html')

@login_required(login_url='/')
def criaLoja(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        logo_loja = request.FILES.get('logo')
        if logo_loja:
            # Verifica se o arquivo é uma imagem
            if not logo_loja.content_type.startswith('image/'):
                messages.error(request, 'O arquivo enviado não é uma imagem ou um arquivo valido')
                return redirect('produtoview')
            else:
                loja = Loja.objects.create(nome=nome, logo=logo_loja)
                userloja = UserLoja.objects.create(user=request.user, loja=loja)
                userloja.save()
                loja.save()
                messages.success(request, 'loja criada com sucesso')
                return redirect('produtoview')
        messages.error(request, 'Insira uma imagem')
        return redirect('produtoview')

@login_required(login_url='/')
def atualizaLoja(request):
    if not request.user.has_perm('auth.add_user'):
        messages.error(request, 'Você não tem permissão para criar ou editar lojas.')
        return redirect('configuracaoview')  # Redireciona para uma página de erro ou home

    if request.method == 'POST':
        box = request.POST.get('checkbox')
        nome = request.POST.get('nome')
        logo_loja = request.FILES.get('logo-loja')
        
        if box:
            if logo_loja:
            # Verifica se o arquivo é uma imagem
                if not logo_loja.content_type.startswith('image/'):
                    messages.error(request, 'O arquivo enviado não é uma imagem ou um arquivo valido')
                    return redirect('configuracaoview')
                else:
                    if Loja.objects.filter(nome=nome).exists():
                        messages.error(request, 'Já existe uma loja com esse nome.')
                        return redirect('configuracaoview')
                    else:
                        loja = Loja.objects.create(nome=nome, logo=logo_loja)
                        userloja = UserLoja.objects.create(user=request.user, loja=loja)
                        userloja.save()
                        loja.save()
                        messages.success(request, 'loja criada com sucesso')
                        return redirect('configuracaoview')
            messages.error(request, 'Insira uma imagem')
            return redirect('configuracaoview')
        else:
            if logo_loja:
                # Verifica se o arquivo é uma imagem
                if not logo_loja.content_type.startswith('image/'):
                    messages.error(request, 'O arquivo enviado não é uma imagem ou um arquivo valido')
                    return redirect('configuracaoview')
                else:
                    loja =  get_object_or_404(Loja, id= request.user.loja.id)
                    loja.logo = logo_loja
                    if nome:
                        loja.nome = nome
                    loja.save()
                    messages.success(request, 'Loja atualiza com sucesso')
                    return redirect('configuracaoview')
            else:
                loja =  get_object_or_404(Loja, id= request.user.loja.id)
                
                loja.nome = nome
                loja.save()
                messages.success(request, 'Nome atualizado')
                return redirect('configuracaoview')
        
