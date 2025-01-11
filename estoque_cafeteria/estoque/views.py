from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .models import Loja,Categoria,Fornecedor, Produto, MovimentoEstoque
from django.contrib.auth import logout,authenticate, update_session_auth_hash
from django.contrib.auth import login as login_django
from datetime import date, timedelta
from django.http import HttpResponseNotAllowed, HttpResponse
from django.core.mail import send_mail
from validate_email import validate_email




def obter_dados(request):
    # Pegar todas as categorias
    loja = Loja.objects.get(id=request.user.loja.id)
    categorias = Categoria.objects.filter(loja=loja)
    fornecedores = Fornecedor.objects.filter(loja=loja)
    produtos = Produto.objects.filter(loja=loja)
    movimentodeestoque = MovimentoEstoque.objects.filter(loja=loja)

    # Dados para movimentações
    total_mov_categoria = {
        categoria.nome: sum(
            mov.quantidade for mov in movimentodeestoque if mov.produto.categoria == categoria
        )
        for categoria in categorias
    }

    total_mov_fornecedor = {
        fornecedor.nome: sum(
            mov.quantidade for mov in movimentodeestoque if mov.produto.fornecedor == fornecedor
        )
        for fornecedor in fornecedores
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
    })


def dashboard(request):
    return render(request, 'dashboard.html')

def login(request):
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
    categorias =  listar_categorias(request)
    fornecedores = listar_fornecedores(request)
    loja_name = request.user.loja.nome
    hoje = date.today()
    return render(request, 'produtoview.html', {'loja': loja_name, 'categorias': categorias, 'fornecedores': fornecedores, 'today': hoje})

@login_required(login_url='/')
def estoqueview(request):
    produtos =  listar_produtos(request)
    categorias =  listar_categorias(request)
    lojas = Loja.objects.all()
    fornecedores = listar_fornecedores(request)
    hoje = date.today()
    return render(request, 'estoque.html', {'categorias': categorias, 'fornecedores': fornecedores,'produtos': produtos, 'today': hoje,'lojas':lojas})

def offline(request):
    return render(request, 'offline.html')


@login_required(login_url='/')
def configuracaoview(request):
    
    usuarios =listar_usuarios_da_loja_atual(request)
    is_proprietario = request.user.groups.filter(name='Proprietario').exists()   
    
    return render(request, 'configuracao.html', {'usuarios': usuarios, 'is_proprietario': is_proprietario})


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
        loja = Loja.objects.get(id=1)
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
    

@login_required(login_url='/')
def editar_nome_user(request):
    '''
    Edita nome do usuario
    '''
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
    categoria = get_object_or_404(Categoria, pk=pk, loja=request.user.loja)

    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso.')
        return redirect('produtoview')

    return redirect('produtoview')


@login_required(login_url='/')
def listar_categorias(request):
    categorias = Categoria.objects.filter(loja=request.user.loja)
    return categorias

@login_required(login_url='/')
def listar_fornecedores(request):
    fornecedores = Fornecedor.objects.filter(loja=request.user.loja)
    return fornecedores

@login_required(login_url='/')
def criar_fornecedor(request):
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
    fornecedor = get_object_or_404(Fornecedor, pk=pk, loja=request.user.loja)
    
    if request.method == 'POST':
        fornecedor.delete()
        messages.success(request, 'Fornecedor excluído com sucesso.')
        return redirect('produtoview')

    return redirect('produtoview')

@login_required(login_url='/')
def listar_produtos(request):
    produtos = Produto.objects.filter(loja=request.user.loja)
    return produtos


