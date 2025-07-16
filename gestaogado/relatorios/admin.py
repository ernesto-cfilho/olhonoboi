from django.contrib import admin
from .models import ObservacaoRelatorio

@admin.register(ObservacaoRelatorio)
class ObservacaoRelatorioAdmin(admin.ModelAdmin):
    list_display = ['user', 'tipo', 'lote', 'data_referencia', 'data_criacao', 'mes', 'ano']
    list_filter = ['tipo', 'mes', 'ano', 'data_criacao']
    search_fields = ['observacao', 'lote']
    date_hierarchy = 'data_criacao'
    
    def observacao_curta(self, obj):
        return obj.observacao[:50] + "..." if len(obj.observacao) > 50 else obj.observacao
    observacao_curta.short_description = 'Observação'
