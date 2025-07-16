from django.db import models
from fazendascdst.models import Fazenda, Lote
from django.contrib.auth.models import User


class Produto(models.Model):
    TIPO_CHOICES = (
        ('vacina', 'Vacina'),
        ('racao', 'Ração'),
        ('material','Material'),
    )
    fazenda = models.ForeignKey(Fazenda, on_delete= models.CASCADE)
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=25, choices= TIPO_CHOICES)
    quantidade = models.IntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.nome}-{self.tipo}-{self.fazenda.nome}'
    
class Movimentacao_estoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete= models.CASCADE)
    tipo = models.CharField(max_length=10, choices=(('entrada', 'Entrada'),('saida','Saída')))
    quantidade = models.IntegerField()
    data = models.DateField()
    observacao = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.tipo}-{self.produto.nome}-{self.quantidade}-{self.data}'

class MovimentacaoLote(models.Model):
    TIPO_CHOICES = (
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('baixa', 'Baixa'),
    )
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    data = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.PositiveIntegerField()
    peso_medio = models.DecimalField(max_digits=6, decimal_places=2)
    motivo = models.CharField(max_length=100, blank=True, null=True)
    obs_manejo = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.lote.nome} - {self.get_tipo_display()} - {self.data} ({self.quantidade})"