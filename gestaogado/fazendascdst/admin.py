from django.contrib import admin
from .models import Fazenda, Lote

@admin.register(Fazenda)
class FazendaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'localização', 'data_de_cadastro', 'is_active')
    search_fields = ('nome', 'localização')
    list_filter = ('data_de_cadastro', 'is_active')
    date_hierarchy = 'data_de_cadastro'
    actions = ['marcar_como_ativo', 'marcar_como_inativo']
    
    def get_queryset(self, request):
        # Mostrar todos os registros (incluindo os deletados) no admin
        return self.model.all_objects.get_queryset()
    
    def marcar_como_ativo(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} fazendas marcadas como ativas.')
    marcar_como_ativo.short_description = "Marcar como ativo"
    
    def marcar_como_inativo(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} fazendas marcadas como inativas.')
    marcar_como_inativo.short_description = "Marcar como inativo"


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'fazenda', 'capacidade_maxima', 'get_animal_count', 'is_active')
    list_filter = ('fazenda', 'is_active')
    search_fields = ('nome', 'fazenda__nome')
    date_hierarchy = 'data_de_cadastro'
    actions = ['marcar_como_ativo', 'marcar_como_inativo']
    
    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()
    
    def marcar_como_ativo(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} lotes marcados como ativos.')
    marcar_como_ativo.short_description = "Marcar como ativo"
    
    def marcar_como_inativo(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} lotes marcados como inativos.')
    marcar_como_inativo.short_description = "Marcar como inativo"
    
    def get_animal_count(self, obj):
        return obj.get_animal_count()
    get_animal_count.short_description = "Nº Animais"
