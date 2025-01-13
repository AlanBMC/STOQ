import json
from django.core.management.base import BaseCommand
from estoque.models import Produto, Fornecedor, Categoria, Loja

class Command(BaseCommand):
    help = 'Recria os produtos a partir de um arquivo JSON'

    def handle(self, *args, **kwargs):
        with open('estoque/data/produtos.json', 'r') as file:
            produtos_list = json.load(file)

        for produto_data in produtos_list:
            fornecedor = Fornecedor.objects.get(nome=produto_data['fornecedor']) if produto_data['fornecedor'] else None
            categoria = Categoria.objects.get(nome=produto_data['categoria']) if produto_data['categoria'] else None
            loja = Loja.objects.get(nome=produto_data['loja'])

            Produto.objects.create(
                nome=produto_data['nome'],
                quantidade=produto_data['quantidade'],
                tipo_quantidade=produto_data['tipo_quantidade'],
                codigo_de_barras=produto_data['codigo_de_barras'],
                validade=produto_data['validade'],
                fornecedor=fornecedor,
                categoria=categoria,
                estoque_minimo=produto_data['estoque_minimo'],
                loja=loja,
                status=produto_data['status'],
            )

        self.stdout.write(self.style.SUCCESS('Produtos recriados com sucesso'))