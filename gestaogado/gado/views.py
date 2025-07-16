# pyright: reportAttributeAccessIssue=false
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse
from .models import Animal, Vacina, Vacinacao
from fazendascdst.models import Fazenda, Lote
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
def lista_animais(request):
    lote_id = request.GET.get('lote')
    if lote_id:
        lote = get_object_or_404(Lote, id=lote_id, user=request.user)
        animais = Animal.objects.filter(lote=lote, user=request.user, is_active=True).select_related('fazenda', 'lote')
        context = {
            'animais': animais,
            'lote_filtro': lote,
        }
    else:
        animais = Animal.objects.filter(user=request.user, is_active=True).select_related('fazenda', 'lote')
        context = {
            'animais': animais,
        }
    return render(request, 'gado/lista.html', context)

@login_required
def adicionar_animal(request):
    if request.method == 'POST':
        try:
            fazenda_id = request.POST.get('fazenda')
            lote_id = request.POST.get('lote')
            identificador = request.POST.get('identificador')
            tipo = 'CORTE'  # Sistema configurado apenas para gado de corte
            data_entrada = request.POST.get('data_entrada') or timezone.now().date()
            peso = request.POST.get('peso')
            fazenda = Fazenda.objects.get(id=fazenda_id, user=request.user)
            lote = Lote.objects.get(id=lote_id, user=request.user)
            # Identificador deve ser informado manualmente
            if not identificador:
                messages.error(request, 'O campo Identificador é obrigatório!')
                raise Exception('Identificador obrigatório')
            identificador = int(identificador)
            ativos = Animal.objects.filter(fazenda=fazenda, user=request.user, is_active=True).values_list('identificador', flat=True)
            if identificador in ativos:
                messages.error(request, f'Já existe um animal ativo com o identificador {identificador}!')
                raise Exception('Identificador duplicado')

            animal = Animal.objects.create(
                fazenda=fazenda,
                lote=lote,
                identificador=identificador,
                tipo=tipo,
                data_entrada=data_entrada,
                peso=peso,
                user=request.user
            )
            messages.success(request, f'Animal {identificador} adicionado com sucesso!')
            return redirect('lista_animais')
        except Exception as e:
            if not messages.get_messages(request):
                messages.error(request, f'Erro ao adicionar animal: {str(e)}')
    fazendas = Fazenda.objects.filter(user=request.user)
    return render(request, 'gado/adicionar.html', {'fazendas': fazendas})

def deletar_animal(request, animal_id):
    if request.method == 'POST':
        try:
            animal = Animal.objects.get(id=animal_id, user=request.user)
            identificador = animal.identificador
            animal.soft_delete()
            return JsonResponse({'success': True, 'message': f'Animal {identificador} removido com sucesso!'})
        except Animal.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Animal não encontrado!'})
    return JsonResponse({'success': False, 'message': 'Método não permitido!'})

# Função para verificar se o usuário é administrador
def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def lista_animais_deletados(request):
    """Lista apenas os animais marcados como deletados (apenas para administradores)"""
    animais_deletados = Animal.all_objects.filter(is_active=False).select_related('fazenda')
    return render(request, 'gado/lista_deletados.html', {'animais': animais_deletados})

@user_passes_test(is_admin)
def restaurar_animal(request, animal_id):
    """Restaura um animal deletado (apenas para administradores)"""
    if request.method == 'POST':
        try:
            animal = Animal.all_objects.get(id=animal_id, is_active=False)
            identificador = animal.identificador
            animal.restore()
            return JsonResponse({'success': True, 'message': f'Animal {identificador} restaurado com sucesso!'})
        except Animal.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Animal não encontrado!'})
    return JsonResponse({'success': False, 'message': 'Método não permitido!'})

@user_passes_test(is_admin)
def deletar_animal_permanente(request, animal_id):
    """Deleta permanentemente um animal (apenas para administradores)"""
    if request.method == 'POST':
        try:
            animal = Animal.all_objects.get(id=animal_id)
            identificador = animal.identificador
            animal.delete()  # Deleção permanente
            return JsonResponse({'success': True, 'message': f'Animal {identificador} removido permanentemente!'})
        except Animal.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Animal não encontrado!'})
    return JsonResponse({'success': False, 'message': 'Método não permitido!'})

