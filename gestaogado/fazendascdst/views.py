from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Fazenda, Lote
from django.http import JsonResponse

def index(request):
    return render(request, 'fazendascdst/index.html')

def lista_fazendas(request):
    fazendas = Fazenda.objects.all()
    return render(request, 'fazendascdst/lista.html', {'fazendas': fazendas})

@login_required
def adicionar_fazenda(request):
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            localizacao = request.POST.get('localizacao')
            area = request.POST.get('area')
            
            fazenda = Fazenda.objects.create(
                nome=nome,
                localização=localizacao,
                area=area if area else None
            )
            
            messages.success(request, f'Fazenda {nome} adicionada com sucesso!')
            return redirect('lista_fazendas')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar fazenda: {str(e)}')
    
    return render(request, 'fazendascdst/adicionar.html')

def deletar_fazenda(request, fazenda_id):
    if request.method == 'POST':
        try:
            fazenda = Fazenda.objects.get(id=fazenda_id)
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
    fazendas_deletadas = Fazenda.all_objects.filter(is_active=False)
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
    """Lista todos os lotes"""
    fazenda_id = request.GET.get('fazenda')
    
    if fazenda_id:
        fazenda = get_object_or_404(Fazenda, id=fazenda_id)
        lotes = Lote.objects.filter(fazenda=fazenda).select_related('fazenda')
    else:
        fazenda = None
        lotes = Lote.objects.all().select_related('fazenda')
    
    fazendas = Fazenda.objects.all()
    context = {
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
            area = request.POST.get('area')
            capacidade_maxima = request.POST.get('capacidade_maxima')
            
            fazenda = Fazenda.objects.get(id=fazenda_id)
            
            # Se nome não fornecido, gerar automaticamente
            if not nome:
                ultimo_lote = Lote.objects.filter(fazenda=fazenda).order_by('id').last()
                proximo_numero = ultimo_lote.id + 1 if ultimo_lote else 1
                nome = f"Lote {proximo_numero}"
            
            lote = Lote.objects.create(
                fazenda=fazenda,
                nome=nome,
                area=area if area else None,
                capacidade_maxima=capacidade_maxima if capacidade_maxima else None
            )
            
            messages.success(request, f'Lote {nome} adicionado com sucesso!')
            return redirect('lista_piquetes')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar lote: {str(e)}')
    
    fazendas = Fazenda.objects.all()
    return render(request, 'fazendascdst/adicionar_lote.html', {'fazendas': fazendas})

@login_required
def editar_piquete(request, piquete_id):
    """Edita um lote existente"""
    lote = get_object_or_404(Lote, id=piquete_id)
    
    if request.method == 'POST':
        try:
            lote.nome = request.POST.get('nome')
            lote.area = request.POST.get('area') if request.POST.get('area') else None
            lote.capacidade_maxima = request.POST.get('capacidade_maxima') if request.POST.get('capacidade_maxima') else None
            lote.save()
            
            messages.success(request, f'Lote {lote.nome} atualizado com sucesso!')
            return redirect('lista_piquetes')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar lote: {str(e)}')
    
    fazendas = Fazenda.objects.all()
    context = {
        'lote': lote,
        'fazendas': fazendas,
    }
    return render(request, 'fazendascdst/editar_lote.html', context)

def deletar_piquete(request, piquete_id):
    """Soft delete de um lote"""
    if request.method == 'POST':
        try:
            lote = Lote.objects.get(id=piquete_id)
            nome = lote.nome
            lote.soft_delete()
            return JsonResponse({'success': True, 'message': f'Lote {nome} removido com sucesso!'})
        except Lote.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Lote não encontrado!'})
    return JsonResponse({'success': False, 'message': 'Método não permitido!'})
