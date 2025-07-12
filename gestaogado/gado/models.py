from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from fazendascdst.models import Fazenda, Lote

class ActiveManager(models.Manager):
    """Manager que retorna apenas registros ativos"""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class AllManager(models.Manager):
    """Manager que retorna todos os registros (incluindo inativos)"""
    def get_queryset(self):
        return super().get_queryset()

class Animal(models.Model):
    TIPO_CHOICES = [
        ('CORTE', 'Gado de Corte'),
        ('LEITE', 'Gado Leiteiro'),
    ]
    
    fazenda = models.ForeignKey(Fazenda, on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='animais', verbose_name="Lote", null=True, blank=True)
    identificador = models.IntegerField("Identificador", unique=True, null=True, blank=True)  
    tipo = models.CharField("Tipo de Gado", max_length=10, choices=TIPO_CHOICES, default='CORTE')
    data_entrada = models.DateField("Data de Entrada")
    data_de_saida = models.DateField("Data de Saída", blank=True, null=True)
    peso = models.DecimalField("Peso (kg)", max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)

    # Managers
    objects = ActiveManager()  # Manager padrão - apenas registros ativos
    all_objects = AllManager()  # Manager para todos os registros

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"

    def soft_delete(self):
        """Marca o animal como inativo (soft delete)"""
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restaura o animal (marca como ativo novamente)"""
        self.is_active = True
        self.save()

    def mover_para_lote(self, novo_lote):
        """Move o animal para um novo lote"""
        if novo_lote.fazenda != self.fazenda:
            raise ValueError("O lote deve pertencer à mesma fazenda do animal")
        self.lote = novo_lote
        self.save()

    def get_next_identificador(self):
        """Retorna o próximo identificador disponível"""
        ultimo_animal = Animal.objects.filter(fazenda=self.fazenda).order_by('identificador').last()
        if ultimo_animal and ultimo_animal.identificador:
            return ultimo_animal.identificador + 1
        return 1

    def peso_em_arrobas(self):
        """Retorna o peso em arrobas (1 arroba = 15kg)"""
        return round(self.peso / 15, 2)

    @staticmethod
    def converter_kg_para_arroba(peso_kg):
        """Converte peso de kg para arroba"""
        return round(peso_kg / 15, 2)

    @staticmethod  
    def converter_arroba_para_kg(peso_arroba):
        """Converte peso de arroba para kg"""
        return round(peso_arroba * 15, 2)
    
    def __str__(self):
        return f'{self.identificador} - {self.fazenda.nome}'

class Vacina(models.Model):
    nome = models.CharField("Nome da Vacina", max_length=100)
    validade_dias = models.IntegerField("Validade (dias)", default=30)

    def __str__(self):
        return self.nome

class Vacinacao(models.Model):  
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name="Animal")
    vacina = models.ForeignKey(Vacina, on_delete=models.CASCADE, verbose_name="Vacina")
    data_de_aplicacao = models.DateField("Data de Aplicação")

    class Meta:
        verbose_name = "Vacinação"
        verbose_name_plural = "Vacinações"

    def __str__(self):
        return f'{self.animal.identificador} - {self.vacina.nome} ({self.data_de_aplicacao})'