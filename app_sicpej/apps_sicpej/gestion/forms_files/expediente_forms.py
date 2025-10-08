from django import forms
from ..models import Expediente, Paquete
from django.core.exceptions import ValidationError

class ExpedienteForm(forms.ModelForm):
    tomo = forms.BooleanField( required=False, label="Tomo",
        #help_text="Marque esta casilla si es un tomo"
    )

    original = forms.BooleanField( required=False, label="Original",
        #help_text="Marque esta casilla si es un tomo"
    )

    class Meta:
        model = Expediente
        fields = '__all__'
        fields = [
            'instancia',
            'materia',
            'distrito_judicial',
            #'municipio',
            'expediente_toca',
            'tomo',
            'numero_tomo',
            #'juzgado'
            'juicio_delito',
            'actor',
            'demandado',
            'fecha_inicio',
            'fecha_sentencia',
            'fecha_archivo',
            'juez',
            'secretario',
            'beneficiario',
            'fecha_convenio',
            'rango_folio_inicial',
            'rango_folio_final',
            'original',
            'duplicado',
            'cuadernillo',
            'acumulado',
            'avocamiento',
            #'numero_acumulado',
            'concluido',
            'fecha_concluido',
            'fecha_ejecutoria',
            'observaciones',
            'medida_centimetros',
            'documento_prestamo',
            'oficio_atencion',
            'numero_oficio',
            'fecha_prestamo'
        ]
        #exclude = ['creado_por', 'actualizado_por', 'fecha_creacion', 'fecha_actualizacion', 'paquete']
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de expediente'
            }),
            'observaciones': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Observaciones del expediente'
            }),
            'fecha_registro': forms.HiddenInput(),

            'paquete': forms.Select(attrs={
                'class': 'form-select select2'
            }),
            'instancia': forms.Select(attrs={
                'class': 'form-select select2'
            }),
            'materia': forms.Select(attrs={
                'class': 'form-select select2'
            }),
            'distrito_judicial': forms.Select(attrs={
                'class': 'form-select select2'
            }),
            'municipio': forms.Select(attrs={
                'class': 'form-select select2'
            }),
            'juzgado': forms.Select(attrs={
                'class': 'form-select select2'
            }),
            'fecha_ejecutoria': forms.Select(attrs={
                'class': 'form-select select2'
            }),

            'tomo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'numero_tomo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de tomo'
            }),
            'rango_folio_inicial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rango de folio inicial'
            }),'rango_folio_final': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rango de folio final'
            }),
            'medida_centimetros': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Medida en centimetros'
            })
            ,
            'expediente_toca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Expediente'
            }),
            'actor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Actor'
            }),
            'demandado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Demandado'
            }),
            'juez': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del juez'
            }),
            'secretario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del secretario'
            }),
            'beneficiario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del beneficiario'
            }),
            'numero_acumulado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número acumulado'
            }),

            # Date fields con flatpickr
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD',
                'id': 'flatpickr-fecha-inicio'
            }),
            'fecha_sentencia': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD',
                'id': 'flatpickr-fecha-sentencia'
            }),
            'fecha_archivo': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD',
                'id': 'flatpickr-fecha-archivo'
            }),
            'fecha_convenio': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD',
                'id': 'flatpickr-fecha-convenio'
            }),
            'fecha_concluido': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD',
                'id': 'flatpickr-fecha-concluido'
            }),
            'fecha_prestamo': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD',
                'id': 'flatpickr-fecha-prestamo'
            }),
            'oficio_atencion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Oficio con atención'
            }),
            'numero_oficio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de oficio'
            }),
            # Booleanos
            'original': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'duplicado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'cuadernillo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'acumulado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'concluido': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            # Auditoría (normalmente se asigna en la vista, no se muestra)
            'creado_por': forms.HiddenInput(),
            'actualizado_por': forms.HiddenInput(),
            'fecha_creacion': forms.HiddenInput(),
            'fecha_actualizacion': forms.HiddenInput(),
            'documento_prestamo': forms.FileInput(attrs={
                'class': 'form-control custom-file-input',
                'accept': 'application/pdf',
                'id': 'documento_prestamo_id'
            }),
        }

        labels = {
            'oficio_atencion': 'Oficio atención (préstamo)',
            'numero_oficio': 'Número oficio (préstamo)',
            'fecha_prestamo': 'Fecha de préstamo',
            'medida_centimetros': 'Medida en centímetros',
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        
        self.one_column_fields = [
            'juicio_delito','cuadernillo', 'acumulado', 'avocamiento'
        ]

        self.two_column_fields = [
            'actor', 'demandado', 'beneficiario', 'observaciones', 'numero', 'fecha_convenio', 'materia', 'distrito_judicial', 'municipio', 'juzgado', 'expediente_toca', 'instancia', 'juez', 'secretario', 'fecha_ejecutoria', 'rango_folio_inicial','rango_folio_final', 'documento_prestamo',
             'acumulado', 'numero_acumulado', 'numero_tomo', 'medida_centimetros', 'oficio_atencion',
            'numero_oficio',
            'fecha_prestamo'
        ]

        self.three_column_fields = [
            'fecha_inicio', 'fecha_sentencia','fecha_archivo', 
        ]

        self.four_column_fields = [
            'original', 'duplicado', 'concluido', 'fecha_concluido'
        ]

        self.ETAPAS = [
            ("Datos jurisdiccionales", ["instancia", "materia", "distrito_judicial"]),
            ("Expediente", ['expediente_toca', 'numero_tomo']),
            ("Datos generales", ['juicio_delito',
            'actor',
            'demandado',
            'fecha_inicio',
            'fecha_sentencia',
            'fecha_archivo',
            'juez',
            'secretario',
            'beneficiario',
            'fecha_convenio',
            'rango_folio_inicial',
            'rango_folio_final',
            'original',
            'duplicado',
            'concluido',
            'fecha_concluido',
            'fecha_ejecutoria',
            'observaciones']),
            ("Datos adicionales", ['cuadernillo', 'acumulado', 'avocamiento', 'documento_prestamo','oficio_atencion',
            'numero_oficio',
            'fecha_prestamo','medida_centimetros']),
        ]

        # Guarda los campos que son BooleanField
        self.boolean_field_names = [
            name for name, field in self.fields.items() if isinstance(field, forms.BooleanField)
        ]

        self.date_field_names = [
            name for name, field in self.fields.items() if isinstance(field, forms.DateField)
        ]

        #if not self.instance.tomo:
        #    self.fields['numero_tomo'].widget.attrs['disabled'] = True

        #if not self.instance.acumulado:
        #    self.fields['numero_acumulado'].widget.attrs['disabled'] = True

        if not self.instance.concluido:
            self.fields['fecha_concluido'].widget.attrs['disabled'] = True
            
        self.fields['oficio_atencion'].widget.attrs['disabled'] = True
        self.fields['numero_oficio'].widget.attrs['disabled'] = True
        self.fields['fecha_prestamo'].widget.attrs['disabled'] = True
        
        if self.instance.documento_prestamo:
            self.fields['oficio_atencion'].widget.attrs['disabled'] = False
            self.fields['numero_oficio'].widget.attrs['disabled'] = False
            self.fields['fecha_prestamo'].widget.attrs['disabled'] = False

        for field_name, field in self.fields.items():
            if field_name not in ['tomo', 'original']:  # Excluye esos campos
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()
                #field_name.is_boolean = isinstance(field, forms.BooleanField)

        # Establecer valores iniciales basados en la sesión
        if self.request:
            archivo_regional = self.request.session.get('archivo_regional')
            organo_jurisdiccional_seleccionado = self.request.session.get('organo_jurisdiccional_seleccionado')

            if organo_jurisdiccional_seleccionado:
                pass
                #self.fields['organo_jurisdiccional'].initial = organo_jurisdiccional_seleccionado
                #self.fields['municipio'].initial = organo_jurisdiccional_seleccionado.municipio
                #self.fields['materia'].initial = organo_jurisdiccional_seleccionado.municipio

    """def save(self, commit=True):
        expediente = super().save(commit=False)
        # Restaurar campos booleanos si no vinieron (porque fueron ocultos)
        for field_name in ['acumulado', 'cuadernillo', 'avocamiento']:
            if field_name not in self.cleaned_data:
                setattr(expediente, field_name, getattr(self.instance, field_name))
        
        if commit:
            expediente.save()
        return expediente """

    def etapas(self):
        """
        Devuelve una lista de tuplas con el nombre de la etapa y los campos correspondientes como objetos BoundField
        """
        return [
            (nombre, [self[field_name] for field_name in campos if field_name in self.fields])
            for nombre, campos in self.ETAPAS
        ]