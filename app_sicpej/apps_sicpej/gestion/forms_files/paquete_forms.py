from django import forms
from apps_sicpej.administracion.models import Juzgado
from ..models import Paquete

class PaqueteForm(forms.ModelForm):
    class Meta:
        model = Paquete
        fields = ['topografia'] #'nombre', 'clave', 'descripcion', 'nota',
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del paquete'
            }),
            'clave': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Clave única del paquete'
            }),
            'topografia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Topografía'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción detallada del paquete'
            }),
            'nota': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Notas sobre este paquete'
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
        #self.fields['juzgado'].queryset = Juzgado.objects.filter(estatus=1).order_by('descripcion')
        #self.fields['juzgado'].label_from_instance = lambda obj: f"{obj.nombre} - {obj.municipio.descripcion}/{obj.archivo_regional.nombre}"
        #self.fields['estatus'].choices = Paquete.ESTATUS
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()