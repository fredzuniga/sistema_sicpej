import json
from django.forms.models import model_to_dict
from apps_sicpej.gestion.models import BitacoraInstancias

def model_to_dict_serializable(instance):
    """
    Convierte un modelo a diccionario de forma segura para JSON
    """
    if instance is None:
        return {}
    
    try:
        # Convertir a diccionario
        data = model_to_dict(instance)
        
        # Manejar campos especiales que no son serializables
        for key, value in data.items():
            if hasattr(value, 'pk'):  # Si es un objeto relacionado
                data[key] = str(value.pk)
            elif hasattr(value, '__str__'):
                data[key] = str(value)
        
        return data
    except:
        return {'__str__': str(instance)}

def registrar_bitacora(instancia, accion, usuario_accion, usuario_asignado=None, valores_nuevos=None, descripcion=None, valores_anteriores=None):
    """
    Registra en la bitácora acciones sobre instancias.
    Si se pasa valores_anteriores={}, se guarda como JSON vacío.
    """
    # Determinar tipo de instancia
    class_name = instancia.__class__.__name__.lower()
    if 'expediente' in class_name:
        tipo = '1'
    elif 'paquete' in class_name:
        tipo = '2'
    else:
        tipo = '3'

    # ¿Es una creación nueva?
    es_nueva_creacion = not instancia.pk

    # MANEJO DE VALORES ANTERIORES
    # Si se pasa explícitamente (incluso como {}), usar ese valor
    if valores_anteriores is not None:
        # Si se pasa {} explícitamente, mantenerlo como diccionario vacío
        valores_anteriores = None
    else:
        # Si NO se pasa explícitamente, determinar automáticamente
        valores_anteriores = None
        if not es_nueva_creacion:
            try:
                db_instance = instancia.__class__.objects.get(pk=instancia.pk)
                valores_anteriores = model_to_dict_serializable(db_instance)
            except:
                valores_anteriores = None

    # Valores nuevos
    if valores_nuevos is None:
        valores_nuevos = model_to_dict_serializable(instancia)

    # Descripción por defecto
    if descripcion is None:
        descripcion = f"{accion.capitalize()} {instancia.__class__.__name__}"

    try:
        # Preparar valores para JSON
        valores_anteriores_json = None
        if valores_anteriores is not None:
            # Si es diccionario vacío {}, se convierte a "{}"
            # Si tiene datos, se convierte normalmente
            valores_anteriores_json = json.dumps(valores_anteriores, ensure_ascii=False, default=str)
        
        BitacoraInstancias.objects.create(
            tipo_instancia=tipo,
            instancia_id=str(instancia.pk) if instancia.pk else "nuevo",
            descripcion=descripcion,
            accion="crear" if es_nueva_creacion else accion,
            valores_anteriores=valores_anteriores_json,  # Puede ser None o JSON string
            valores_nuevos=json.dumps(valores_nuevos, ensure_ascii=False, default=str),
            usuario_asignado=usuario_asignado,
            usuario_accion=usuario_accion
        )
        return True
    except Exception as e:
        print(f"Error al registrar bitácora: {e}")
        return False