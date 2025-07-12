from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='relatorios_index'),
    path('mensal/', views.relatorio_mensal, name='relatorio_mensal'),
    path('anual/', views.relatorio_anual, name='relatorio_anual'),
]