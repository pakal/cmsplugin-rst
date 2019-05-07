# Generated by Django 2.1.8 on 2019-05-07 11:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmsplugin_rst', '0002_rstpluginmodel_header_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rstpluginmodel',
            name='body',
            field=models.TextField(help_text='<a target="_blank" href="http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html">Restructuredtext Reference</a>'),
        ),
        migrations.AlterField(
            model_name='rstpluginmodel',
            name='cmsplugin_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='cmsplugin_rst_rstpluginmodel', serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='rstpluginmodel',
            name='header_level',
            field=models.PositiveIntegerField(blank=True, help_text='If >0, specifies at which level the headings start.', null=True),
        ),
        migrations.AlterField(
            model_name='rstpluginmodel',
            name='name',
            field=models.CharField(blank=True, help_text='Used to identify your plugin instance in page structure.', max_length=255),
        ),
    ]