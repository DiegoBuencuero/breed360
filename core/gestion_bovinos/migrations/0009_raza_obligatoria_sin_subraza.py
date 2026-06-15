from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_bovinos', '0008_eliminar_raza_animal'),
    ]

    operations = [
        # Paso 1: agregar raza como nullable temporalmente
        migrations.AddField(
            model_name='animalbovino',
            name='raza',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='animales',
                to='gestion_bovinos.razabovino',
                verbose_name='Raza',
            ),
        ),
        # Paso 2: quitar subraza de animalbovino
        migrations.RemoveField(
            model_name='animalbovino',
            name='subraza',
        ),
    ]
