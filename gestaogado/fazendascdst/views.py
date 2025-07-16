# pyright: reportAttributeAccessIssue=false
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse
from .models import Fazenda, Lote
from django.http import JsonResponse
from gado.models import Animal
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate
from django.utils import timezone

def index(request):
    return render(request, 'fazendascdst/index.html')

def lista_fazendas(request):
    fazendas = Fazenda.objects.filter(user=request.user)
    return render(request, 'fazendascdst/lista.html', {'fazendas': fazendas})

@login_required
def adicionar_fazenda(request):
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            localizacao = request.POST.get('localizacao')
            
            fazenda = Fazenda.objects.create(
                nome=nome,
                localização=localizacao,
                user=request.user
            )
            
            messages.success(request, f'Fazenda {nome} adicionada com sucesso!')
            return redirect('lista_fazendas')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar fazenda: {str(e)}')
    
    return render(request, 'fazendascdst/adicionar.html')

def deletar_fazenda(request, fazenda_id):
    if request.method == 'POST':
        try:
            fazenda = Fazenda.objects.get(id=fazenda_id, user=request.user)
            nome = fazenda.nome
            fazenda.soft_delete()  # Usar soft delete ao invés de delete()
            return JsonResponse({'success': True, 'message': f'Fazenda {nome} removida com sucesso!'})
        except Fazenda.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Fazenda não encontrada!'})
    return JsonResponse({'success': False, 'message': 'Método não permitido!'})

# Função para verificar se o usuário é administrador
def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def lista_fazendas_deletadas(request):
    """Lista apenas as fazendas marcadas como deletadas (apenas para administradores)"""
    fazendas_deletadas = Fazenda.all_objects.filter(is_active=False, user=request.user)
    return render(request, 'fazendascdst/lista_deletadas.html', {'fazendas': fazendas_deletadas})

@user_passes_test(is_admin)
def restaurar_fazenda(request, fazenda_id):
    """Restaura uma fazenda deletada (apenas para administradores)"""
    if request.method == 'POST':
        try:
            fazenda = Fazenda.all_objects.get(id=fazenda_id, is_active=False)
            nome = fazenda.nome
            fazenda.restore()
            return JsonResponse({'success': True, 'message': f'Fazenda {nome} restaurada com sucesso!'})
        except Fazenda.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Fazenda não encontrada!'})
    return JsonResponse({'success': False, 'message': 'Método não permitido!'})

@user_passes_test(is_admin)
def deletar_fazenda_permanente(request, fazenda_id):
    """Deleta permanentemente uma fazenda (apenas para administradores)"""
    if request.method == 'POST':
        try:
            fazenda = Fazenda.all_objects.get(id=fazenda_id)
            nome = fazenda.nome
            fazenda.delete()  # Deleção permanente
            return JsonResponse({'success': True, 'message': f'Fazenda {nome} removida permanentemente!'})
        except Fazenda.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Fazenda não encontrada!'})
    return JsonResponse({'success': False, 'message': 'Método não permitido!'})

# ========== VIEWS PARA LOTES ==========

@login_required
def lista_piquetes(request):
    fazenda_id = request.GET.get('fazenda')
    if fazenda_id:
        fazenda = get_object_or_404(Fazenda, id=fazenda_id, user=request.user)
        lotes = Lote.objects.filter(fazenda=fazenda, user=request.user).select_related('fazenda')
    else:
        fazenda = None
        lotes = Lote.objects.filter(user=request.user).select_related('fazenda')
    fazendas = Fazenda.objects.filter(user=request.user)
    # Adicionar contagem de animais ativos em cada lote
    lotes_data = []
    for lote in lotes:
        total_animais = lote.animais.filter(is_active=True, user=request.user).count()
        lotes_data.append({
            'lote': lote,
            'total_animais': total_animais,
        })
    context = {
        'lotes_data': lotes_data,
        'lotes': lotes,
        'fazendas': fazendas,
        'fazenda_selecionada': fazenda,
    }
    return render(request, 'fazendascdst/lista_lotes.html', context)