# ========== VIEWS PARA VACINAS ==========

@login_required
def lista_vacinas(request):
    """Lista todas as vacinas"""
    vacinas = Vacina.objects.filter(user=request.user)
    return render(request, 'gado/vacinas/lista.html', {'vacinas': vacinas})

@login_required
def adicionar_vacina(request):
    """Adiciona uma nova vacina"""
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            validade_dias = request.POST.get('validade_dias')
            vacina = Vacina.objects.create(
                nome=nome,
                validade_dias=validade_dias,
                user=request.user
            )
            messages.success(request, f'Vacina {nome} adicionada com sucesso!')
            return redirect('lista_vacinas')
        except Exception as e:
            messages.error(request, f'Erro ao adicionar vacina: {str(e)}')
    
    return render(request, 'gado/vacinas/adicionar.html')

@login_required
def editar_vacina(request, vacina_id):
    """Edita uma vacina existente"""
    vacina = get_object_or_404(Vacina, id=vacina_id, user=request.user)
    
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            validade_dias = request.POST.get('validade_dias')
            
            vacina.nome = nome
            vacina.validade_dias = validade_dias
            vacina.save()
            
            messages.success(request, f'Vacina {nome} atualizada com sucesso!')
            return redirect('lista_vacinas')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar vacina: {str(e)}')
    
    return render(request, 'gado/vacinas/editar.html', {'vacina': vacina})

@login_required
def excluir_vacina(request, vacina_id):
    """Exclui uma vacina"""
    if request.method == 'POST':
        try:
            vacina = get_object_or_404(Vacina, id=vacina_id, user=request.user)
            nome = vacina.nome
            vacina.delete()
            messages.success(request, f'Vacina {nome} excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir vacina: {str(e)}')
    
    return redirect('lista_vacinas')

@login_required
def lista_vacinacoes(request):
    """Lista todas as vacinações"""
    vacinacoes = Vacinacao.objects.filter(user=request.user).select_related('animal', 'vacina')
    return render(request, 'gado/vacinacoes/lista.html', {'vacinacoes': vacinacoes})

@login_required
def adicionar_vacinacao(request):
    """Adiciona uma nova vacinação (individual ou em lote)"""
    if request.method == 'POST':
        try:
            lote_id = request.POST.get('lote')
            animal_id = request.POST.get('animal')
            vacina_id = request.POST.get('vacina')
            data_aplicacao = request.POST.get('data_aplicacao')
            vacina = Vacina.objects.get(id=vacina_id, user=request.user)
            vacinados = []
            if lote_id:
                # Vacinação em lote
                animais = Animal.objects.filter(lote_id=lote_id, user=request.user, is_active=True)
                for animal in animais:
                    Vacinacao.objects.create(
                        animal=animal,
                        vacina=vacina,
                        data_de_aplicacao=data_aplicacao,
                        user=request.user
                    )
                    vacinados.append(animal.identificador)
                messages.success(request, f'Vacinação registrada para {len(vacinados)} animais do lote!')
            elif animal_id:
                # Vacinação individual
                animal = Animal.objects.get(id=animal_id, user=request.user)
                Vacinacao.objects.create(
                    animal=animal,
                    vacina=vacina,
                    data_de_aplicacao=data_aplicacao,
                    user=request.user
                )
                messages.success(request, f'Vacinação de {animal.identificador} com {vacina.nome} registrada!')
            else:
                messages.error(request, 'Selecione um animal ou um lote para registrar a vacinação.')
                return redirect('adicionar_vacinacao')
            return redirect('lista_vacinacoes')
        except Exception as e:
            messages.error(request, f'Erro ao registrar vacinação: {str(e)}')
    animais = Animal.objects.filter(user=request.user)
    vacinas = Vacina.objects.filter(user=request.user)
    lotes = Lote.objects.filter(user=request.user)
    return render(request, 'gado/vacinacoes/adicionar.html', {
        'animais': animais,
        'vacinas': vacinas,
        'lotes': lotes
    })

