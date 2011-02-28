from cmsplugin_rst.models import RstPluginModel
from django import forms


help_text = '<a href="http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html">Reference</a>'

class RstPluginForm(forms.ModelForm):
    body = forms.CharField(
                widget=forms.Textarea(attrs={
                    'rows':30,
                    'cols':80,
                    'style':'font-family:monospace'
                }),
                help_text=help_text
            )
    
    class Meta:
        model = RstPluginModel