@login_required
def adicionar_piquete(request):
    """Adiciona um novo lote"""
    if request.method == 'POST':
        try:
            fazenda_id = request.POST.get('fazenda')
            nome = request.POST.get('nome')
            capacidade_maxima = request.POST.get('capacidade_maxima')
            
            fazenda = Fazenda.objects.get(id=fazenda_id, user=request.user)
            
            # Se nome não fornecido, gerar automaticamente
            if not nome:
                ultimo_lote = Lote.objects.filter(fazenda=fazenda, user=request.user).order_by('id').last()
                proximo_numero = ultimo_lote.id + 1 if ultimo_lote else 1
                nome = f"Lote {proximo_numero}"
            
            lote = Lote.objects.create(
                fazenda=fazenda,
                nome=nome,
                capacidade_maxima=capacidade_maxima if capacidade_maxima else None,
                user=request.user
            )
            
            messages.success(request, f'Lote {nome} adicionado com sucesso!')
            return redirect('lista_piquetes')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar lote: {str(e)}')
    
    fazendas = Fazenda.objects.filter(user=request.user)
    return render(request, 'fazendascdst/adicionar_lote.html', {'fazendas': fazendas})

@login_required
def editar_piquete(request, piquete_id):
    """Edita um lote existente"""
    lote = get_object_or_404(Lote, id=piquete_id, user=request.user)
    
    if request.method == 'POST':
        try:
            lote.nome = request.POST.get('nome')
            lote.capacidade_maxima = request.POST.get('capacidade_maxima') if request.POST.get('capacidade_maxima') else None
            lote.save()
            
            messages.success(request, f'Lote {lote.nome} atualizado com sucesso!')
            
            # Verificar se há parâmetros de retorno para preservar filtros
            next_url = request.POST.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            elif request.POST.get('fazenda'):
                return redirect(f'{reverse("overview_piquetes")}?fazenda={request.POST.get("fazenda")}')
            else:
                return redirect('overview_piquetes')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar lote: {str(e)}')
    
    fazendas = Fazenda.objects.filter(user=request.user)
    context = {
        'lote': lote,
        'fazendas': fazendas,
    }
    return render(request, 'fazendascdst/editar_lote.html', context)

def deletar_piquete(request, piquete_id):
    """Soft delete de um lote"""
    if request.method == 'POST':
        try:
            lote = Lote.objects.get(id=piquete_id, user=request.user)
            nome = lote.nome
            lote.soft_delete()
            return JsonResponse({'success': True, 'message': f'Lote {nome} removido com sucesso!'})
        except Lote.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Lote não encontrado!'})
    return JsonResponse({'success': False, 'message': 'Método não permitido!'})

@login_required
@require_POST
def excluir_animais_do_lote(request):
    lote_id = request.POST.get('lote_id')
    quantidade = int(request.POST.get('quantidade', 0))
    if not lote_id or quantidade <= 0:
        messages.error(request, 'Selecione um lote e informe uma quantidade válida.')
        return redirect('lista_piquetes')
    try:
        lote = Lote.objects.get(id=lote_id, user=request.user)
        animais = Animal.objects.filter(lote=lote, user=request.user, is_active=True).order_by('data_entrada')[:quantidade]
        count = 0
        for animal in animais:
            animal.soft_delete()
            count += 1
        if count:
            messages.success(request, f'{count} animal(is) excluído(s) do lote {lote.nome} com sucesso!')
        else:
            messages.warning(request, 'Nenhum animal ativo encontrado para exclusão neste lote.')
    except Lote.DoesNotExist:
        messages.error(request, 'Lote não encontrado.')
    return redirect('lista_piquetes')

@login_required
@require_POST
def adicionar_animal_lote(request):
    lote_id = request.POST.get('lote_id')
    identificador = request.POST.get('identificador') or 'SN'
    tipo = 'CORTE'  # Sistema configurado apenas para gado de corte
    peso = request.POST.get('peso') or 0
    data_entrada = request.POST.get('data_entrada') or timezone.now().date()
    lote = get_object_or_404(Lote, id=lote_id, user=request.user)
    Animal.objects.create(
        fazenda=lote.fazenda,
        lote=lote,
        identificador=identificador,
        tipo=tipo,
        peso=peso,
        data_entrada=data_entrada,
        user=request.user
    )
    messages.success(request, f'Animal {identificador} adicionado ao lote {lote.nome}!')
    return redirect('overview_lotes')

