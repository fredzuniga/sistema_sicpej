from django import forms
from ..models import UsuarioPerfil

class UsuarioPerfilForm(forms.ModelForm):
    class Meta:
        model = UsuarioPerfil
        fields = [
            'usuario',
            'perfil',
            'estatus',
            'archivo_regional',
            #'organo_jurisdiccional',
            #'fecha_inicio',
            #'fecha_fin'
        ]
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'perfil': forms.Select(attrs={'class': 'form-select'}),
            'estatus': forms.Select(attrs={'class': 'form-select'}),
            'archivo_regional': forms.Select(attrs={'class': 'form-select'}),
            'organo_jurisdiccional': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'