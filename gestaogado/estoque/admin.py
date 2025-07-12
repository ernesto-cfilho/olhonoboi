from django.contrib import admin
from .models import Produto, Movimentacao_estoque

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'fazenda', 'quantidade', 'valor_unitario')
    list_filter = ('tipo', 'fazenda')
    search_fields = ('nome', 'fazenda__nome')
    list_editable = ('quantidade', 'valor_unitario')

@admin.register(Movimentacao_estoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo', 'quantidade', 'data', 'observacao')
    list_filter = ('tipo', 'data', 'produto__tipo')
    search_fields = ('produto__nome', 'observacao')
    date_hierarchy = 'data'
