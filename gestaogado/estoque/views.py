from django.shortcuts import render
from django.db.models import Sum, Count, Q
from .models import Produto, Movimentacao_estoque

def index(request):
    produtos = Produto.objects.all().select_related('fazenda')
    
    # Cálculos para estatísticas
    total_produtos = produtos.count()
    valor_total_estoque = produtos.aggregate(
        total=Sum('quantidade') * Sum('valor_unitario')
    )['total'] or 0
    
    # Produtos com baixo estoque (menos de 10 unidades)
    baixo_estoque = produtos.filter(quantidade__lt=10).count()
    
    # Categorias únicas
    categorias = produtos.values('tipo').distinct().count()
    
    # Produtos por categoria
    produtos_por_categoria = produtos.values('tipo').annotate(
        total=Count('id'),
        quantidade_total=Sum('quantidade')
    )
    
    context = {
        'produtos': produtos,
        'total_produtos': total_produtos,
        'valor_total_estoque': valor_total_estoque,
        'baixo_estoque': baixo_estoque,
        'categorias': categorias,
        'produtos_por_categoria': produtos_por_categoria,
    }
    
    return render(request, 'estoque/index.html', context)
