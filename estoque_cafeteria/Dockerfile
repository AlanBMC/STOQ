# Usar uma imagem base com Python
FROM python:3.11-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar o arquivo de dependências
COPY requirements.txt /app

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código do projeto para dentro do container
COPY . /app

# Expor a porta que o Waitress/Django usará
EXPOSE 8000

# Comando para rodar o servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
