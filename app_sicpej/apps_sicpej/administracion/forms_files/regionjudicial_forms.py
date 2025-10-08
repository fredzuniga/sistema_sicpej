from django import forms
from ..models import Materia, RegionJudicial, ArchivoRegional

class RegionJudicialForm(forms.ModelForm):
    estatus = forms.ChoiceField(
        choices=[('', '---------')] + list(RegionJudicial.ESTATUS),
        label='Estatus',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = RegionJudicial
        fields = ['nombre', 'descripcion','materia','estatus']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Distrito Judicial'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción del distrito judicial'
            }),
            'nota': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Notas adicionales sobre este distrito'
            }),
        }
        labels = {
            'descripcion': 'Descripción'
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if RegionJudicial.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un distrito judicial con este nombre")
        return nombre
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['materia'].queryset = Materia.objects.filter(estatus=1).order_by('pk')
        self.fields['materia'].label_from_instance = lambda obj: obj.nombre
        #self.fields['archivo_regional'].queryset = ArchivoRegional.objects.filter(estatus=1).order_by('pk')
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()