# ========== VIEWS PARA BATCH INSERT ==========

@login_required
def batch_insert_animais(request):
    """Formulário para inserção em lote de animais com peso total"""
    if request.method == 'POST':
        try:
            fazenda_id = request.POST.get('fazenda')
            lote_id = request.POST.get('lote')
            tipo = 'CORTE'  # Sistema configurado apenas para gado de corte
            data_entrada = request.POST.get('data_entrada') or timezone.now().date()
            
            # Novos campos para inserção em lote
            quantidade_animais = int(request.POST.get('quantidade_animais', 0))
            peso_total = float(request.POST.get('peso_total', 0))
            unidade_peso = request.POST.get('unidade_peso', 'kg')  # kg ou arroba
            
            if quantidade_animais <= 0 or peso_total <= 0:
                messages.error(request, 'Quantidade de animais e peso total devem ser maiores que zero!')
                raise Exception('Valores inválidos')
            
            fazenda = Fazenda.objects.get(id=fazenda_id, user=request.user)
            lote = Lote.objects.get(id=lote_id, user=request.user)
            
            # Converter peso total para kg se estiver em arroba
            if unidade_peso == 'arroba':
                peso_total_kg = Animal.converter_arroba_para_kg(peso_total)
            else:
                peso_total_kg = peso_total
            
            # Calcular peso médio por animal
            peso_medio_kg = peso_total_kg / quantidade_animais
            

            
            # Criar animais sem identificadores automáticos
            animais_criados = []
            for i in range(quantidade_animais):
                animal = Animal.objects.create(
                    fazenda=fazenda,
                    lote=lote,
                    identificador=None,  # Deixar identificador como None para ser preenchido pelo cliente
                    tipo=tipo,
                    data_entrada=data_entrada,
                    peso=peso_medio_kg,
                    user=request.user
                )
                animais_criados.append(animal)
            
            # Mostrar informações na mensagem de sucesso
            peso_total_arroba = Animal.converter_kg_para_arroba(peso_total_kg)
            messages.success(request, 
                f'{len(animais_criados)} animais adicionados! '
                f'Peso total: {peso_total_kg:.1f}kg ({peso_total_arroba:.1f}@) - '
                f'Peso médio: {peso_medio_kg:.1f}kg ({Animal.converter_kg_para_arroba(peso_medio_kg):.1f}@)')
            
            return redirect('lista_animais')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar animais: {str(e)}')
    
    fazendas = Fazenda.objects.filter(user=request.user)
    return render(request, 'gado/batch_insert.html', {'fazendas': fazendas})

# ========== VIEWS PARA PIQUETES ==========

@login_required
def overview_piquetes(request):
    """Overview dos lotes com contagem de animais"""
    fazenda_id = request.GET.get('fazenda')
    
    if fazenda_id:
        fazenda = get_object_or_404(Fazenda, id=fazenda_id, user=request.user)
        lotes = Lote.objects.filter(fazenda=fazenda, user=request.user, is_active=True).prefetch_related('animais')
    else:
        fazenda = None
        lotes = Lote.objects.filter(user=request.user, is_active=True).prefetch_related('animais')
    
    # Adicionar contagem de animais para cada lote
    lotes_data = []
    total_animais_geral = 0
    for lote in lotes:
        animais_lote = lote.animais.filter(is_active=True)
        peso_total_kg = sum(animal.peso for animal in animais_lote)
        peso_total_arroba = Animal.converter_kg_para_arroba(peso_total_kg)
        n_animais = animais_lote.count()
        lotes_data.append({
            'lote': lote,
            'total_animais': n_animais,
            'peso_total_kg': peso_total_kg,
            'peso_total_arroba': peso_total_arroba,
        })
        total_animais_geral += n_animais
    
    fazendas = Fazenda.objects.filter(user=request.user)
    context = {
        'lotes_data': lotes_data,
        'fazendas': fazendas,
        'fazenda_selecionada': fazenda,
        'total_animais_geral': total_animais_geral,
    }
    return render(request, 'gado/overview_lotes.html', context)

