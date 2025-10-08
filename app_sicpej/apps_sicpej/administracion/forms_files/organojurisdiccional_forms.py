from django import forms
from django.utils import timezone
from ..models import OrganoJurisdiccional, ArchivoRegional, Juzgado, Municipio, NombreJuzgadoHistorico, Instancia, TipoJuzgado, Materia, DistritoJudicial, RegionJudicial


class OrganoJurisdiccionalForm(forms.ModelForm):
    descripcion = forms.CharField(
        label='Descripción',
        widget=forms.Textarea(attrs={
            'cols': 4,   # Este valor representa el número de columnas (ancho)
            'rows': 3    # Opcional: controla la altura
        })
    )
    
    """tipo = forms.ChoiceField(
        choices=[('', '---------')] + [(k, v.capitalize()) for k, v in Juzgado.TIPO],
        label='Tipo de juzgado',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    ) """

    estatus = forms.ChoiceField(
        choices=[('', '---------')] + list(OrganoJurisdiccional.ESTATUS),
        label='Estatus',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = OrganoJurisdiccional
        #fields = '__all__'
        fields = [
            'nombre',
            'descripcion',
            'materia',
            'archivo_regional',
            'instancia',
            'municipio',
            'locacion',
            'direccion',
            'distrito_judicial',
            'region_judicial',
            'estatus'
        ]
        #exclude = ['nombre_corto','clave_interna','creado_por','actualizado_por','tipo']
        labels = {
            'locacion': 'Locación',
            'direccion': 'Dirección',
            'descripcion': 'Descripción',
            'materia': 'Materia',
            'distrito_judicial':'Distrito judicial',
            'region_judicial':'Región judicial'
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        self.one_column_fields = [
            
        ]

        self.two_column_fields = [
            'municipio','archivo_regional', 'distrito_judicial', 'region_judicial', 'materia', 'estatus','instancia'
        ]

        self.three_column_fields = [
            
        ]

        self.four_column_fields = [
            
        ]

        # Puedes personalizar los querysets si es necesario
        #self.fields['tipo_juzgado'].queryset = TipoJuzgado.objects.filter(estatus=1).order_by('pk')
        #self.fields['tipo_juzgado'].label_from_instance = lambda obj: obj.nombre
        self.fields['materia'].queryset = Materia.objects.filter(estatus=1).order_by('pk')
        self.fields['materia'].label_from_instance = lambda obj: obj.nombre
        self.fields['municipio'].queryset = Municipio.objects.all().order_by('pk')
        self.fields['municipio'].label_from_instance = lambda obj: obj.descripcion
        self.fields['archivo_regional'].queryset = ArchivoRegional.objects.filter(estatus=1).order_by('pk')
        self.fields['distrito_judicial'].queryset = DistritoJudicial.objects.filter(estatus=1).order_by('pk')
        self.fields['region_judicial'].queryset = RegionJudicial.objects.filter(estatus=1).order_by('pk')
        self.fields['instancia'].queryset = Instancia.objects.filter(estatus=1).order_by('pk')

        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()