# myapp/signals.py
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from django.forms.models import model_to_dict
from .models import LogCambio
from .middleware import get_current_user
import json
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed


_old_data_cache = {}

# relaciones.py o directamente en signals.py

RELACIONES_PADRE_HIJO = {
    'Cuadernillo': ('Expediente', 'expediente'),
    'Acumulado': ('Expediente', 'expediente'),
}

def obtener_relacion_padre(instance):
    modelo_nombre = instance.__class__.__name__
    if modelo_nombre in RELACIONES_PADRE_HIJO:
        modelo_padre, campo = RELACIONES_PADRE_HIJO[modelo_nombre]
        relacionado_id = getattr(instance, f"{campo}_id", None)
        return modelo_padre, relacionado_id
    return None, None

EXCLUDED_MODELS = {
    "LogCambio",     # Tu propio modelo de log
    "Session",       # Django sessions
}
EXCLUDED_APPS = {
    "admin",
    "sessions",
    "contenttypes",  # opcional
    "auth",          # opcional
}

def is_loggable_model(model):
    return (
        model.__name__ not in EXCLUDED_MODELS
        and model._meta.app_label not in EXCLUDED_APPS
    )

def pre_save_handler(sender, instance, **kwargs):
    if not is_loggable_model(sender):
        return
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            _old_data_cache[(sender, instance.pk)] = model_to_dict(old_instance)
        except sender.DoesNotExist:
            _old_data_cache[(sender, instance.pk)] = {}

def post_save_handler(sender, instance, created, **kwargs):
    # Diccionario: modelo_hijo -> (modelo_padre, campo_relacion)
    if not is_loggable_model(sender):
        return

    key = (sender, instance.pk)
    old_data = _old_data_cache.pop(key, {}) if key in _old_data_cache else {}
    new_data = model_to_dict(instance)
    user = get_current_user()

    modelo_nombre = sender.__name__
    relacionado_con_modelo = None
    relacionado_con_id = None

    relacionado_con_modelo, relacionado_con_id = obtener_relacion_padre(instance)

    log_data = {
        'modelo': modelo_nombre,
        'instancia_id': instance.pk,
        'usuario': user,
        'relacionado_con_modelo': relacionado_con_modelo,
        'relacionado_con_id': relacionado_con_id,
    }

    if created:
        LogCambio.objects.create(
            **log_data,
            accion='creado',
            valores_nuevos=json.dumps(new_data, default=str),
            app_label=instance._meta.app_label
        )
    elif old_data != new_data:
        LogCambio.objects.create(
            **log_data,
            accion='actualizado',
            valores_anteriores=json.dumps(old_data, default=str),
            valores_nuevos=json.dumps(new_data, default=str),
            app_label=instance._meta.app_label
        )

@receiver(post_delete)
def post_delete_handler(sender, instance, **kwargs):
    if not is_loggable_model(sender):
        return

    user = get_current_user()
    modelo_nombre = sender.__name__
    valores_anteriores = model_to_dict(instance)

    relacionado_con_modelo, relacionado_con_id = obtener_relacion_padre(instance)

    log_data = {
        'modelo': modelo_nombre,
        'instancia_id': instance.pk,
        'usuario': user,
        'relacionado_con_modelo': relacionado_con_modelo,
        'relacionado_con_id': relacionado_con_id,
    }

    LogCambio.objects.create(
        **log_data,
        accion='eliminado',
        valores_anteriores=json.dumps(valores_anteriores, default=str),
        valores_nuevos="",
        app_label=instance._meta.app_label
    )

# --------- HANDLERS LOGIN / LOGOUT ---------
@receiver(user_logged_in)
def registrar_login(sender, request, user, **kwargs):
    LogCambio.objects.create(
        modelo="User",
        instancia_id=user.pk,
        usuario=user,
        accion="login",
        valores_nuevos=json.dumps({"username": user.username}, default=str),
        app_label=user._meta.app_label
    )

@receiver(user_logged_out)
def registrar_logout(sender, request, user, **kwargs):
    LogCambio.objects.create(
        modelo="User",
        instancia_id=user.pk if user else None,
        usuario=user,
        accion="logout",
        valores_nuevos="",
        app_label=user._meta.app_label if user else "auth"
    )

@receiver(user_login_failed)
def registrar_login_fallido(sender, credentials, request, **kwargs):
    LogCambio.objects.create(
        modelo="User",
        instancia_id=None,
        usuario=None,
        accion="login_failed",
        valores_nuevos=json.dumps({"username": credentials.get("username")}, default=str),
        app_label="auth"
    )