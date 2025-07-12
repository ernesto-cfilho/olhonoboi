# Simple approach - just do the database schema change

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('fazendascdst', '0005_delete_piquete_alter_lote_unique_together'),
        ('gado', '0005_remove_animal_piquete_animal_lote_and_more'),
    ]

    operations = [
        # Skip the data migration for now - we'll handle it manually
    ]