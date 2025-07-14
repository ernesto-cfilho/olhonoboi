from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from .models import Produto, Movimentacao_estoque
from fazendascdst.models import Fazenda

@login_required
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

@login_required
def adicionar_produto(request):
    if request.method == 'POST':
        try:
            fazenda_id = request.POST.get('fazenda')
            nome = request.POST.get('nome')
            tipo = request.POST.get('tipo')
            quantidade = int(request.POST.get('quantidade', 0))
            valor_unitario = float(request.POST.get('valor_unitario', 0))
            
            fazenda = Fazenda.objects.get(id=fazenda_id)
            
            produto = Produto.objects.create(
                fazenda=fazenda,
                nome=nome,
                tipo=tipo,
                quantidade=quantidade,
                valor_unitario=valor_unitario
            )
            
            # Registrar movimentação de entrada
            if quantidade > 0:
                Movimentacao_estoque.objects.create(
                    produto=produto,
                    tipo='entrada',
                    quantidade=quantidade,
                    data=request.POST.get('data', None),
                    observacao='Entrada inicial do produto'
                )
            
            messages.success(request, f'Produto {nome} adicionado com sucesso!')
            return redirect('estoque_index')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar produto: {str(e)}')
    
    fazendas = Fazenda.objects.all()
    return render(request, 'estoque/adicionar_produto.html', {'fazendas': fazendas})

@login_required
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    
    if request.method == 'POST':
        try:
            produto.nome = request.POST.get('nome')
            produto.tipo = request.POST.get('tipo')
            produto.valor_unitario = float(request.POST.get('valor_unitario', 0))
            produto.save()
            
            messages.success(request, f'Produto {produto.nome} atualizado com sucesso!')
            return redirect('estoque_index')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar produto: {str(e)}')
    
    fazendas = Fazenda.objects.all()
    return render(request, 'estoque/editar_produto.html', {
        'produto': produto,
        'fazendas': fazendas
    })

@login_required
def movimentar_estoque(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    
    if request.method == 'POST':
        try:
            tipo_movimentacao = request.POST.get('tipo')
            quantidade = int(request.POST.get('quantidade', 0))
            data = request.POST.get('data')
            observacao = request.POST.get('observacao', '')
            
            if tipo_movimentacao == 'saida' and quantidade > produto.quantidade:
                messages.error(request, 'Quantidade insuficiente em estoque!')
                return redirect('estoque_index')
            
            # Registrar movimentação
            Movimentacao_estoque.objects.create(
                produto=produto,
                tipo=tipo_movimentacao,
                quantidade=quantidade,
                data=data,
                observacao=observacao
            )
            
            # Atualizar quantidade do produto
            if tipo_movimentacao == 'entrada':
                produto.quantidade += quantidade
            else:
                produto.quantidade -= quantidade
            
            produto.save()
            
            messages.success(request, f'Movimentação registrada com sucesso!')
            return redirect('estoque_index')
            
        except Exception as e:
            messages.error(request, f'Erro ao registrar movimentação: {str(e)}')
    
    movimentacoes = Movimentacao_estoque.objects.filter(produto=produto).order_by('-data')
    return render(request, 'estoque/movimentar_estoque.html', {
        'produto': produto,
        'movimentacoes': movimentacoes
    })

@login_required
def deletar_produto(request, produto_id):
    if request.method == 'POST':
        try:
            produto = Produto.objects.get(id=produto_id)
            nome = produto.nome
            produto.delete()
            messages.success(request, f'Produto {nome} removido com sucesso!')
        except Produto.DoesNotExist:
            messages.error(request, 'Produto não encontrado!')
    
    return redirect('estoque_index')
