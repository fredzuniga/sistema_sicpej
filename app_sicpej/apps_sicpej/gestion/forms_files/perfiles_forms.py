# forms.py

from django import forms
from ..models import Perfil

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nombre', 'descripcion', 'tipo_perfil']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del perfil'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción del perfil'
            }),
            'tipo_perfil': forms.Select(attrs={
                'class': 'form-select'
            }),
            'visibilidad_paquetes': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nombre': 'Nombre del perfil',
            'descripcion': 'Descripción',
            'tipo_perfil': 'Tipo de perfil',
            'visibilidad_paquetes': 'Visible en paquetes'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mejora para asegurarse de aplicar clases base si no están incluidas
        for field_name, field in self.fields.items():
            widget = field.widget
            if not isinstance(widget, forms.CheckboxInput):
                existing_class = widget.attrs.get('class', '')
                widget.attrs['class'] = f'{existing_class} form-control'.strip()
