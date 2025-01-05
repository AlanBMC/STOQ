from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .models import Loja,Categoria,Fornecedor, Produto
from django.contrib.auth import logout,authenticate, update_session_auth_hash
from django.contrib.auth import login as login_django
from datetime import date, timedelta
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
    categorias =  listar_categorias(request)
    fornecedores = listar_fornecedores(request)
    hoje = date.today()
    return render(request, 'produtoview.html', {'categorias': categorias, 'fornecedores': fornecedores, 'today': hoje})

@login_required(login_url='/')
def estoqueview(request):
  
    return render(request, 'estoque.html')

def offline(request):
    return render(request, 'offline.html')


@login_required(login_url='/')
def configuracaoview(request):
    usuarios =listar_usuarios_da_loja_atual(request)
    is_proprietario = request.user.groups.filter(name='Proprietario').exists()   
    return render(request, 'configuracao.html', {'usuarios': usuarios, 'is_proprietario': is_proprietario
})


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

@login_required
def listar_fornecedores(request):
    fornecedores = Fornecedor.objects.filter(loja=request.user.loja)
    return fornecedores

@login_required
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


@login_required
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

@login_required
def excluir_fornecedor(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk, loja=request.user.loja)
    
    if request.method == 'POST':
        fornecedor.delete()
        messages.success(request, 'Fornecedor excluído com sucesso.')
        return redirect('produtoview')

    return redirect('produtoview')

@login_required
def listar_produtos(request):
    produtos = Produto.objects.filter(loja=request.user.loja)
    return produtos


@login_required
def criar_produto(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        quantidade = request.POST.get('quantidade')
        tipo_quantidade = request.POST.get('tipo_quantidade')
        codigo_de_barras = request.POST.get('codigo_de_barras')
        validade = request.POST.get('validade')
        fornecedor_id = request.POST.get('Fornecedor')
        categoria_id = request.POST.get('Categoria')

        # Verifica se o produto já existe na mesma loja
        if Produto.objects.filter(nome=nome, loja=request.user.loja).exists():
            messages.error(request, 'Produto com esse nome já existe.')
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
            loja=request.user.loja
        )
        messages.success(request, 'Produto criado com sucesso.')
        return redirect('produtoview')

    return redirect('produtoview')


@login_required
def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk, loja=request.user.loja)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        quantidade = request.POST.get('quantidade')
        tipo_quantidade = request.POST.get('tipo_quantidade')
        codigo_de_barras = request.POST.get('codigo_de_barras')
        validade = request.POST.get('validade')
        fornecedor_id = request.POST.get('fornecedor')
        categoria_id = request.POST.get('categoria')

        # Evita duplicidade ao editar (exclui o próprio produto da verificação)
        if Produto.objects.filter(nome=nome, loja=request.user.loja).exclude(pk=pk).exists():
            messages.error(request, 'Já existe um produto com esse nome.')
            return redirect('produtoview')

        # Atualização do produto
        produto.nome = nome
        produto.quantidade = quantidade
        produto.tipo_quantidade = tipo_quantidade
        produto.codigo_de_barras = codigo_de_barras
        produto.validade = validade
        produto.fornecedor_id = fornecedor_id
        produto.categoria_id = categoria_id
        produto.save()

        messages.success(request, 'Produto atualizado com sucesso.')
        return redirect('produtoview')

    return redirect('produtoview')


@login_required
def excluir_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk, loja=request.user.loja)
    
    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto excluído com sucesso.')
        return redirect('produtoview')

    return redirect('produtoview')