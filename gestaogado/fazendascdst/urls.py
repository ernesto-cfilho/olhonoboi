from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fazendas/', views.lista_fazendas, name='lista_fazendas'),
    path('fazendas/adicionar/', views.adicionar_fazenda, name='adicionar_fazenda'),
    path('fazendas/deletar/<int:fazenda_id>/', views.deletar_fazenda, name='deletar_fazenda'),
    
    # URLs para administradores
    path('fazendas/admin/deletadas/', views.lista_fazendas_deletadas, name='lista_fazendas_deletadas'),
    path('fazendas/admin/restaurar/<int:fazenda_id>/', views.restaurar_fazenda, name='restaurar_fazenda'),
    path('fazendas/admin/deletar-permanente/<int:fazenda_id>/', views.deletar_fazenda_permanente, name='deletar_fazenda_permanente'),
    
    # URLs para lotes
    path('lotes/', views.lista_piquetes, name='lista_piquetes'),
    path('lotes/adicionar/', views.adicionar_piquete, name='adicionar_piquete'),
    path('lotes/editar/<int:piquete_id>/', views.editar_piquete, name='editar_piquete'),
    path('lotes/deletar/<int:piquete_id>/', views.deletar_piquete, name='deletar_piquete'),
    path('excluir-animais-do-lote/', views.excluir_animais_do_lote, name='excluir_animais_do_lote'),
    path('adicionar-animal-lote/', views.adicionar_animal_lote, name='adicionar_animal_lote'),
    path('adicionar-animais-lote/', views.adicionar_animais_lote, name='adicionar_animais_lote'),
    path('excluir-animal-lote/', views.excluir_animal_lote, name='excluir_animal_lote'),
    path('excluir-animais-lote/', views.excluir_animais_lote, name='excluir_animais_lote'),
    path('excluir-lote-com-senha/', views.excluir_lote_com_senha, name='excluir_lote_com_senha'),
]
