from django.db import models
from django.contrib.auth.models import User
from django.db.models import  SET_NULL


class Loja(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

User.add_to_class('loja', models.ForeignKey(Loja, on_delete=models.SET_NULL, null=True, blank=True))

class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    contato = models.CharField(max_length=100)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, default=1)


    def __str__(self):
        return self.nome

# Categoria de Produto
class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.nome

# Produto
class Produto(models.Model):
    STATUS_CHOICES = [
        ('em_estoque', 'Em Estoque'),
        ('em_uso', 'Em Uso'),
    ]

    TIPO_QUANTIDADE_CHOICES = [
        ('UN', 'Unidade'),
        ('L', 'Litro'),
        ('KG', 'Quilograma'),
        ('G', 'Grama'),
        ('PCT', 'Pacote')
    ]

    nome = models.CharField(max_length=100)
    quantidade = models.FloatField()
    tipo_quantidade = models.CharField(max_length=20, choices=TIPO_QUANTIDADE_CHOICES)
    codigo_de_barras = models.CharField(max_length=50)
    validade = models.DateField(null=True, blank=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=SET_NULL, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=SET_NULL, null=True, blank=True)
    estoque_minimo = models.FloatField(default=0)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, default=1)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='em_estoque'
    )
    class Meta:
        unique_together = ('codigo_de_barras', 'loja')  # Restringe a unicidade para código de barras e loja

    def __str__(self):
        return f"{self.nome} - {self.quantidade} {self.tipo_quantidade} ({self.status})"

# Movimento de Estoque
class MovimentoEstoque(models.Model):
    TIPOS_MOVIMENTO = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('transferencia', 'Transferência')
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    tipo_movimento = models.CharField(max_length=20, choices=TIPOS_MOVIMENTO)
    quantidade = models.FloatField()
    data_movimento = models.DateTimeField(auto_now_add=True)
    responsavel = models.ForeignKey(User, on_delete=models.CASCADE)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.tipo_movimento} - {self.produto.nome} ({self.quantidade})"
