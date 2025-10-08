# forms.py

from django import forms
from ..models import TipoCuadernillo

class TipoCuadernilloForm(forms.ModelForm):
    class Meta:
        model = TipoCuadernillo
        fields = ['nombre', 'descripcion', 'nota', 'estatus']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del tipo de cuadernillo'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción detallada del tipo de cuadernillo'
            }),
            'nota': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Notas sobre tipo de cuadernillo'
            }),
            'estatus': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'descripcion': 'Descripción'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()