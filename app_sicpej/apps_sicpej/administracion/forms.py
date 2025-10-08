from django import forms
from django.utils import timezone
from .models import ArchivoRegional, Juzgado, Municipio, NombreJuzgadoHistorico, Instancia, TipoJuzgado, Materia, DistritoJudicial, RegionJudicial

class ArchivoRegionalForm(forms.ModelForm):
    class Meta:
        model = ArchivoRegional
        exclude = ['clave','nombre_corto']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class JuzgadoForm(forms.ModelForm):
    guardar_historico = forms.BooleanField(
        required=False,
        label="Guardar cambio nombre",
        help_text="Marque esta casilla si desea guardar el nombre anterior en el historial"
    )
    motivo_cambio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        label="Motivo del cambio",
        help_text="Opcional: especifique el motivo del cambio de nombre"
    )
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
        choices=[('', '---------')] + list(Juzgado.ESTATUS),
        label='Estatus',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Juzgado
        #fields = '__all__'
        exclude = ['nombre_corto','clave_interna','creado_por','actualizado_por','tipo_juzgado']
        labels = {
            'locacion': 'Locación',
            'direccion': 'Dirección',
            'descripcion': 'Descripción',
            #'tipo_juzgado': 'Materia'
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
            'municipio','archivo_regional', 'distrito_judicial', 'region_judicial', 'materia', 'estatus'
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

        if not self.instance.pk:
            self.fields.pop('guardar_historico')
            self.fields.pop('motivo_cambio')
        for field_name, field in self.fields.items():
            if field_name != 'guardar_historico':
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()
    
    def save(self, commit=True):
        juzgado = super().save(commit=False)
        if commit:
            juzgado.save()

            if NombreJuzgadoHistorico.objects.filter( juzgado=juzgado ).count() == 0:
                NombreJuzgadoHistorico.objects.create(
                    juzgado=juzgado,
                    nombre=self.initial.get('nombre', juzgado.nombre),
                    fecha_inicio=timezone.now().date(),
                    activo=True
                )
            
            if self.cleaned_data.get('guardar_historico') and self.instance.pk:
                # Desactivar cualquier registro histórico activo previo
                NombreJuzgadoHistorico.objects.filter(
                    juzgado=juzgado,
                    activo=True
                ).update(
                    fecha_fin=timezone.now().date(),
                    activo=False
                )
                
                # Crear nuevo registro histórico
                NombreJuzgadoHistorico.objects.create(
                    juzgado=juzgado,
                    nombre=self.initial.get('nombre', juzgado.nombre),
                    fecha_inicio=timezone.now().date(),
                    usuario_registro=self.request.user if self.request else None,
                    motivo_cambio=self.cleaned_data.get('motivo_cambio', ''),
                    activo=True
                )
        
        return juzgado