@login_required
@require_POST
def adicionar_animais_lote(request):
    lote_id = request.POST.get('lote_id')
    quantidade = int(request.POST.get('quantidade', 0))
    peso_total = float(request.POST.get('peso_total', 0))
    identificadores = request.POST.get('identificadores', '').replace(',', '\n').splitlines()
    tipo = 'CORTE'  # Sistema configurado apenas para gado de corte
    data_entrada = request.POST.get('data_entrada') or timezone.now().date()
    lote = get_object_or_404(Lote, id=lote_id, user=request.user)

    if quantidade <= 0 or peso_total <= 0:
        messages.error(request, 'Informe uma quantidade e peso total válidos.')
        return redirect('overview_lotes')

    peso_medio = round(peso_total / quantidade, 2)
    # Se não informar identificadores, todos serão 'SN'
    if not identificadores or all(not i.strip() for i in identificadores):
        identificadores = ['SN'] * quantidade
    else:
        # Completa com 'SN' se informar menos identificadores que a quantidade
        identificadores = [i.strip() or 'SN' for i in identificadores]
        while len(identificadores) < quantidade:
            identificadores.append('SN')
        # Se informar mais identificadores que a quantidade, ignora o excedente
        identificadores = identificadores[:quantidade]

    count = 0
    for identificador in identificadores:
        Animal.objects.create(
            fazenda=lote.fazenda,
            lote=lote,
            identificador=identificador,
            tipo=tipo,
            peso=peso_medio,
            data_entrada=data_entrada,
            user=request.user
        )
        count += 1
    messages.success(request, f'{count} animal(is) adicionado(s) ao lote {lote.nome} com peso médio de {peso_medio}kg!')
    return redirect('overview_lotes')

@login_required
@require_POST
def excluir_animal_lote(request):
    lote_id = request.POST.get('lote_id')
    identificador = request.POST.get('identificador')
    lote = get_object_or_404(Lote, id=lote_id, user=request.user)
    animal = Animal.objects.filter(lote=lote, identificador=identificador, is_active=True, user=request.user).first()
    if animal:
        animal.soft_delete()
        messages.success(request, f'Animal {identificador} excluído do lote {lote.nome}!')
    else:
        messages.error(request, f'Animal {identificador} não encontrado no lote {lote.nome}!')
    return redirect('overview_lotes')

@login_required
@require_POST
def excluir_animais_lote(request):
    lote_id = request.POST.get('lote_id')
    quantidade = int(request.POST.get('quantidade', 0))
    lote = get_object_or_404(Lote, id=lote_id, user=request.user)
    animais = Animal.objects.filter(lote=lote, is_active=True, user=request.user).order_by('data_entrada')[:quantidade]
    count = 0
    for animal in animais:
        animal.soft_delete()
        count += 1
    messages.success(request, f'{count} animal(is) excluído(s) do lote {lote.nome}!')
    return redirect('overview_lotes')

@login_required
@require_POST
def excluir_lote_com_senha(request):
    lote_id = request.POST.get('lote_id')
    senha = request.POST.get('senha')
    user = request.user
    lote = get_object_or_404(Lote, id=lote_id, user=user)
    if not user.check_password(senha):
        messages.error(request, 'Senha incorreta! O lote não foi excluído.')
        return redirect('overview_lotes')
    lote.delete()
    messages.success(request, f'Lote {lote.nome} excluído com sucesso!')
    return redirect('overview_lotes')

@login_required
def overview_lotes(request):
    lotes = Lote.objects.filter(user=request.user, is_active=True)
    lotes_data = []
    total_animais = 0
    for lote in lotes:
        n_animais = lote.animais.filter(is_active=True, user=request.user).count()
        lotes_data.append({
            'lote': lote,
            'total_animais': n_animais,
        })
        total_animais += n_animais
    context = {
        'lotes_data': lotes_data,
        'total_lotes': lotes.count(),
        'total_animais': total_animais,
    }
    return render(request, 'fazendascdst/overview_lotes.html', context)
