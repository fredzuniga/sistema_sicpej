from django import forms
from ..models import TipoJuicio, Materia

class TipoJuicioForm(forms.ModelForm):
    estatus = forms.ChoiceField(
        choices=[('', '---------')] + list(TipoJuicio.ESTATUS),
        label='Estatus',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = TipoJuicio
        fields = ['nombre', 'materia', 'descripcion', 'estatus']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de tipo de juicio'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción detallada de tipo de juicio'
            }),
            'nota': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Notas sobre el tipo de juicio'
            })
        }
        labels = {
            'materia': 'Materia',
            'descripcion': 'Descripción'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['materia'].queryset = Materia.objects.filter(estatus=1).order_by('nombre')
        self.fields['materia'].label_from_instance = lambda obj: obj.nombre
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if TipoJuicio.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un tipo de juicio con este nombre")
        return nombre