from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model

User = get_user_model()
    
class Estado(models.Model):
    clave = models.CharField(max_length=10, null=True, blank=True)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return '{}'.format(self.descripcion)

class Municipio(models.Model):
    clave = models.CharField(max_length=10, null=True, blank=True)
    descripcion = models.CharField(max_length=250)
    id_estado = models.ForeignKey(Estado, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.descripcion)

class Localidad(models.Model):
    descripcion = models.CharField(max_length=150)
    id_estado = models.ForeignKey(Estado, on_delete=models.CASCADE, null=True, blank=True)
    id_municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, null=True, blank=True)
    ambito = models.CharField(max_length=2, null=True, blank=True)

class ArchivoRegional(models.Model):
    ESTATUS = (
        (0, "No activo"),
        (1, "Activo")
    )
    nombre = models.CharField(max_length=255)
    #municipio = models.TextField(null=True, blank=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE,null=True)
    locacion = models.TextField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    clave = models.CharField(max_length=50,null=True, blank=True)
    nombre_corto = models.CharField(max_length=50,null=True, blank=True)
    rgb_color_identificacion = models.CharField(max_length=15,null=True, blank=True)
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)
    # Campos de auditoría
    creado_por = models.ForeignKey(User,  on_delete=models.SET_NULL, null=True, related_name='archivos_regionales_creados')
    actualizado_por = models.ForeignKey( User, on_delete=models.SET_NULL, null=True, related_name='archivos_regionales_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    def __str__(self):
        return self.nombre or "Sin nombre"

class TipoJuzgado(models.Model):
    ESTATUS = (
        (0, "No activo"),
        (1, "Activo")
    )

    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    nota = models.TextField(blank=True, null=True)
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)
    
    # Campos de auditoría
    creado_por = models.ForeignKey( User,  on_delete=models.SET_NULL,  null=True,  related_name='tipos_juzgado_creados')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tipos_juzgado_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    class Meta:
        verbose_name = "Tipo juzgado"
        verbose_name_plural = "Tipo juzgado"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
class Materia(models.Model):
    ESTATUS = (
        (0, "No activo"),
        (1, "Activo")
    )

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    nota = models.TextField(blank=True, null=True)
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)

    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='materias_creadas')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='materias_actualizadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class DistritoJudicial(models.Model):
    ESTATUS = (
        (0, "No activo"),
        (1, "Activo")
    )

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    locacion = models.CharField(max_length=500, null=True, blank=True)
    direccion = models.CharField(max_length=500, null=True, blank=True)
    nota = models.TextField(blank=True, null=True)
    archivo_regional = models.ForeignKey(ArchivoRegional, on_delete=models.CASCADE,null=True, blank=True)
    materia = models.ForeignKey( Materia, on_delete=models.SET_NULL, null=True, blank=True,related_name='materias')
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE,blank=True, null=True)
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)

    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='distritos_creados')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='distritos_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    class Meta:
        verbose_name = "Distrito Judicial"
        verbose_name_plural = "Distritos Judiciales"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
class RegionJudicial(models.Model):
    ESTATUS = (
        (0, "No activo"),
        (1, "Activo")
    )

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    nota = models.TextField(blank=True, null=True)
    #archivo_regional = models.ForeignKey(ArchivoRegional, on_delete=models.CASCADE,null=True, blank=True)
    materia = models.ForeignKey( Materia, on_delete=models.SET_NULL, null=True, blank=True,related_name='regiones_judiciales')
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)

    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='regiones_judiciales_creadas')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='regiones_judiciales_actualizadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    class Meta:
        verbose_name = "Región judicial"
        verbose_name_plural = "Regiones judijciales"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
 
