from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='estoque_index'),
    path('adicionar/', views.adicionar_produto, name='adicionar_produto'),
    path('editar/<int:produto_id>/', views.editar_produto, name='editar_produto'),
    path('movimentar/<int:produto_id>/', views.movimentar_estoque, name='movimentar_estoque'),
    path('deletar/<int:produto_id>/', views.deletar_produto, name='deletar_produto'),
    path('movimentacao-lote/', views.movimentacao_lote, name='movimentacao_lote'),
    path('historico-movimentacao-lote/', views.historico_movimentacao_lote, name='historico_movimentacao_lote'),
    path('relatorio-movimentacao-lote/', views.relatorio_movimentacao_lote, name='relatorio_movimentacao_lote'),
    path('exportar-excel-relatorio-movimentacao-lote/', views.exportar_excel_relatorio_movimentacao_lote, name='exportar_excel_relatorio_movimentacao_lote'),
    path('exportar-pdf-relatorio-movimentacao-lote/', views.exportar_pdf_relatorio_movimentacao_lote, name='exportar_pdf_relatorio_movimentacao_lote'),
]