@login_required
def mover_animais(request):
    """Interface para mover animais entre lotes com especificação de peso"""
    if request.method == 'POST':
        try:
            animal_ids = request.POST.getlist('animais')
            novo_lote_id = request.POST.get('novo_lote')
            peso_total_especificado = request.POST.get('peso_total', '')
            unidade_peso = request.POST.get('unidade_peso', 'kg')
            
            novo_lote = Lote.objects.get(id=novo_lote_id, user=request.user)
            animais_movidos = []
            peso_total_real = 0
            
            for animal_id in animal_ids:
                animal = Animal.objects.get(id=animal_id, user=request.user)
                animal.mover_para_lote(novo_lote)
                animais_movidos.append(animal.identificador)
                peso_total_real += animal.peso
            
            # Calcular peso em ambas as unidades - converter para float para evitar problemas de tipo
            peso_total_kg = float(peso_total_real)
            peso_total_arroba = Animal.converter_kg_para_arroba(peso_total_kg)
            
            # Verificar se peso especificado confere (se fornecido)
            if peso_total_especificado:
                peso_especificado = float(peso_total_especificado)
                if unidade_peso == 'arroba':
                    peso_especificado_kg = float(Animal.converter_arroba_para_kg(peso_especificado))
                else:
                    peso_especificado_kg = float(peso_especificado)
                
                diferenca = abs(peso_especificado_kg - peso_total_kg)
                if diferenca > 5:  # Tolerância de 5kg
                    messages.warning(request, 
                        f'Atenção: Peso especificado ({peso_especificado:.1f}{unidade_peso}) '
                        f'difere do peso real ({peso_total_kg:.1f}kg)')
            
            messages.success(request, 
                f'{len(animais_movidos)} animais movidos para {novo_lote.nome}! '
                f'Peso total: {peso_total_kg:.1f}kg ({peso_total_arroba:.1f}@)')
            
            return redirect('overview_piquetes')
            
        except Exception as e:
            messages.error(request, f'Erro ao mover animais: {str(e)}')
    
    lote_id = request.GET.get('lote')
    if lote_id:
        lote_origem = get_object_or_404(Lote, id=lote_id, user=request.user)
        animais = Animal.objects.filter(lote=lote_origem, user=request.user)
        outros_lotes = Lote.objects.filter(fazenda=lote_origem.fazenda, user=request.user).exclude(id=lote_id)
    else:
        lote_origem = None
        animais = Animal.objects.filter(user=request.user)
        outros_lotes = Lote.objects.filter(user=request.user)
    
    context = {
        'lote_origem': lote_origem,
        'animais': animais,
        'outros_lotes': outros_lotes,
    }
    return render(request, 'gado/mover_animais.html', context)

# ========== AJAX HELPERS ==========

@login_required
def get_lotes_by_fazenda(request):
    """Retorna lotes de uma fazenda específica (AJAX)"""
    fazenda_id = request.GET.get('fazenda_id')
    if fazenda_id:
        lotes = Lote.objects.filter(fazenda_id=fazenda_id, user=request.user).values('id', 'nome')
        return JsonResponse({'lotes': list(lotes)})
    return JsonResponse({'lotes': []})

@login_required
@require_POST
def excluir_animais_lote(request):
    ids = request.POST.getlist('animais_ids')
    lote_id = request.POST.get('lote_filtro')
    
    if not ids:
        messages.error(request, 'Nenhum animal selecionado para exclusão.')
        if lote_id:
            return redirect(f'{reverse("lista_animais")}?lote={lote_id}')
        return redirect('lista_animais')
    
    animais = Animal.objects.filter(id__in=ids, user=request.user, is_active=True)
    count = 0
    for animal in animais:
        animal.soft_delete()
        count += 1
    
    messages.success(request, f'{count} animal(is) excluído(s) com sucesso!')
    
    # Redirecionar de volta para o lote específico se veio de um filtro
    if lote_id:
        return redirect(f'{reverse("lista_animais")}?lote={lote_id}')
    return redirect('lista_animais')
