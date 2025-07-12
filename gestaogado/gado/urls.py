from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_animais, name='lista_animais'),
    path('adicionar/', views.adicionar_animal, name='adicionar_animal'),
    path('deletar/<int:animal_id>/', views.deletar_animal, name='deletar_animal'),
    
    # URLs para administradores
    path('admin/deletados/', views.lista_animais_deletados, name='lista_animais_deletados'),
    path('admin/restaurar/<int:animal_id>/', views.restaurar_animal, name='restaurar_animal'),
    path('admin/deletar-permanente/<int:animal_id>/', views.deletar_animal_permanente, name='deletar_animal_permanente'),
    
    # URLs para vacinas
    path('vacinas/', views.lista_vacinas, name='lista_vacinas'),
    path('vacinas/adicionar/', views.adicionar_vacina, name='adicionar_vacina'),
    
    # URLs para vacinações
    path('vacinacoes/', views.lista_vacinacoes, name='lista_vacinacoes'),
    path('vacinacoes/adicionar/', views.adicionar_vacinacao, name='adicionar_vacinacao'),
    
    # URLs para batch insert e lotes
    path('batch-insert/', views.batch_insert_animais, name='batch_insert_animais'),
    path('lotes/', views.overview_piquetes, name='overview_piquetes'),
    path('mover-animais/', views.mover_animais, name='mover_animais'),
    
    # AJAX URLs
    path('ajax/lotes/', views.get_lotes_by_fazenda, name='get_lotes_by_fazenda'),
]
