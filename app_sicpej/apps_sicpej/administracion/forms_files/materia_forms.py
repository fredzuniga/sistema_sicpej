from django import forms
from ..models import Materia

class MateriaForm(forms.ModelForm):
    estatus = forms.ChoiceField(
        choices=[('', '---------')] + list(Materia.ESTATUS),
        label='Estatus',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Materia
        fields = ['nombre', 'descripcion', 'estatus']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de materia'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción detallada de materia'
            }),
            'nota': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Notas sobre la materia'
            })
        }
        labels = {
            'descripcion': 'Descripción'
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Materia.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe una materia con este nombre")
        return nombre
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()