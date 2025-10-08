from django import forms
from ..models import TipoJuzgado

class TipoJuzgadoForm(forms.ModelForm):
    estatus = forms.ChoiceField(
        choices=[('', '---------')] + list(TipoJuzgado.ESTATUS),
        label='Estatus',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = TipoJuzgado
        fields = ['nombre', 'descripcion', 'nota', 'estatus']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Familiar, Civil, Penal'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción detallada de tipo de materia de juzgado'
            }),
            'nota': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Notas sobre el tipo de materia de juzgado'
            })
        }
        labels = {
            'descripcion': 'Descripción'
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if TipoJuzgado.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un tipo de juzgado con este nombre")
        return nombre
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()