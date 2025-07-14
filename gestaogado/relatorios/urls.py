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
]