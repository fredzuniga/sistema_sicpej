from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth import get_user_model
User = get_user_model()
from ..models import UserConfig, Juzgado, ArchivoRegional, OrganoJurisdiccional
from apps_sicpej.gestion.models import Perfil, UsuarioPerfil
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

class UserWithConfigForm(UserCreationForm):
    """juzgado = forms.ModelChoiceField(
        queryset=Juzgado.objects.all(),
        required=False
    )"""

    """organo_jurisdiccional = forms.ModelChoiceField(
        queryset=OrganoJurisdiccional.objects.all(),
        required=False
    )"""

    archivo_regional = forms.ModelChoiceField(
        queryset=ArchivoRegional.objects.all(),
        required=False,
        label="Archivo Regional"
    )

    perfil_capturista = forms.ModelChoiceField(
        queryset=Perfil.objects.all(),
        required=True,
        initial="1"
    )
    
    estatus_perfil = forms.ChoiceField(
        choices=UsuarioPerfil.ESTATUS,
        required=True,
        label="Estatus",
        initial=1
    )

    es_administrador_general = forms.BooleanField(required=False, label="Administrador general")
    es_administrador_regional = forms.BooleanField(required=False, label="Administrador regional")
    es_capturista_regional = forms.BooleanField(required=False, label="Capturista regional")
    es_usuario_consulta = forms.BooleanField(required=False, label="Consultor")

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'archivo_regional',
            'es_administrador_general',
            'es_administrador_regional',
            'es_capturista_regional',
            'perfil_capturista','estatus_perfil',
            'es_usuario_consulta',
            'is_superuser',
            'is_staff',
            'is_active',
            
        ]
        labels = {
            'username': 'Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'is_active': 'Activo',
            'is_staff': 'Usuario común',
            'is_superuser': 'Es superusuario',
            'es_administrador_general': 'Administrador general',
            'es_administrador_regional': 'Administrador regional',
            'es_capturista_regional': 'Capturista regional',
            'es_usuario_consulta': 'Consultor',
            'perfil_capturista' :'Perfil capturista'
        }
        help_texts = {
            'username': 'Obligatorio. Hasta 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.',
            'is_active': 'Indica si este usuario debe ser tratado como activo. Desactiva esta opción en lugar de eliminar la cuenta.',
            'is_staff': 'Designa si el usuario puede iniciar sesión en el sitio de administración.',
            'is_superuser': 'Designa que el usuario tiene acceso total a todas las funcionalidades.',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        self.fields['archivo_regional'].label_from_instance = (
            lambda obj: f"{obj.nombre} ({obj.municipio.descripcion})"
        )

        # Agregar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()

        self.boolean_field_names = [
            name for name, field in self.fields.items() if isinstance(field, forms.BooleanField)
        ]
        
        # Quitar campos si es staff (pero no superusuario)
        if self.request:
            user_actual = self.request.user
            if user_actual.is_staff and not user_actual.is_superuser:
                for field in ['is_superuser', 'is_staff', 'is_active', 'archivo_regional', 'organo_jurisdiccional']:
                    if field in self.fields:
                        del self.fields[field]

        # Etiquetas y ayuda para contraseñas
        self.fields['password1'].label = "Contraseña"
        self.fields['password2'].label = "Confirmar contraseña"
        self.fields['password1'].help_text = mark_safe(
            "Tu contraseña debe contener al menos 8 caracteres.<br>"
            "Tu contraseña no puede ser una contraseña comúnmente usada.<br>"
            "Tu contraseña no puede ser completamente numérica."
        )
        self.fields['password2'].help_text = "Ingresa la misma contraseña que antes, para verificación."

        # Configuración al editar un usuario existente
        if self.instance.pk:
            self.fields['username'].required = False
            self.fields['username'].widget.attrs['readonly'] = True

            self.fields['password1'].required = False
            self.fields['password2'].required = False
            self.fields['password1'].help_text = "Dejar en blanco para mantener la contraseña actual."
            self.fields['password2'].help_text = "Introduce la misma contraseña que antes, para verificación."

            # Inicializar campos personalizados si ya existen
            try:
                user_config = self.instance.configuracion
                #if 'juzgado' in self.fields:
                #    self.fields['juzgado'].initial = user_config.juzgado
                if 'archivo_regional' in self.fields:
                    self.fields['archivo_regional'].initial = user_config.archivo_regional
                if 'organo_jurisdiccional' in self.fields:
                    self.fields['organo_jurisdiccional'].initial = user_config.organo_jurisdiccional
                # Cargar valores iniciales de los campos tipo checkbox
                if 'es_administrador_general' in self.fields:
                    self.fields['es_administrador_general'].initial = user_config.es_administrador_general
                if 'es_administrador_regional' in self.fields:
                    self.fields['es_administrador_regional'].initial = user_config.es_administrador_regional
                if 'es_capturista_regional' in self.fields:
                    self.fields['es_capturista_regional'].initial = user_config.es_capturista_regional
                if 'es_usuario_consulta' in self.fields:
                    self.fields['es_usuario_consulta'].initial = user_config.es_usuario_consulta

                #if self.instance.configuracion.es_capturista_regional:
                user_perfil = self.instance.perfiles_asignados.first()
                if user_perfil:
                    self.fields['perfil_capturista'].initial = user_perfil.perfil
                    self.fields['estatus_perfil'].initial = user_perfil.estatus
                

            except UserConfig.DoesNotExist:
                pass

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if not self.instance.pk and not password2:
            raise ValidationError("Debes confirmar la contraseña para nuevos usuarios.")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")

        return password2

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre.")
        return username

    """def save(self, commit=True, request_user=None):
        user = super().save(commit=False)

        # Restaurar campos booleanos si no vinieron (porque fueron ocultos)
        for field_name in ['is_active', 'is_staff', 'is_superuser']:
            if field_name not in self.cleaned_data:
                setattr(user, field_name, getattr(self.instance, field_name))

        # Asignar nueva contraseña solo si fue especificada
        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

            # Guardar UserConfig
            user_config, created = UserConfig.objects.get_or_create(user=user)
            #if 'juzgado' in self.cleaned_data and self.cleaned_data['juzgado']:
            #    user_config.juzgado = self.cleaned_data['juzgado']
            if 'archivo_regional' in self.cleaned_data and self.cleaned_data['archivo_regional']:
                user_config.archivo_regional = self.cleaned_data['archivo_regional']

            if 'organo_jurisdiccional' in self.cleaned_data and self.cleaned_data['organo_jurisdiccional']:
                user_config.organo_jurisdiccional = self.cleaned_data['organo_jurisdiccional']

            if request_user:
                if created:
                    user_config.creado_por = request_user
                user_config.actualizado_por = request_user

            user_config.save()

        return user """
    
    def save(self, commit=True, request_user=None):
        user = self.instance  # NO usar super().save(), evitar que sobreescriba con contraseñas vacías

        for field_name in ['is_active', 'is_staff', 'is_superuser','es_administrador_general']:
            if field_name not in self.cleaned_data:
                setattr(user, field_name, getattr(self.instance, field_name))

        # Actualizar campos del modelo
        for field in self.Meta.fields:
            if field in self.cleaned_data:
                setattr(user, field, self.cleaned_data[field])

        # Solo si se ingresa una nueva contraseña
        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

            # Guardar o actualizar configuración del usuario
            user_config, created = UserConfig.objects.get_or_create(user=user)

            if 'archivo_regional' in self.cleaned_data:
                user_config.archivo_regional = self.cleaned_data['archivo_regional']
            if 'organo_jurisdiccional' in self.cleaned_data:
                user_config.organo_jurisdiccional = self.cleaned_data['organo_jurisdiccional']
            if 'es_administrador_general' in self.cleaned_data:
                user_config.es_administrador_general = self.cleaned_data['es_administrador_general']
            if 'es_administrador_regional' in self.cleaned_data:
                user_config.es_administrador_regional = self.cleaned_data['es_administrador_regional']
            if 'es_capturista_regional' in self.cleaned_data:
                user_config.es_capturista_regional = self.cleaned_data['es_capturista_regional']
            if 'es_usuario_consulta' in self.cleaned_data:
                user_config.es_usuario_consulta = self.cleaned_data['es_usuario_consulta']

            if 'es_capturista_regional' in self.cleaned_data:
                es_capturista = self.cleaned_data.get("es_capturista_regional")
                perfil_capturista = self.cleaned_data.get("perfil_capturista")
                estatus_perfil = self.cleaned_data.get("estatus_perfil")

                if es_capturista:
                    # Caso activado → guardar/actualizar relación
                    if perfil_capturista and estatus_perfil is not None:
                        user_perfil = UsuarioPerfil.objects.filter(usuario=user).first()

                        if user_perfil:
                            # Actualizar el perfil existente (aunque cambie el perfil)
                            user_perfil.perfil = perfil_capturista
                            user_perfil.estatus = estatus_perfil
                            user_perfil.archivo_regional = self.cleaned_data.get("archivo_regional")
                            user_perfil.organo_jurisdiccional = self.cleaned_data.get("organo_jurisdiccional")
                            user_perfil.actualizado_por = request_user
                            user_perfil.save()
                            created = False
                        else:
                            # Si no existe, lo creamos
                            user_perfil = UsuarioPerfil.objects.create(
                                usuario=user,
                                perfil=perfil_capturista,
                                estatus=estatus_perfil,
                                archivo_regional=self.cleaned_data.get("archivo_regional"),
                                organo_jurisdiccional=self.cleaned_data.get("organo_jurisdiccional"),
                                creado_por= request_user,
                                actualizado_por= request_user
                            )
                            created = True
                else:
                    # Caso desactivado → buscar y deshabilitar
                    user_perfil = UsuarioPerfil.objects.filter(usuario=user).first()
                    if user_perfil:
                        user_perfil.estatus = 0
                        user_perfil.actualizado_por = request_user
                        user_perfil.save(update_fields=["estatus", "actualizado_por"])

            
            if request_user:
                if created:
                    user_config.creado_por = request_user
                user_config.actualizado_por = request_user

            user_config.save()

        return user