@login_required(login_url='/')
def criar_produto(request):
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
            print(estoquemin)
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
def cria_movimento_de_estoque(request):
    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        tipo_movimento = request.POST.get('tipo_movimento')
        quantidade = request.POST.get('quantidade')
        status = request.POST.get('status')
        
        # Converte a quantidade para float (aceita decimais)
        try:
            quantidade = float(quantidade)
        except ValueError:
            messages.error(request, 'A quantidade deve ser um número válido.')
            return redirect('estoqueview')
        
        # Busca o produto vinculado à loja do usuário
        produto = get_object_or_404(Produto, id=produto_id, loja=request.user.loja)
        produto.status = status
        
        try:
            # Lógica para entrada de produtos
            if tipo_movimento == 'Entrada':
                if quantidade <= 0:
                    messages.error(request, 'A quantidade de entrada deve ser maior que zero.')
                    return redirect('estoqueview')
                
                produto.quantidade += quantidade
                produto.save()
                MovimentoEstoque.objects.create(
                    produto=produto,
                    tipo_movimento=tipo_movimento,
                    quantidade=quantidade,
                    responsavel=request.user,
                    loja=request.user.loja
                )
                messages.success(request, 'Entrada de estoque registrada com sucesso.')
                return redirect('estoqueview')
            
            # Lógica para saída de produtos
            elif tipo_movimento == 'Saida':
                if produto.quantidade < quantidade:
                    messages.error(request, 'Quantidade insuficiente para saída.')
                    return redirect('estoqueview')
                
                produto.quantidade -= quantidade
                produto.save()
                MovimentoEstoque.objects.create(
                    produto=produto,
                    tipo_movimento=tipo_movimento,
                    quantidade=quantidade,
                    responsavel=request.user,
                    loja=request.user.loja
                )
                messages.success(request, 'Saída de estoque registrada com sucesso.')
                return redirect('estoqueview')

            else:
                messages.error(request, 'Tipo de movimento inválido.')
                return redirect('estoqueview')
        
        except Exception as e:
            messages.error(request, f'Ocorreu um erro: {str(e)}')
            return redirect('estoqueview')
        

@login_required(login_url='/')
def cria_movimento_de_estoque_em_lote(request):
    if request.method == 'POST':
        quantidades = request.POST.getlist('quantidades')
        movimentos = request.POST.getlist('movimentos')
        produto_ids = request.POST.getlist('produto_ids')

        produtos_alterados = []

        for produto_id, quantidade, tipo_movimento in zip(produto_ids, quantidades, movimentos):
            # Converte a quantidade para float (aceita decimais)
            try:
                quantidade = float(quantidade)
            except ValueError:
                messages.error(request, 'A quantidade deve ser um número válido.')
                return redirect('estoqueview')

            # Busca o produto vinculado à loja do usuário
            produto = get_object_or_404(Produto, id=produto_id, loja=request.user.loja)

            if quantidade == 0:
                continue

            try:
                # Lógica para entrada de produtos
                if tipo_movimento == 'Entrada':
                    if quantidade <= 0:
                        messages.error(request, 'A quantidade de entrada deve ser maior que zero.')
                        return redirect('estoqueview')

                    produto.quantidade += quantidade
                    produto.save()
                    MovimentoEstoque.objects.create(
                        produto=produto,
                        tipo_movimento=tipo_movimento,
                        quantidade=quantidade,
                        responsavel=request.user,
                        loja=request.user.loja
                    )
                    produtos_alterados.append(produto.nome)

                # Lógica para saída de produtos
                elif tipo_movimento == 'Saida':
                    if produto.quantidade < quantidade:
                        messages.error(request, f'Quantidade insuficiente para saída do produto {produto.nome}.')
                        return redirect('estoqueview')

                    produto.quantidade -= quantidade
                    produto.save()
                    MovimentoEstoque.objects.create(
                        produto=produto,
                        tipo_movimento=tipo_movimento,
                        quantidade=quantidade,
                        responsavel=request.user,
                        loja=request.user.loja
                    )
                    produtos_alterados.append(produto.nome)

                else:
                    messages.error(request, 'Tipo de movimento inválido.')
                    return redirect('estoqueview')

            except Exception as e:
                messages.error(request, f'Ocorreu um erro com o produto {produto.nome}: {str(e)}')
                return redirect('estoqueview')

        if produtos_alterados:
            messages.success(request, f'Movimento de estoque registrado com sucesso para os produtos: {", ".join(produtos_alterados)}.')
        else:
            messages.info(request, 'Nenhum movimento de estoque foi registrado.')

        return redirect('estoqueview')

    return redirect('estoqueview')

@login_required(login_url='/')
def cria_movimento_de_estoque_em_lote2(request):
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

                loja_destino = Loja.objects.get(id=loja_destino_id[indice])
                print(loja_destino)
                if not loja_destino:
                    mensagem.append(f'Loja destino não encontrada. Produto {produto.nome} não transferido.')
                    continue

                # Verificar se o produto já existe na loja de destino
                produto_destino = Produto.objects.filter(
                    codigo_de_barras=produto.codigo_de_barras, loja=loja_destino
                ).first()

                if not produto_destino:
                    # Criar categoria e fornecedor, se necessário
                    categoria, _ = Categoria.objects.get_or_create(nome='Transferência', loja=loja_destino)
                    fornecedor, _ = Fornecedor.objects.get_or_create(nome='Transferência', loja=loja_destino)
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