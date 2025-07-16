# pyright: reportAttributeAccessIssue=false
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class ObservacaoRelatorio(models.Model):
    TIPO_CHOICES = [
        ('LOTE', 'Lote'),
        ('VACINACAO', 'Vacinação'),
        ('BAIXA', 'Baixa de Animais'),
        ('GERAL', 'Observação Geral'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, null=True, blank=True)
    lote = models.CharField(max_length=100, blank=True, null=True, help_text="Nome do lote (se aplicável)")
    data_referencia = models.DateField(blank=True, null=True, help_text="Data de referência (se aplicável)")
    observacao = models.TextField(blank=True, null=True, help_text="Observação (opcional)")
    data_criacao = models.DateTimeField(default=timezone.now)
    mes = models.IntegerField()
    ano = models.IntegerField()
    
    class Meta:
        verbose_name = "Observação de Relatório"
        verbose_name_plural = "Observações de Relatórios"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.data_criacao.strftime('%d/%m/%Y')}"

    @classmethod
    def get_observacao(cls, user, ano, mes):
        """Retorna a observação para um usuário, ano e mês específicos"""
        try:
            return cls.objects.get(user=user, ano=ano, mes=mes)
        except cls.DoesNotExist:
            return None
