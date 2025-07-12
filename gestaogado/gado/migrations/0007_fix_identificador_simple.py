# Simple fix for identificador issues

from django.db import migrations, models

def simple_fix_identificadores(apps, schema_editor):
    """Simple fix for identificador values"""
    Animal = apps.get_model('gado', 'Animal')
    Lote = apps.get_model('fazendascdst', 'Lote')
    Fazenda = apps.get_model('fazendascdst', 'Fazenda')
    
    # First, ensure all animals have lotes
    for fazenda in Fazenda.objects.all():
        animals_without_lotes = Animal.objects.filter(fazenda=fazenda, lote__isnull=True)
        
        if animals_without_lotes.exists():
            # Create or get default lote
            default_lote, created = Lote.objects.get_or_create(
                fazenda=fazenda,
                nome="Lote 1",
                defaults={'is_active': True}
            )
            # Assign all animals without lotes to this default lote
            animals_without_lotes.update(lote=default_lote)
    
    # Simple approach: just assign sequential numbers to all animals
    counter = 1
    for animal in Animal.objects.all().order_by('id'):
        animal.identificador = counter
        animal.save()
        counter += 1

def reverse_simple_fix(apps, schema_editor):
    """Cannot reverse this migration"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('gado', '0006_fix_data_and_add_unique_constraint'),
    ]

    operations = [
        migrations.RunPython(simple_fix_identificadores, reverse_simple_fix),
    ]