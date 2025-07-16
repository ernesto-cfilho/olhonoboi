#!/usr/bin/env python
# pyright: reportAttributeAccessIssue=false
"""
Script para configurar grupos de usuários no sistema
Execute: python manage.py shell < setup_grupos.py
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from gado.models import Animal, Vacina, Vacinacao
from fazendascdst.models import Fazenda

print("=== CONFIGURANDO GRUPOS DE USUÁRIOS ===\n")

# 1. Criar grupo "Funcionários"
grupo_funcionarios, created = Group.objects.get_or_create(name='Funcionários')
if created:
    print("✅ Grupo 'Funcionários' criado")
else:
    print("ℹ️ Grupo 'Funcionários' já existe")

# 2. Definir permissões para funcionários
permissoes_funcionarios = [
    # Animais - pode adicionar e visualizar
    'add_animal',
    'view_animal',
    
    # Vacinas - pode adicionar e visualizar  
    'add_vacina',
    'view_vacina',
    
    # Vacinações - pode adicionar e visualizar
    'add_vacinacao',
    'view_vacinacao',
    
    # Fazendas - apenas visualizar
    'view_fazenda',
]

# 3. Atribuir permissões ao grupo
for perm_code in permissoes_funcionarios:
    try:
        # Encontrar a permissão
        permission = Permission.objects.get(codename=perm_code)
        grupo_funcionarios.permissions.add(permission)
        print(f"✅ Permissão '{perm_code}' adicionada aos funcionários")
    except Permission.DoesNotExist:
        print(f"❌ Permissão '{perm_code}' não encontrada")

print(f"\n📊 Total de permissões para funcionários: {grupo_funcionarios.permissions.count()}")

print("\n=== GRUPOS CONFIGURADOS ===")
print("👥 Funcionários: Podem adicionar animais, vacinas e vacinações")
print("👑 Administradores (is_staff=True): Controle total do sistema")

print("\n=== COMO USAR ===")
print("1. Crie usuários no admin (/admin/)")
print("2. Adicione usuários normais ao grupo 'Funcionários'")
print("3. Marque administradores com 'is_staff=True'")
print("4. Pronto! O sistema controlará automaticamente os acessos")

print("\n=== CONFIGURAÇÃO CONCLUÍDA ===")
