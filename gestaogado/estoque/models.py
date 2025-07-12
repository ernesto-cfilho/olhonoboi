from django.db import models
from fazendascdst.models import Fazenda


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

    def __str__(self):
        return f'{self.nome}-{self.tipo}-{self.fazenda.nome}'
    
class Movimentacao_estoque(models.Model):
    produto = models.ForeignKey(Produto, on_delete= models.CASCADE)
    tipo = models.CharField(max_length=10, choices=(('entrada', 'Entrada'),('saida','Saída')))
    quantidade = models.IntegerField()
    data = models.DateField()
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.tipo}-{self.produto.nome}-{self.quantidade}-{self.data}'