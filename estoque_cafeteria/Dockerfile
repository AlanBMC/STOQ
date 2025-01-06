# Usar uma imagem base com Python
FROM python:3.11-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos do projeto para o container
COPY . /app

# Instalar as dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expor a porta que o Waitress usará
EXPOSE 8000

# Comando para iniciar o servidor com Waitress
CMD ["waitress-serve", "--port=8000", "estoque_cafeteria.wsgi:application"]
