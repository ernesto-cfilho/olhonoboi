from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import Animal, Vacina, Vacinacao
from fazendascdst.models import Fazenda, Lote
from django.utils import timezone
from django.http import JsonResponse

@login_required
def lista_animais(request):
    animais = Animal.objects.all().select_related('fazenda')  
    return render(request, 'gado/lista.html', {'animais': animais})

@login_required
def adicionar_animal(request):
    if request.method == 'POST':
        try:
            fazenda_id = request.POST.get('fazenda')
            lote_id = request.POST.get('lote')
            identificador = request.POST.get('identificador')
            tipo = request.POST.get('tipo', 'CORTE')
            data_entrada = request.POST.get('data_entrada') or timezone.now().date()
            peso = request.POST.get('peso')
            
            fazenda = Fazenda.objects.get(id=fazenda_id)
            lote = Lote.objects.get(id=lote_id)
            
            # Se identificador não fornecido, gerar automaticamente
            if not identificador:
                ultimo_animal = Animal.objects.filter(fazenda=fazenda).order_by('identificador').last()
                identificador = ultimo_animal.identificador + 1 if ultimo_animal and ultimo_animal.identificador else 1
            
            # Verificar capacidade máxima do lote
            if lote.capacidade_maxima:
                animais_no_lote = lote.animais.count()
                if animais_no_lote >= lote.capacidade_maxima:
                    messages.error(request, f'Lote {lote.nome} já está na capacidade máxima ({lote.capacidade_maxima} animais)!')
                    raise Exception('Capacidade máxima do lote excedida')
            
            animal = Animal.objects.create(
                fazenda=fazenda,
                lote=lote,
                identificador=int(identificador),
                tipo=tipo,
                data_entrada=data_entrada,
                peso=peso
            )
            
            messages.success(request, f'Animal {identificador} adicionado com sucesso!')
            return redirect('lista_animais')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar animal: {str(e)}')
    
    fazendas = Fazenda.objects.all()
    return render(request, 'gado/adicionar.html', {'fazendas': fazendas})

def deletar_animal(request, animal_id):
    if request.method == 'POST':
        try:
            animal = Animal.objects.get(id=animal_id)
            identificador = animal.identificador
            animal.soft_delete()  # Usar soft delete ao invés de delete()
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
    vacinas = Vacina.objects.all()
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
                validade_dias=validade_dias
            )
            
            messages.success(request, f'Vacina {nome} adicionada com sucesso!')
            return redirect('lista_vacinas')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar vacina: {str(e)}')
    
    return render(request, 'gado/vacinas/adicionar.html')

@login_required
def lista_vacinacoes(request):
    """Lista todas as vacinações"""
    vacinacoes = Vacinacao.objects.all().select_related('animal', 'vacina')
    return render(request, 'gado/vacinacoes/lista.html', {'vacinacoes': vacinacoes})

@login_required
def adicionar_vacinacao(request):
    """Adiciona uma nova vacinação"""
    if request.method == 'POST':
        try:
            animal_id = request.POST.get('animal')
            vacina_id = request.POST.get('vacina')
            data_aplicacao = request.POST.get('data_aplicacao')
            
            animal = Animal.objects.get(id=animal_id)
            vacina = Vacina.objects.get(id=vacina_id)
            
            vacinacao = Vacinacao.objects.create(
                animal=animal,
                vacina=vacina,
                data_de_aplicacao=data_aplicacao
            )
            
            messages.success(request, f'Vacinação de {animal.identificador} com {vacina.nome} registrada!')
            return redirect('lista_vacinacoes')
            
        except Exception as e:
            messages.error(request, f'Erro ao registrar vacinação: {str(e)}')
    
    animais = Animal.objects.all()
    vacinas = Vacina.objects.all()
    return render(request, 'gado/vacinacoes/adicionar.html', {
        'animais': animais,
        'vacinas': vacinas
    })

# ========== VIEWS PARA BATCH INSERT ==========

