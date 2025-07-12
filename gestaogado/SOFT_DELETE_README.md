# Sistema de Soft Delete - Documentação

## Visão Geral

O sistema de **Soft Delete** foi implementado para permitir que você possa "deletar" registros sem removê-los permanentemente do banco de dados. Apenas administradores podem fazer exclusões permanentes.

## Como Funciona

### 1. Campo `is_active`
- Todos os modelos principais (`Animal` e `Fazenda`) agora têm um campo `is_active`
- Por padrão, todos os registros são criados com `is_active=True`
- Quando você "deleta" um registro, ele é marcado como `is_active=False`

### 2. Managers Customizados
- **`objects`** (Manager padrão): Retorna apenas registros ativos (`is_active=True`)
- **`all_objects`**: Retorna todos os registros (ativos e inativos)

### 3. Métodos Disponíveis

#### Para Animais:
```python
# Soft delete (marca como inativo)
animal.soft_delete()

# Restaurar (marca como ativo)
animal.restore()

# Listar apenas ativos
Animal.objects.all()

# Listar todos (incluindo deletados)
Animal.all_objects.all()
```

#### Para Fazendas:
```python
# Soft delete (marca como inativo)
fazenda.soft_delete()

# Restaurar (marca como ativo)
fazenda.restore()

# Listar apenas ativas
Fazenda.objects.all()

# Listar todas (incluindo deletadas)
Fazenda.all_objects.all()
```

## Funcionalidades por Perfil

### Usuário Comum
- **Pode visualizar**: Apenas registros ativos
- **Pode "deletar"**: Registros são marcados como inativos (soft delete)
- **Não pode**: Ver registros deletados ou fazer exclusões permanentes

### Administrador (is_staff=True)
- **Pode visualizar**: Todos os registros (ativos e inativos)
- **Pode restaurar**: Registros marcados como deletados
- **Pode deletar permanentemente**: Remover registros definitivamente do banco
- **Pode gerenciar**: Status ativo/inativo via Django Admin

## URLs Disponíveis

### Animais
- `/gado/` - Lista animais ativos
- `/gado/adicionar/` - Adicionar novo animal
- `/gado/deletar/<id>/` - Soft delete de animal
- `/gado/admin/deletados/` - Lista animais deletados (só admin)
- `/gado/admin/restaurar/<id>/` - Restaurar animal (só admin)
- `/gado/admin/deletar-permanente/<id>/` - Deletar permanentemente (só admin)

### Fazendas
- `/fazendas/` - Lista fazendas ativas
- `/fazendas/adicionar/` - Adicionar nova fazenda
- `/fazendas/deletar/<id>/` - Soft delete de fazenda
- `/fazendas/admin/deletadas/` - Lista fazendas deletadas (só admin)
- `/fazendas/admin/restaurar/<id>/` - Restaurar fazenda (só admin)
- `/fazendas/admin/deletar-permanente/<id>/` - Deletar permanentemente (só admin)

## Django Admin

No Django Admin, os administradores podem:
- Ver todos os registros com filtro por status ativo/inativo
- Usar ações em lote para marcar registros como ativo/inativo
- Fazer exclusões permanentes quando necessário

## Vantagens

1. **Segurança**: Dados não são perdidos por engano
2. **Auditoria**: Histórico completo mantido
3. **Recuperação**: Fácil restauração de dados
4. **Controle**: Apenas administradores podem fazer exclusões definitivas

## Exemplos de Uso

### Usuário comum deletando um animal:
```python
# Na view deletar_animal
animal = Animal.objects.get(id=animal_id)
animal.soft_delete()  # Animal fica inativo, mas permanece no banco
```

### Administrador vendo todos os registros:
```python
# Ver todos os animais (incluindo deletados)
todos_animais = Animal.all_objects.all()

# Ver apenas animais deletados
animais_deletados = Animal.all_objects.filter(is_active=False)
```

### Restaurando um registro:
```python
# Na view restaurar_animal
animal = Animal.all_objects.get(id=animal_id, is_active=False)
animal.restore()  # Animal volta a ficar ativo
```

## Migrações Aplicadas

As seguintes migrações foram criadas e aplicadas:
- `fazendascdst/migrations/0002_fazenda_is_active.py`
- `gado/migrations/0002_animal_is_active.py`

Todos os registros existentes foram automaticamente marcados como `is_active=True`.