class Juzgado(models.Model):
    TIPO = (
        (1, "FAMILIAR"),
        (2, "MERCANTIL"),
        (3, "CIVIL"),
        (4, "PENAL"),
        (5, "LABORAL"),
        (6, "MIXTO"),
        (7, "CONCILIACION"),
        (8, "OFICIALIA DE PARTES"),
        (9, "DE PAZ "),
        (13, "FEDERAL"),
        (14, "CONSIGNACIONES Y PAGOS"),
    )

    ESTATUS = (
        (0, "No activo"),
        (1, "Activo")
    )

    nombre = models.CharField(max_length=550)
    nombre_corto = models.CharField(max_length=50,null=True, blank=True)
    descripcion = models.TextField()
    clave_interna = models.CharField(max_length=50,null=True, blank=True)
    locacion = models.CharField(max_length=500, null=True, blank=True)
    direccion = models.CharField(max_length=500, null=True, blank=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    archivo_regional = models.ForeignKey(ArchivoRegional, on_delete=models.CASCADE)
    distrito_judicial = models.ForeignKey(DistritoJudicial,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Distrito Judicial o Región")
    region_judicial = models.ForeignKey(RegionJudicial,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Región Judicial")
    #RegionJudicial
    #tipo = models.PositiveSmallIntegerField(choices=TIPO, default=1)
    tipo_juzgado = models.ForeignKey(TipoJuzgado, on_delete=models.CASCADE,null=True, blank=True,related_name='juzgados')
    materia = models.ForeignKey( Materia, on_delete=models.SET_NULL, null=True, blank=True,related_name='juzgados')
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)
    #created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL,  null=True, related_name='juzgados_creados')
    actualizado_por = models.ForeignKey( User, on_delete=models.SET_NULL, null=True, related_name='juzgados_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)

    def nombre_en_fecha(self, fecha):
        if not fecha:
            return self.nombre or "Sin nombre"
        
        nombre_historico = self.nombres_historicos.filter(
            fecha_inicio__lte=fecha,
            fecha_fin__gte=fecha
        ).order_by('-fecha_inicio').first()
        
        return nombre_historico.nombre if nombre_historico else self.nombre
    
    def __str__(self):
        return self.nombre or "Sin nombre"

class Instancia(models.Model):
    ESTATUS = (
        (0, "No activo"),
        (1, "Activo")
    )
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    nota = models.TextField(blank=True, null=True)
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)

    # Campos de auditoría
    creado_por = models.ForeignKey( User,  on_delete=models.SET_NULL,  null=True,  related_name='instancias_creadas')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='instancias_actualizadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    class Meta:
        verbose_name = "Instancia"
        verbose_name_plural = "Instancias"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
class OrganoJurisdiccional(models.Model):
    TIPO = (
        (1, "Juzgado"),
        (2, "Tribunal"),
    )

    ESTATUS = (
        (0, "No activo"),
        (1, "Activo")
    )

    nombre = models.CharField(max_length=550)
    nombre_corto = models.CharField(max_length=50,null=True, blank=True)
    descripcion = models.TextField()
    clave_interna = models.CharField(max_length=50,null=True, blank=True)
    locacion = models.CharField(max_length=500, null=True, blank=True)
    direccion = models.CharField(max_length=500, null=True, blank=True)
    
    #RegionJudicial
    #tipo = models.PositiveSmallIntegerField(choices=TIPO, default=1)
    materia = models.ForeignKey( Materia, on_delete=models.SET_NULL, null=True, blank=True,related_name='organos_jurisdiccionales')
    tipo_organo = models.PositiveSmallIntegerField(choices=TIPO, default=1)
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)

    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, related_name='organos_jurisdiccionales')
    archivo_regional = models.ForeignKey(ArchivoRegional, on_delete=models.CASCADE, related_name='organos_jurisdiccionales')
    distrito_judicial = models.ForeignKey(DistritoJudicial,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Distrito Judicial o Región", related_name='organos_jurisdiccionales')
    region_judicial = models.ForeignKey(RegionJudicial,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Región Judicial", related_name='organos_jurisdiccionales')
    tipo = models.ForeignKey(TipoJuzgado, on_delete=models.CASCADE,null=True, blank=True,related_name='organos_jurisdiccionales')
    instancia = models.ForeignKey(Instancia, on_delete=models.CASCADE,null=True, blank=True,related_name='organos_jurisdiccionales')
    
    #created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL,  null=True, related_name='organos_jurisdiccionales_creados')
    actualizado_por = models.ForeignKey( User, on_delete=models.SET_NULL, null=True, related_name='organos_jurisdiccionales_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    def __str__(self):
        nombre = self.nombre or "Sin nombre"
        municipio = self.municipio or "Sin municipio"
        return f"{nombre}, {municipio.descripcion}"
    
class UserConfig(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='configuracion')
    juzgado = models.ForeignKey(Juzgado, on_delete=models.CASCADE, null=True, blank=True, related_name='configuraciones_usuario')
    organo_jurisdiccional = models.ForeignKey(OrganoJurisdiccional, on_delete=models.CASCADE, null=True, blank=True, related_name='configuraciones_usuario')
    archivo_regional = models.ForeignKey(ArchivoRegional, on_delete=models.CASCADE, null=True ,blank=True,related_name='configuraciones_usuario' )
    es_administrador_general = models.BooleanField(default=False, verbose_name="Administrador general")
    es_administrador_regional = models.BooleanField(default=False, verbose_name="Administrador regional del archivo")
    es_capturista_regional = models.BooleanField(default=False, verbose_name="Capturista del archivo regional")
    es_usuario_consulta = models.BooleanField(default=False, verbose_name="Usuario de consulta")
    #
    creado_por = models.ForeignKey( User, on_delete=models.SET_NULL,  null=True,  related_name='configuraciones_creadas')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='configuraciones_actualizadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name_plural = 'Configuraciones USER'

    def __str__(self):
        return f"Configuración del usuario #{self.user.pk} - {self.user.username}"
    
class NombreJuzgadoHistorico(models.Model):
    juzgado = models.ForeignKey(Juzgado, on_delete=models.CASCADE, related_name='nombres_historicos')
    nombre = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    #falta_user_creador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    motivo_cambio = models.TextField(blank=True)
    activo = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name_plural = 'Histórico nombres juzgado'
    
    def __str__(self):
        return f"{self.nombre} ({self.fecha_inicio} a {self.fecha_fin or 'Actual'})"
    
    def save(self, *args, **kwargs):
        if not self.fecha_inicio:
            self.fecha_inicio = timezone.now().date()
        super().save(*args, **kwargs)
            
class TipoJuicio(models.Model):
    ESTATUS = (
        (0, "No activo"),
        (1, "Activo")
    )

    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    nota = models.TextField(blank=True, null=True)
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)
    
    # Relación con Materia
    materia = models.ForeignKey( Materia, on_delete=models.SET_NULL, null=True, blank=True,related_name='tipos_juicios_materia')
    
    # Campos de auditoría
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tipos_jucios_creados')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tipos_juicios_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    class Meta:
        verbose_name = "Tipo juicio"
        verbose_name_plural = "Tipo juicio"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    

class LogCambio(models.Model):
    modelo = models.CharField(max_length=100)
    instancia_id = models.CharField(max_length=50)
    descripcion = models.TextField(null=True)
    accion = models.CharField(max_length=20, choices=[('creado', 'Creado'), ('actualizado', 'Actualizado'), ('eliminado', 'Eliminado'),('login', 'Login'),('logout', 'Logout'),('login_failed', 'Login Failed')])
    valores_anteriores = models.TextField(blank=True, null=True)
    valores_nuevos = models.TextField(blank=True, null=True)
    #usuario = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_accion = models.DateTimeField(auto_now_add=True)
    relacionado_con_modelo = models.CharField(max_length=100, null=True, blank=True)  # 'Expediente'
    relacionado_con_id = models.CharField(max_length=50, null=True, blank=True) 
    app_label = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        partes = [
            f"[{self.fecha_accion.strftime('%Y-%m-%d %H:%M:%S')}]",
            f"{self.usuario} realizó",
            f"{self.accion.upper()}",
            f"en {self.modelo}(id={self.instancia_id})"
        ]

        if self.relacionado_con_modelo and self.relacionado_con_id:
            partes.append(f"relacionado con {self.relacionado_con_modelo}(id={self.relacionado_con_id})")

        return " - ".join(partes)
    

    def restaurar_instancia(self):
        if self.accion != 'eliminado' or not self.valores_anteriores:
            raise ValueError("Este log no corresponde a una eliminación válida")

        from django.apps import apps
        import json

        if not self.app_label:
            raise ValueError("Falta app_label en el log")

        modelo = apps.get_model(app_label=self.app_label, model_name=self.modelo)
        data = json.loads(self.valores_anteriores)

        # Procesar relaciones ForeignKey
        for field in modelo._meta.fields:
            if field.is_relation and field.many_to_one:
                fk_name = field.name
                fk_model = field.related_model
                fk_id = data.get(fk_name)
                if fk_id:
                    try:
                        data[fk_name] = fk_model.objects.get(pk=fk_id)
                    except fk_model.DoesNotExist:
                        data[fk_name] = None  # o eliminar con: data.pop(fk_name)

        # Restaurar la instancia
        instancia = modelo(**data)
        instancia.pk = self.instancia_id
        instancia.save()
        return instancia

