
# Generated migration for certificate field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0002_enrollment'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomcompletion',
            name='certificate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='lms.certificate', verbose_name='Certificate'),
        ),
    ]
