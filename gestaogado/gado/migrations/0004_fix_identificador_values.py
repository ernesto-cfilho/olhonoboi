# Empty migration - data fix moved to 0006

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('gado', '0003_animal_piquete_animal_tipo'),
    ]

    operations = [
        # No operations - this is now just a placeholder
    ]