from django.contrib import admin
from .models import Animal, Vacina, Vacinacao  
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'fazenda', 'lote', 'tipo', 'peso', 'peso_em_arrobas', 'data_entrada', 'is_active')
    list_filter = ('fazenda', 'lote', 'tipo', 'is_active')
    search_fields = ('identificador', 'fazenda__nome', 'lote__nome')
    date_hierarchy = 'data_entrada'
    actions = ['marcar_como_ativo', 'marcar_como_inativo']
    
    def get_queryset(self, request):
        # Mostrar todos os registros (incluindo os deletados) no admin
        return self.model.all_objects.get_queryset()
    
    def marcar_como_ativo(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} animais marcados como ativos.')
    marcar_como_ativo.short_description = "Marcar como ativo"
    
    def marcar_como_inativo(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} animais marcados como inativos.')
    marcar_como_inativo.short_description = "Marcar como inativo"

@admin.register(Vacina)
class VacinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'validade_dias')
    search_fields = ('nome',)

@admin.register(Vacinacao)
class VacinacaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'vacina', 'data_de_aplicacao')
    list_filter = ('vacina', 'data_de_aplicacao')
    date_hierarchy = 'data_de_aplicacao'