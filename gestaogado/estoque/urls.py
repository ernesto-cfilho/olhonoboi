from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='estoque_index'),
    path('adicionar/', views.adicionar_produto, name='adicionar_produto'),
    path('editar/<int:produto_id>/', views.editar_produto, name='editar_produto'),
    path('movimentar/<int:produto_id>/', views.movimentar_estoque, name='movimentar_estoque'),
    path('deletar/<int:produto_id>/', views.deletar_produto, name='deletar_produto'),
]