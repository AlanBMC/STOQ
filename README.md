# Controle de Estoque com Django e PWA

![Logo do Projeto](insira-link-ou-caminho-da-logo-aqui)

Este projeto implementa um sistema de controle de estoque utilizando Django, com suporte a Progressive Web App (PWA) para garantir acessibilidade offline e uma experiência de aplicativo nativa.

## Recursos Principais

### Funcionalidades Gerais

- **Autenticação de Usuários**: Suporte a login, logout e gerenciamento de sessões.
- **Gestão de Produtos**: Criação, edição, exclusão e listagem de produtos.
- **Gestão de Categorias**: Criação, edição, exclusão e listagem de categorias de produtos.
- **Gestão de Fornecedores**: Criação, edição, exclusão e listagem de fornecedores.
- **Movimentação de Estoque**: Registro de entrada, saída e transferência de produtos.
- **Notificações**: Alertas automáticos para produtos com estoque baixo ou próximos do vencimento.

### Progressive Web App (PWA)



- Instalação do sistema como aplicativo em dispositivos móveis e desktops.

### Dashboard

- Visualização de movimentações de estoque por categoria, fornecedor e produto.
- Exibição de métricas como quantidade total, movimentações e alertas de estoque.

## Estrutura do Projeto

### Modelos Utilizados

1. **Loja**: Identificação da loja.
2. **Categoria**: Organização de produtos.
3. **Fornecedor**: Registro de fornecedores.
4. **Produto**: Detalhamento de produtos (nome, quantidade, validade, etc.).
5. **MovimentoEstoque**: Registro de movimentações de entrada, saída e transferência.

### Views Principais

#### Dashboard

- **Endpoint**: `/dashboard`
- **Descrição**: Exibe as principais métricas do estoque e movimentações.

#### Login e Logout

- **Endpoints**: `/login`, `/logout`
- **Descrição**: Gerencia autenticação e encerramento de sessões.

#### Gestão de Produtos

- **Endpoints**: `/produtoview`, `/criar_produto`, `/editar_produto`, `/excluir_produto`
- **Descrição**: Manipula o CRUD de produtos.

#### Gestão de Categorias

- **Endpoints**: `/listar_categorias`, `/criar_categoria`, `/editar_categoria`, `/excluir_categoria`
- **Descrição**: Manipula o CRUD de categorias.

#### Gestão de Fornecedores

- **Endpoints**: `/listar_fornecedores`, `/criar_fornecedor`, `/editar_fornecedor`, `/excluir_fornecedor`
- **Descrição**: Manipula o CRUD de fornecedores.

#### Movimentação de Estoque

- **Endpoint**: `/cria_movimento_de_estoque_em_lote`
- **Descrição**: Registra entradas, saídas e transferências de produtos entre lojas.

#### Notificações

- **Função**: `func_notifica_vencimento`
- **Descrição**: Gera alertas para:
  - Produtos com validade próxima (14, 30 ou 60 dias).
  - Produtos com estoque abaixo do mínimo.

#### Páginas Offline

- **Endpoint**: `/offline`
- **Descrição**: Renderiza uma página amigável quando o sistema é acessado sem conexão.

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

*(Insira a imagem ou link do diagrama gerado aqui)*

## Design

O design do sistema é responsivo e otimizado para dispositivos móveis e desktops, utilizando o seguinte:

- **HTML5**
- **CSS3**
- **Bootstrap ou Tailwind (se aplicável)**
- **Templates Django**

*(Adicione imagens ou capturas de tela do design do sistema aqui)*

## Licença

Este projeto está licenciado sob a Licença MIT. Consulte o arquivo LICENSE para mais detalhes.

---

### Contato

Se tiver dúvidas ou sugestões, entre em contato pelo e-mail: [seuemail@exemplo.com](mailto\:seuemail@exemplo.com).

**Sua Foto**:
*(Insira sua foto aqui ou um link para uma imagem de perfil)*

