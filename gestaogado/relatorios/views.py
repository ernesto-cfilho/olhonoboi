from django.shortcuts import render
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta
from gado.models import Animal, Vacinacao
from fazendascdst.models import Fazenda, Lote
from estoque.models import Produto, Movimentacao_estoque
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

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

# Funções de exportação
def exportar_pdf_relatorio_mensal(request):
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    
    # Dados do mês atual
    animais_mes = Animal.objects.filter(data_entrada__gte=inicio_mes)
    vacinacoes_mes = Vacinacao.objects.filter(data_de_aplicacao__gte=inicio_mes)
    movimentacoes_mes = Movimentacao_estoque.objects.filter(data__gte=inicio_mes)
    
    # Criar PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Título
    elements.append(Paragraph(f"Relatório Mensal - {hoje.strftime('%B %Y')}", title_style))
    elements.append(Spacer(1, 20))
    
    # Resumo
    resumo_data = [
        ['Métrica', 'Valor'],
        ['Total de Animais', str(animais_mes.count())],
        ['Total de Vacinações', str(vacinacoes_mes.count())],
        ['Movimentações de Estoque', str(movimentacoes_mes.count())],
    ]
    
    resumo_table = Table(resumo_data)
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(resumo_table)
    elements.append(Spacer(1, 20))
    
    # Animais do mês
    if animais_mes.exists():
        elements.append(Paragraph("Animais Adicionados no Mês", styles['Heading2']))
        animais_data = [['ID', 'Fazenda', 'Lote', 'Tipo', 'Peso (kg)', 'Data Entrada']]
        
        for animal in animais_mes:
            animais_data.append([
                str(animal.identificador or 'N/A'),
                animal.fazenda.nome,
                animal.lote.nome if animal.lote else 'N/A',
                animal.get_tipo_display(),
                f"{animal.peso:.1f}",
                animal.data_entrada.strftime('%d/%m/%Y')
            ])
        
        animais_table = Table(animais_data)
        animais_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(animais_table)
        elements.append(Spacer(1, 20))
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_mensal_{hoje.strftime("%Y_%m")}.pdf"'
    return response

def exportar_excel_relatorio_mensal(request):
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    
    # Dados do mês atual
    animais_mes = Animal.objects.filter(data_entrada__gte=inicio_mes)
    vacinacoes_mes = Vacinacao.objects.filter(data_de_aplicacao__gte=inicio_mes)
    movimentacoes_mes = Movimentacao_estoque.objects.filter(data__gte=inicio_mes)
    
    # Criar workbook
    wb = Workbook()
    
    # Planilha de resumo
    ws1 = wb.active
    ws1.title = "Resumo"
    
    # Estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    # Título
    ws1['A1'] = f"Relatório Mensal - {hoje.strftime('%B %Y')}"
    ws1['A1'].font = Font(bold=True, size=16)
    ws1.merge_cells('A1:F1')
    
    # Resumo
    ws1['A3'] = "Métrica"
    ws1['B3'] = "Valor"
    ws1['A3'].font = header_font
    ws1['B3'].font = header_font
    ws1['A3'].fill = header_fill
    ws1['B3'].fill = header_fill
    
    ws1['A4'] = "Total de Animais"
    ws1['B4'] = animais_mes.count()
    ws1['A5'] = "Total de Vacinações"
    ws1['B5'] = vacinacoes_mes.count()
    ws1['A6'] = "Movimentações de Estoque"
    ws1['B6'] = movimentacoes_mes.count()
    
    # Planilha de animais
    ws2 = wb.create_sheet("Animais")
    ws2['A1'] = "ID"
    ws2['B1'] = "Fazenda"
    ws2['C1'] = "Lote"
    ws2['D1'] = "Tipo"
    ws2['E1'] = "Peso (kg)"
    ws2['F1'] = "Data Entrada"
    
    # Aplicar estilo ao cabeçalho
    for cell in ws2[1]:
        cell.font = header_font
        cell.fill = header_fill
    
    # Dados dos animais
    row = 2
    for animal in animais_mes:
        ws2[f'A{row}'] = animal.identificador or 'N/A'
        ws2[f'B{row}'] = animal.fazenda.nome
        ws2[f'C{row}'] = animal.lote.nome if animal.lote else 'N/A'
        ws2[f'D{row}'] = animal.get_tipo_display()
        ws2[f'E{row}'] = float(animal.peso)
        ws2[f'F{row}'] = animal.data_entrada.strftime('%d/%m/%Y')
        row += 1
    
    # Ajustar largura das colunas
    for column in ws2.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws2.column_dimensions[column_letter].width = adjusted_width
    
    # Salvar
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="relatorio_mensal_{hoje.strftime("%Y_%m")}.xlsx"'
    return response

def exportar_pdf_relatorio_anual(request):
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
    
    # Criar PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1
    )
    
    # Título
    elements.append(Paragraph(f"Relatório Anual - {hoje.year}", title_style))
    elements.append(Spacer(1, 20))
    
    # Resumo anual
    resumo_data = [
        ['Métrica', 'Valor'],
        ['Total de Animais (Ano)', str(animais_ano.count())],
        ['Total de Vacinações (Ano)', str(vacinacoes_ano.count())],
    ]
    
    resumo_table = Table(resumo_data)
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(resumo_table)
    elements.append(Spacer(1, 20))
    
    # Animais por mês
    elements.append(Paragraph("Animais por Mês", styles['Heading2']))
    animais_mes_data = [['Mês', 'Total de Animais']]
    
    for item in animais_por_mes:
        animais_mes_data.append([item['nome_mes'], str(item['total'])])
    
    animais_mes_table = Table(animais_mes_data)
    animais_mes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(animais_mes_table)
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_anual_{hoje.year}.pdf"'
    return response

def exportar_excel_relatorio_anual(request):
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
    
    # Criar workbook
    wb = Workbook()
    
    # Planilha de resumo
    ws1 = wb.active
    ws1.title = "Resumo Anual"
    
    # Estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    # Título
    ws1['A1'] = f"Relatório Anual - {hoje.year}"
    ws1['A1'].font = Font(bold=True, size=16)
    ws1.merge_cells('A1:C1')
    
    # Resumo
    ws1['A3'] = "Métrica"
    ws1['B3'] = "Valor"
    ws1['A3'].font = header_font
    ws1['B3'].font = header_font
    ws1['A3'].fill = header_fill
    ws1['B3'].fill = header_fill
    
    ws1['A4'] = "Total de Animais (Ano)"
    ws1['B4'] = animais_ano.count()
    ws1['A5'] = "Total de Vacinações (Ano)"
    ws1['B5'] = vacinacoes_ano.count()
    
    # Planilha de animais por mês
    ws2 = wb.create_sheet("Animais por Mês")
    ws2['A1'] = "Mês"
    ws2['B1'] = "Total de Animais"
    
    # Aplicar estilo ao cabeçalho
    for cell in ws2[1]:
        cell.font = header_font
        cell.fill = header_fill
    
    # Dados dos animais por mês
    row = 2
    for item in animais_por_mes:
        ws2[f'A{row}'] = item['nome_mes']
        ws2[f'B{row}'] = item['total']
        row += 1
    
    # Ajustar largura das colunas
    for column in ws2.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws2.column_dimensions[column_letter].width = adjusted_width
    
    # Salvar
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="relatorio_anual_{hoje.year}.xlsx"'
    return response