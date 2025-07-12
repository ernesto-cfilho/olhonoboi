from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from gado.models import Animal, Vacinacao
from fazendascdst.models import Fazenda, Lote
from estoque.models import Produto, Movimentacao_estoque

def index(request):
    # Data atual
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    inicio_ano = hoje.replace(month=1, day=1)
    
    # Estatísticas gerais
    total_animais = Animal.objects.count()
    total_fazendas = Fazenda.objects.count()
    total_lotes = Lote.objects.count()
    total_produtos = Produto.objects.count()
    
    # Estatísticas por tipo de gado
    gado_por_tipo = Animal.objects.values('tipo').annotate(
        total=Count('id'),
        peso_medio=Avg('peso')
    )
    
    # Animais por fazenda
    animais_por_fazenda = Animal.objects.values('fazenda__nome').annotate(
        total=Count('id'),
        peso_total=Sum('peso')
    ).order_by('-total')[:5]
    
    # Vacinações recentes (últimos 30 dias)
    vacinacoes_mes = Vacinacao.objects.filter(
        data_de_aplicacao__gte=hoje - timedelta(days=30)
    ).count()
    
    context = {
        'total_animais': total_animais,
        'total_fazendas': total_fazendas, 
        'total_lotes': total_lotes,
        'total_produtos': total_produtos,
        'gado_por_tipo': gado_por_tipo,
        'animais_por_fazenda': animais_por_fazenda,
        'vacinacoes_mes': vacinacoes_mes,
    }
    
    return render(request, 'relatorios/index.html', context)

def relatorio_mensal(request):
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    
    # Dados do mês atual
    animais_mes = Animal.objects.filter(data_entrada__gte=inicio_mes)
    vacinacoes_mes = Vacinacao.objects.filter(data_de_aplicacao__gte=inicio_mes)
    
    # Movimentações de estoque do mês
    movimentacoes_mes = Movimentacao_estoque.objects.filter(data__gte=inicio_mes)
    
    context = {
        'mes_atual': hoje.strftime('%B %Y'),
        'animais_mes': animais_mes,
        'vacinacoes_mes': vacinacoes_mes,
        'movimentacoes_mes': movimentacoes_mes,
        'total_animais_mes': animais_mes.count(),
        'total_vacinacoes_mes': vacinacoes_mes.count(),
    }
    
    return render(request, 'relatorios/mensal.html', context)

def relatorio_anual(request):
    hoje = timezone.now().date()
    inicio_ano = hoje.replace(month=1, day=1)
    
    # Dados do ano atual
    animais_ano = Animal.objects.filter(data_entrada__gte=inicio_ano)
    vacinacoes_ano = Vacinacao.objects.filter(data_de_aplicacao__gte=inicio_ano)
    
    # Estatísticas anuais por mês
    animais_por_mes = []
    for mes in range(1, 13):
        count = Animal.objects.filter(
            data_entrada__year=hoje.year,
            data_entrada__month=mes
        ).count()
        animais_por_mes.append({
            'mes': mes,
            'nome_mes': datetime(hoje.year, mes, 1).strftime('%B'),
            'total': count
        })
    
    context = {
        'ano_atual': hoje.year,
        'animais_ano': animais_ano,
        'vacinacoes_ano': vacinacoes_ano,
        'total_animais_ano': animais_ano.count(),
        'total_vacinacoes_ano': vacinacoes_ano.count(),
        'animais_por_mes': animais_por_mes,
    }
    
    return render(request, 'relatorios/anual.html', context)