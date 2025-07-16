from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='relatorios_index'),
    path('mensal/', views.relatorio_mensal, name='relatorio_mensal'),
    path('anual/', views.relatorio_anual, name='relatorio_anual'),
    path('mensal/pdf/', views.exportar_pdf_relatorio_mensal, name='exportar_pdf_mensal'),
    path('mensal/excel/', views.exportar_excel_relatorio_mensal, name='exportar_excel_mensal'),
    path('anual/pdf/', views.exportar_pdf_relatorio_anual, name='exportar_pdf_anual'),
    path('anual/excel/', views.exportar_excel_relatorio_anual, name='exportar_excel_anual'),
    # URLs para observações
    path('observacao/<int:ano>/<int:mes>/', views.editar_observacao, name='editar_observacao'),
    path('observacao/<int:ano>/<int:mes>/get/', views.obter_observacao, name='obter_observacao'),
    # URLs para observações detalhadas
    path('observacao-detalhada/adicionar/', views.adicionar_observacao_detalhada, name='adicionar_observacao_detalhada'),
    path('observacao-detalhada/listar/', views.listar_observacoes_detalhadas, name='listar_observacoes_detalhadas'),
    path('observacao-detalhada/excluir/<int:obs_id>/', views.excluir_observacao_detalhada, name='excluir_observacao_detalhada'),
]