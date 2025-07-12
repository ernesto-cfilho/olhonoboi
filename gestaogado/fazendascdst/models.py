from django.db import models

class ActiveManager(models.Manager):
    """Manager que retorna apenas registros ativos"""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class AllManager(models.Manager):
    """Manager que retorna todos os registros (incluindo inativos)"""
    def get_queryset(self):
        return super().get_queryset()

class Fazenda(models.Model):
    nome = models.CharField(max_length=100)
    localização = models.TextField()
    area = models.DecimalField("Área (hectares)", max_digits=10, decimal_places=2, null=True, blank=True)
    data_de_cadastro = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Managers
    objects = ActiveManager()  # Manager padrão - apenas registros ativos
    all_objects = AllManager()  # Manager para todos os registros

    def soft_delete(self):
        """Marca a fazenda como inativa (soft delete)"""
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restaura a fazenda (marca como ativa novamente)"""
        self.is_active = True
        self.save()
    
    def __str__(self):
        return self.nome


class Lote(models.Model):
    nome = models.CharField("Nome do Lote", max_length=100)
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE, related_name='lotes')
    area = models.DecimalField("Área (hectares)", max_digits=8, decimal_places=2, null=True, blank=True)
    capacidade_maxima = models.IntegerField("Capacidade Máxima de Animais", null=True, blank=True)
    data_de_cadastro = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Managers
    objects = ActiveManager()
    all_objects = AllManager()

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        unique_together = ['nome', 'fazenda']

    def soft_delete(self):
        """Marca o lote como inativo (soft delete)"""
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restaura o lote (marca como ativo novamente)"""
        self.is_active = True
        self.save()

    def get_animal_count(self):
        """Retorna a quantidade de animais no lote"""
        return self.animais.count()

    def get_next_numero(self):
        """Retorna o próximo número para o lote"""
        ultimo_lote = Lote.objects.filter(fazenda=self.fazenda).order_by('id').last()
        if ultimo_lote:
            try:
                # Tenta extrair o número do nome do último lote
                import re
                numeros = re.findall(r'\d+', ultimo_lote.nome)
                if numeros:
                    return int(numeros[-1]) + 1
                else:
                    return ultimo_lote.id + 1
            except:
                return ultimo_lote.id + 1
        return 1

    def __str__(self):
        return f'{self.nome} - {self.fazenda.nome}'
    