import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_rst', '0003_field_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rstpluginmodel',
            name='cmsplugin_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='%(app_label)s_%(class)s', serialize=False, to='cms.cmsplugin'),
        ),
    ]
