# Controle de Estoque com Django e PWA


<img src="maskable_icon (1).png"  width="150px"></br> 
Este projeto implementa um sistema de controle de estoque utilizando Django, com suporte a Progressive Web App (PWA) para garantir uma experiência de aplicativo nativa.

## Recursos Principais

### Funcionalidades Gerais

- **Autenticação de Usuários**: Suporte a login, logout e gerenciamento de sessões, group do django.
- **Gestão de Produtos**: Criação, edição, exclusão e listagem de produtos.
- **Gestão de Categorias**: Criação, edição, exclusão e listagem de categorias de produtos.
- **Gestão de Fornecedores**: Criação, edição, exclusão e listagem de fornecedores.
- **Movimentação de Estoque**: Registro de entrada, saída e transferência de produtos.
- **Notificações**: Alertas automáticos para produtos com estoque baixo ou próximos do vencimento.
- **Transitar entre lojas**: O usuário pode criar lojas (filias) e trasitar entre elas, cada uma com seus proprios funcionarios e produtos.
- **Backup**: O sistema tem uma rota para backup `<localhost>/api/backup/download/dados`

  
### Progressive Web App (PWA)

- Instalação do sistema como aplicativo em dispositivos móveis e desktops.

### Dashboard

- Visualização de movimentações de estoque por categoria, fornecedor e produto.
- Exibição de métricas como quantidade total, movimentações e alertas (Dentro do proprio sistema) de estoque.

## Estrutura do Projeto

### Modelos Utilizados

1. **Loja**: Identificação da loja.
2. **Categoria**: Organização de produtos.
3. **Fornecedor**: Registro de fornecedores.
4. **Produto**: Detalhamento de produtos (nome, quantidade, validade, etc.).
5. **MovimentoEstoque**: Registro de movimentações de entrada, saída e transferência.
6. **User**: Usuario do proprio Django
7. **UserLoja**: Relação entre Loja e Usuario
   
### Views Principais

#### Dashboard

- **Endpoint**: `/dashboard`
- **Descrição**: Exibe as principais métricas do estoque e movimentações.

<div style="display: flex;"> 
   <img src="mobile-dashboard.png" alt="Imagem 1" width="150px" style="margin-right: 10px;"> 
   <img src="desktop-tablet-dashboard.png" alt="Imagem 2" width="617px"> 
</div>


#### Login e Logout

- **Endpoints**: `/login`, `/logout`
- **Descrição**: Gerencia autenticação e encerramento de sessões.
<div style="display: flex;"> 
   <img src="mobile-login.png" alt="Imagem 1" width="150px" style="margin-right: 10px;"> 
   <img src="desktop-tablet-login.png" alt="Imagem 2" width="600px"> 
</div>

#### Gestão de Produtos

- **Endpoints**: `/produtoview`, `/criar_produto`, `/editar_produto`, `/excluir_produto`
- **Descrição**: Manipula o CRUD de produtos.


#### Gestão de Categorias

- **Endpoints**: `/listar_categorias`, `/criar_categoria`, `/editar_categoria`, `/excluir_categoria`
- **Descrição**: Manipula o CRUD de categorias.

#### Gestão de Fornecedores

- **Endpoints**: `/listar_fornecedores`, `/criar_fornecedor`, `/editar_fornecedor`, `/excluir_fornecedor`
- **Descrição**: Manipula o CRUD de fornecedores.
  
<div style="display: flex;"> 
   <img src="mobile-produto.png" alt="Imagem 1" width="150px" style="margin-right: 10px;"> 
   <img src="desktop-tablet-produto.png" alt="Imagem 2" width="617px"> 
</div>

#### Movimentação de Estoque

- **Endpoint**: `/cria_movimento_de_estoque_em_lote`
- **Descrição**: Registra entradas, saídas e transferências de produtos entre lojas.

<div style="display: flex;"> 
   <img src="mobile-estoque.png" alt="Imagem 1" width="150px" style="margin-right: 10px;"> 
   <img src="desktop-tablet-estoque.png" alt="Imagem 2" width="617px"> 
</div>


#### Cadastro Loja-User

- **Função**: `cadastroUserLoja`
- **Descrição**: Função para cadastrar um usuário proprietário de uma loja:
  - Cadastro de Usuario e Loja. O usuario cadastro desta maneira pertece ao grupo de proprietario.

<div style="display: flex;"> 
   <img src="mobile-alerta.png" alt="Imagem 1" width="150px" style="margin-right: 10px;"> 
   <img src="desktop-tablet-alerta.png" alt="Imagem 2" width="617px"> 
</div>

#### Notificações

- **Função**: `func_notifica_vencimento`
- **Descrição**: Gera alertas para:
  - Produtos com validade próxima (14, 30 ou 60 dias).
  - Produtos com estoque abaixo do mínimo.
<div style="display: flex;"> 
   <img src="mobile-alerta.png" alt="Imagem 1" width="150px" style="margin-right: 10px;"> 
   <img src="desktop-tablet-alerta.png" alt="Imagem 2" width="617px"> 
</div>

## Pré-requisitos

- **Python 3.8+**
- **Django 4.x**
- **SQLite**
- **Django PWA**

## Instalação

1. Clone o repositório:

   ```bash
   git clone <url-do-repositorio>
   cd <nome-do-projeto>
   ```

2. Crie um ambiente virtual e ative-o:

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Aplique as migrações:

   ```bash
   python manage.py migrate
   ```

5. Inicie o servidor de desenvolvimento:

   ```bash
   python manage.py runserver
   ```

6. Acesse o sistema em [http://localhost:8000](http://localhost:8000).

## Modelagem Lógica

Abaixo está o diagrama de modelagem lógica do sistema:

*irei colocar imagens aqui*

## Design

O design do sistema é responsivo e otimizado para dispositivos móveis e desktops, utilizando o seguinte:

- **HTML5**
- **CSS3**
- **Bootstrap ou Tailwind (se aplicável)**
- **Templates Django**





## Sobre o autor

<!-- Coloque seu nome, uma foto sua e uma pequena bio sobre você na seguinte tabela: -->
|  |  |
|:-------------:|:------------------------------------------------------------:|
|  <img src="EU2.jpg" width="150px"></br> **Alan Bruno Morais Costa** | 
Me chamo Alan, sou estudante de Ciências da Computação na Universidade Federal de Mato Grosso (UFMT) e estou participando de um curso oferecido pela Cyber-edux. Neste repositório, apresento o Cardy, um sistema inovador de gerenciamento de tarefas e estudos projetado para melhorar a organização e eficiência de estudantes e profissionais.  |

- **Email:** alanbrunomoraescosta18@hotmail.com
- **LinkedIn:** [Alan's LinkedIn](https://www.linkedin.com/in/alan-morais-4861322b0)