@login_required
def batch_insert_animais(request):
    """Formulário para inserção em lote de animais com peso total"""
    if request.method == 'POST':
        try:
            fazenda_id = request.POST.get('fazenda')
            lote_id = request.POST.get('lote')
            tipo = request.POST.get('tipo', 'CORTE')
            data_entrada = request.POST.get('data_entrada') or timezone.now().date()
            
            # Novos campos para inserção em lote
            quantidade_animais = int(request.POST.get('quantidade_animais', 0))
            peso_total = float(request.POST.get('peso_total', 0))
            unidade_peso = request.POST.get('unidade_peso', 'kg')  # kg ou arroba
            
            if quantidade_animais <= 0 or peso_total <= 0:
                messages.error(request, 'Quantidade de animais e peso total devem ser maiores que zero!')
                raise Exception('Valores inválidos')
            
            fazenda = Fazenda.objects.get(id=fazenda_id)
            lote = Lote.objects.get(id=lote_id)
            
            # Converter peso total para kg se estiver em arroba
            if unidade_peso == 'arroba':
                peso_total_kg = Animal.converter_arroba_para_kg(peso_total)
            else:
                peso_total_kg = peso_total
            
            # Calcular peso médio por animal
            peso_medio_kg = peso_total_kg / quantidade_animais
            
            # Verificar capacidade máxima do lote
            if lote.capacidade_maxima:
                animais_no_lote = lote.animais.count()
                if (animais_no_lote + quantidade_animais) > lote.capacidade_maxima:
                    messages.error(request, f'Lote {lote.nome} não tem capacidade para {quantidade_animais} animais! Capacidade atual: {lote.capacidade_maxima - animais_no_lote} vagas disponíveis.')
                    raise Exception('Capacidade máxima do lote excedida')
            
            # Criar animais sem identificadores automáticos
            animais_criados = []
            for i in range(quantidade_animais):
                animal = Animal.objects.create(
                    fazenda=fazenda,
                    lote=lote,
                    identificador=None,  # Deixar identificador como None para ser preenchido pelo cliente
                    tipo=tipo,
                    data_entrada=data_entrada,
                    peso=peso_medio_kg
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
    
    fazendas = Fazenda.objects.all()
    return render(request, 'gado/batch_insert.html', {'fazendas': fazendas})

# ========== VIEWS PARA PIQUETES ==========

@login_required
def overview_piquetes(request):
    """Overview dos lotes com contagem de animais"""
    fazenda_id = request.GET.get('fazenda')
    
    if fazenda_id:
        fazenda = get_object_or_404(Fazenda, id=fazenda_id)
        lotes = Lote.objects.filter(fazenda=fazenda).prefetch_related('animais')
    else:
        fazenda = None
        lotes = Lote.objects.all().prefetch_related('animais')
    
    # Adicionar contagem de animais para cada lote
    lotes_data = []
    for lote in lotes:
        animais_lote = lote.animais.all()
        peso_total_kg = sum(animal.peso for animal in animais_lote)
        peso_total_arroba = Animal.converter_kg_para_arroba(peso_total_kg)
        
        lotes_data.append({
            'lote': lote,
            'total_animais': animais_lote.count(),
            'gado_corte': animais_lote.filter(tipo='CORTE').count(),
            'gado_leite': animais_lote.filter(tipo='LEITE').count(),
            'peso_total_kg': peso_total_kg,
            'peso_total_arroba': peso_total_arroba,
        })
    
    fazendas = Fazenda.objects.all()
    context = {
        'lotes_data': lotes_data,
        'fazendas': fazendas,
        'fazenda_selecionada': fazenda,
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
            
            novo_lote = Lote.objects.get(id=novo_lote_id)
            animais_movidos = []
            peso_total_real = 0
            
            for animal_id in animal_ids:
                animal = Animal.objects.get(id=animal_id)
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
        lote_origem = get_object_or_404(Lote, id=lote_id)
        animais = Animal.objects.filter(lote=lote_origem)
        outros_lotes = Lote.objects.filter(fazenda=lote_origem.fazenda).exclude(id=lote_id)
    else:
        lote_origem = None
        animais = Animal.objects.all()
        outros_lotes = Lote.objects.all()
    
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
        lotes = Lote.objects.filter(fazenda_id=fazenda_id).values('id', 'nome')
        return JsonResponse({'lotes': list(lotes)})
    return JsonResponse({'lotes': []})
