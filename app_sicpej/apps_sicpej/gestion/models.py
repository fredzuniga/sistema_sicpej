from django.db import models
from apps_sicpej.administracion.models import DistritoJudicial, Instancia, Juzgado, Materia, Municipio, OrganoJurisdiccional, TipoJuicio, ArchivoRegional
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.timezone import now
import os
from django.db.models import Sum

User = get_user_model()

class Paquete(models.Model):
    TIPO_PAQUETE = (
        (1, "Principal"),
        (2, "Extensión"),
    )

    CLASIFICACION_PAQUETE = (
        ('N', "TRAMITE"),
        ('C', "CONCLUIDO"),
    )

    ESTATUS = (
        (1, "Sin asignar"),
        (2, "Asignado"),
        (3, "Terminado"),
    )

    numero_paquete= models.PositiveIntegerField(null=True, blank=True)
    numero_paquete_letra= models.PositiveIntegerField(null=True, blank=True)
    letra = models.CharField(max_length=1, blank=True, null=True, help_text="Letra del paquete, por ejemplo: A, B, C")
    clave_paquete = models.CharField(max_length=10, blank=True, null=True)
    nombre = models.CharField(max_length=255,null=True, blank=True)
    clave = models.CharField(max_length=255,null=True, blank=True)
    topografia = models.CharField(max_length=255,null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    nota = models.TextField(null=True, blank=True)
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)
    juzgado = models.ForeignKey(Juzgado, on_delete=models.CASCADE,null=True, blank=True)
    archivo_regional = models.ForeignKey(ArchivoRegional, on_delete=models.CASCADE,null=True, blank=True, related_name='paquetes')
    organo_jurisdiccional = models.ForeignKey(OrganoJurisdiccional, on_delete=models.CASCADE, null=True, related_name='paquetes')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_concluido = models.DateTimeField(null=True, blank=True)
    tipo_paquete = models.PositiveSmallIntegerField(choices=TIPO_PAQUETE, default=1)
    clasificacion_paquete = models.CharField(max_length=1, choices=CLASIFICACION_PAQUETE, default='N')
    paquete_padre = models.ForeignKey('self', on_delete=models.CASCADE,null=True, blank=True)
    ultimo = models.BooleanField(default=True)
    # Campos de auditoría
    creado_por = models.ForeignKey(User,  on_delete=models.SET_NULL, null=True, related_name='paquetes_creados')
    actualizado_por = models.ForeignKey( User, on_delete=models.SET_NULL, null=True, related_name='paquetes_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    def __str__(self):
        #juzgado_nombre = self.juzgado.nombre if self.juzgado and self.juzgado.nombre else "Juzgado desconocido"
        organo_jurisdiccional_nombre = self.organo_jurisdiccional.nombre if self.organo_jurisdiccional and self.organo_jurisdiccional.nombre else "Organo jurisdiccional desconocido"
        municipio = self.organo_jurisdiccional.municipio if self.organo_jurisdiccional and self.organo_jurisdiccional.municipio.descripcion else "Municipio desconocido"
        clave_paquete = self.clave_paquete if self.clave_paquete is not None else "sin número"
        return f"Paquete #{clave_paquete} - {organo_jurisdiccional_nombre} ({municipio})"
    
    @property
    def num_expedientes(self):
        return self.expedientes.count()
    
    @property
    def total_medida_centimetros(self):
        total = self.expedientes.aggregate(
            total=Sum('medida_centimetros')
        )['total']
        return total or 0  # Si es None, devolvemos 0
    
    def save(self, *args, **kwargs):
        self.archivo_regional = self.organo_jurisdiccional.archivo_regional

        with transaction.atomic():
            # Conteo independiente por órgano jurisdiccional y clasificación
            if not self.numero_paquete:
                ultimo_num = Paquete.objects.filter(
                    organo_jurisdiccional=self.organo_jurisdiccional,
                    clasificacion_paquete=self.clasificacion_paquete
                ).order_by('-numero_paquete').first()

                if ultimo_num and ultimo_num.numero_paquete:
                    self.numero_paquete = ultimo_num.numero_paquete + 1
                else:
                    self.numero_paquete = 1

            if not self.numero_paquete_letra:
                ultimo_letra = Paquete.objects.filter(
                    organo_jurisdiccional=self.organo_jurisdiccional,
                    clasificacion_paquete=self.clasificacion_paquete,
                    tipo_paquete=1
                ).order_by('-numero_paquete_letra').first()

                if ultimo_letra and ultimo_letra.numero_paquete_letra:
                    self.numero_paquete_letra = ultimo_letra.numero_paquete_letra + 1
                else:
                    self.numero_paquete_letra = 1

            if not self.letra:
                self.letra = 'A'

            if not self.clave_paquete:
                sufijo = f"-{self.clasificacion_paquete}" if self.clasificacion_paquete != 'N' else ''
                self.clave_paquete = f"{self.numero_paquete_letra}{self.letra}{sufijo}"

            #self.ultimo = True

        super().save(*args, **kwargs)

    def asignacion(self):
        return self.asignaciones_perfiles.filter(
            #usuario_perfil__estatus=1,
            estatus=1
        )
    
    @property
    def paquetes_extension(self):
        return Paquete.objects.filter(paquete_padre=self)

    @property
    def tiene_extension(self):
        return self.paquetes_extension.exists()

def archivo_upload_path(instance, filename):
    timestamp = now().strftime('%Y%m%d%H%M%S')
    # Nombre final: DOCUMENTO-PRESTAMO-EXPEDIENTE-ID-TIMESTAMP.pdf
    filename = f"DOC-PRESTAMO-EXP-{instance.id}-{timestamp}.pdf"
    # Ruta final: documentos/expediente_<id>/<archivo>.pdf
    return os.path.join('documentos', f"expediente_{instance.id}", filename)

class Expediente(models.Model):
    TIPO_EXPEDIENTE = (
        (1, "Principal"),
        (2, "Extensión"),
    )

    ESTATUS = (
        (1, "Captura"),
        (2, "En proceso"),
        (3, "Cierre")
    )

    numero = models.PositiveIntegerField(null=True, blank=True)
    letra = models.CharField(max_length=1, blank=True, null=True, help_text="Letra del expediente, por ejemplo: A, B, C")
    clave_expediente = models.CharField(max_length=10, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    expediente_toca = models.CharField(max_length=50, blank=True, null=True, verbose_name="Expediente")
    tomo = models.BooleanField(default=True)
    numero_tomo = models.CharField(max_length=100, blank=True, null=True,verbose_name="Número de tomo")
    juicio_delito = models.CharField(max_length=200, blank=True, null=True, verbose_name="Juicio") #Dropdown
    actor = models.CharField(max_length=200, blank=True, null=True, verbose_name="Actor")
    demandado = models.CharField(max_length=200, blank=True, null=True, verbose_name="Demandado")
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_sentencia = models.DateField(blank=True, null=True)
    fecha_archivo = models.DateField(blank=True, null=True)
    juez = models.CharField(max_length=200, blank=True, null=True)
    secretario = models.CharField(max_length=200, blank=True, null=True)
    beneficiario = models.CharField(max_length=200, blank=True, null=True)
    fecha_convenio = models.DateField(blank=True, null=True)
    original = models.BooleanField(default=False)
    duplicado = models.BooleanField(default=False)
    cuadernillo = models.BooleanField(default=True, verbose_name="Cuadernillo")
    acumulado = models.BooleanField(default=True, verbose_name="Acumulado")
    avocamiento = models.BooleanField(default=True, verbose_name="Avocamiento")
    numero_acumulado = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número acumulado")
    concluido = models.BooleanField(default=False)
    tipo_expediente = models.PositiveSmallIntegerField(choices=TIPO_EXPEDIENTE, default=1)
    fecha_concluido = models.DateField(blank=True, null=True)
    fecha_ejecutoria = models.DateField(blank=True, null=True)
    rango_folio_inicial = models.CharField(max_length=200, blank=True, null=True, verbose_name="Rango de folio inicial")
    rango_folio_final = models.CharField(max_length=200, blank=True, null=True, verbose_name="Rango de folio final")
    estatus_expediente = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)

    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE, related_name='expedientes')
    instancia = models.ForeignKey(Instancia,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Instancia")
    materia = models.ForeignKey(Materia,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Materia del expediente")
    distrito_judicial = models.ForeignKey(DistritoJudicial,on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Distrito Judicial o Región")
    tipo_juicio = models.ForeignKey(TipoJuicio, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de juicio")
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, blank=True, null=True)
    juzgado = models.ForeignKey(Juzgado, on_delete=models.SET_NULL, blank=True, null=True)
    archivo_regional = models.ForeignKey(ArchivoRegional, on_delete=models.CASCADE,null=True, blank=True,related_name='expedientes')
    organo_jurisdiccional = models.ForeignKey(OrganoJurisdiccional, on_delete=models.CASCADE, null=True, related_name='expedientes')
    medida_centimetros = models.CharField(max_length=200, blank=True, null=True, verbose_name="Medida en centimetros")
    # Campo de archivo
    documento_prestamo = models.FileField(upload_to=archivo_upload_path,blank=True, null=True)  # carpeta donde se guardará el archivo
    oficio_atencion = models.CharField(max_length=200, blank=True, null=True)
    numero_oficio   = models.CharField(max_length=200, blank=True, null=True)
    fecha_prestamo  = models.DateField(blank=True, null=True)
    # Campos de auditoría
    creado_por = models.ForeignKey(User,  on_delete=models.SET_NULL, null=True, related_name='expedientes_creados')
    actualizado_por = models.ForeignKey( User, on_delete=models.SET_NULL, null=True, related_name='expedientes_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True,null=True, blank=True)
    
    class Meta:
        verbose_name = "Expediente"
        verbose_name_plural = "Expedientes"
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['numero']),
            #models.Index(fields=['juzgado']),
            models.Index(fields=['fecha_inicio']),
        ]
    
    def __str__(self):
        return f"No.{self.numero} - {self.expediente_toca} - Materia: {self.materia or 'Sin materia especificada'} - {self.organo_jurisdiccional}, {self.municipio}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.numero:
                ultimo_expediente = Expediente.objects.filter(
                    organo_jurisdiccional=self.organo_jurisdiccional
                ).order_by('-numero').first()
                
                if ultimo_expediente and ultimo_expediente.numero:
                    self.numero = ultimo_expediente.numero + 1
                else:
                    self.numero = 1

        if not self.letra and self.numero:
            self.letra = 'A'
            self.clave_expediente = f"{self.numero}{self.letra}"

        try:
            expediente_anterior = Expediente.objects.get(pk=self.pk)
            if expediente_anterior.documento_prestamo and expediente_anterior.documento_prestamo != self.documento_prestamo:
                archivo_anterior_path = expediente_anterior.documento_prestamo.path
                if os.path.isfile(archivo_anterior_path):
                    os.remove(archivo_anterior_path)

        except Expediente.DoesNotExist:
            # El expediente es nuevo, no hay archivo anterior que eliminar
            pass
        super().save(*args, **kwargs)

# Bitacora Expediente

class BitacoraInstancias(models.Model):
    INSTANCIA = (
        ('1', 'Expediente'),
        ('2', 'Paquete')
    )
    tipo_instancia = models.CharField(max_length=2, choices=INSTANCIA, default=0)
    instancia_id = models.CharField(max_length=50)
    descripcion = models.TextField(null=True)
    accion = models.CharField(max_length=20, choices= [
        ('creado', 'Creado'), ('actualizado', 'Actualizado'), ('eliminado', 'Eliminado'),('asignado_a', 'Asignado a')
    ])
    valores_anteriores = models.TextField(blank=True, null=True)
    valores_nuevos = models.TextField(blank=True, null=True)
    usuario_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name='usuario_asignado_bitacora')
    usuario_accion = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='usuario_accion_bitacora')
    fecha_accion = models.DateTimeField(auto_now_add=True)
    
# models.py

class TipoCuadernillo(models.Model):
    ESTATUS = (
        (0, "No activo"),
        (1, "Activo")
    )

    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    nota = models.TextField(blank=True, null=True)
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)

    creado_por = models.ForeignKey( User, on_delete=models.SET_NULL, null=True, related_name='tipos_cuadernillos_creados' )
    actualizado_por = models.ForeignKey( User, on_delete=models.SET_NULL, null=True, related_name='tipos_cuadernillos_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Tipo de cuadernillo"
        verbose_name_plural = "Tipos de cuadernillo"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Cuadernillo(models.Model):
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='cuadernillos')
    organo_jurisdiccional = models.ForeignKey(OrganoJurisdiccional, on_delete=models.CASCADE, null=True, related_name='cuadernillos')
    tipo_cuadernillo = models.ForeignKey(TipoCuadernillo, on_delete=models.CASCADE, null=True, related_name='cuadernillos')
    tipo = models.CharField(max_length=300)
    rango_inicial = models.CharField(max_length=200, blank=True, null=True)
    rango_final = models.CharField(max_length=200, blank=True, null=True)

    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cuadernillos_creados')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cuadernillos_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Cuadernillo {self.tipo} ({self.rango_inicial}-{self.rango_final})"

class Acumulado(models.Model):
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='acumulados')
    numero_expediente = models.CharField(max_length=100)
    organo_jurisdiccional = models.ForeignKey(OrganoJurisdiccional, on_delete=models.CASCADE, null=True, related_name='acumulados')
    rango_inicial = models.CharField(max_length=200, blank=True, null=True)
    rango_final = models.CharField(max_length=200, blank=True, null=True)

    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='acumulados_creados')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='acumulados_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Acumulado {self.numero_expediente}"

class Avocamiento(models.Model):
    expediente = models.ForeignKey(Expediente, on_delete=models.CASCADE, related_name='avocamientos')
    numero_expediente = models.CharField(max_length=100)
    organo_jurisdiccional = models.ForeignKey(OrganoJurisdiccional, on_delete=models.CASCADE, null=True, related_name='avocamientos')
    rango_inicial = models.CharField(max_length=200, blank=True, null=True)
    rango_final = models.CharField(max_length=200, blank=True, null=True)

    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='avocamientos_creados')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='avocamientos_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Avocamiento {self.numero_expediente}"
    
class Perfil(models.Model):
    TIPO_PERFIL = (
        ('1', 'Capturista'),
        ('2', 'Otro')
    )
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)  # Nueva campo para descripción
    tipo_perfil = models.CharField(max_length=1, choices=TIPO_PERFIL, default=1)
    visibilidad_paquetes = models.BooleanField(default=True)  # Control explícito para visibilidad
    #
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='perfiles_creados')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='perfiles_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
    
class UsuarioPerfil(models.Model):
    ESTATUS = (
        (0, "No activo"),
        (1, "Activo")
    )

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name="perfiles_asignados" )
    perfil = models.ForeignKey( Perfil,  on_delete=models.CASCADE, null=True, related_name="usuarios_asignados" )
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)
    archivo_regional = models.ForeignKey(ArchivoRegional, on_delete=models.SET_NULL, null=True, blank=True, related_name='perfiles_por_archivo')
    organo_jurisdiccional = models.ForeignKey(OrganoJurisdiccional, on_delete=models.SET_NULL, null=True, blank=True, related_name='perfiles_por_organo')
    fecha_inicio = models.DateField(null=True, blank=True)  # Nuevo campo
    fecha_fin = models.DateField(null=True, blank=True)  # Nuevo campo
    #
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='asignaciones_perfiles_creadas')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='asignaciones_perfiles_actualizadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Asignación de Usuario a Perfil'
        verbose_name_plural = 'Usuarios Perfiles'
        unique_together = ('usuario', 'perfil')  # Evita duplicados
        ordering = ['usuario__username', 'perfil__nombre']

    def __str__(self):
        return f'{self.usuario.username} como {self.perfil.nombre} en {self.archivo_regional}'


class AsignacionPaquetePerfil(models.Model):
    """
    Asigna paquetes a un perfil de usuario específico (UsuarioPerfil), no a todos los usuarios del perfil.
    """
    ESTATUS = (
        (0, "Inactivo"),
        (1, "Activo"),
        (2, "En revisión"),
        (3, "Completado")
    )
    
    TIPO_ASIGNACION = (
        ('A', 'Automática'),
        ('M', 'Manual')
    )

    paquete = models.ForeignKey(Paquete,on_delete=models.CASCADE,related_name='asignaciones_perfiles')
    usuario_perfil = models.ForeignKey( UsuarioPerfil, on_delete=models.CASCADE, null=True, related_name='asignaciones_paquetes')
    estatus = models.PositiveSmallIntegerField(choices=ESTATUS, default=1)
    tipo_asignacion = models.CharField(max_length=1, choices=TIPO_ASIGNACION, default='M')
    fecha_limite = models.DateTimeField(null=True, blank=True)
    prioridad = models.PositiveSmallIntegerField(default=1)
    fecha_asignacion = models.DateTimeField(null=True, blank=True)
    asignado_por = models.ForeignKey( User, on_delete=models.SET_NULL, null=True, related_name='paquetes_asignados_a_perfiles')
    actualizado_por = models.ForeignKey( User, on_delete=models.SET_NULL, null=True, related_name='paquetes_asignados_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Asignación de Paquete a Perfil de Usuario'
        verbose_name_plural = 'Asignaciones Paquetes Perfiles'
        unique_together = ('paquete', 'usuario_perfil')
        ordering = ['-fecha_creacion']

    def __str__(self):
        try:
            perfil = self.usuario_perfil.perfil.nombre
            usuario = self.usuario_perfil.usuario.username
            return f'Paquete {self.paquete} asignado a {usuario} ({perfil})'
        except:
            return f'Asignación incompleta (ID: {self.id})'
    

class HistorialAsignacionPaquete(models.Model):
    TIPO_ACCION = (
        ('A', 'Asignación'),
        ('R', 'Reasignación'),
        ('D', 'Desasignación'),
        ('C', 'Cambio de estado')
    )

    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE, related_name='historial_asignaciones')
    perfil = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True, related_name='historial_asignaciones')
    usuario_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='historial_asignaciones_recibidas')
    tipo_accion = models.CharField(max_length=1, choices=TIPO_ACCION, default='A')
    estado_anterior = models.CharField(max_length=50, blank=True, null=True)
    estado_nuevo = models.CharField(max_length=50, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)  # Nuevo campo
    #
    asignado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='historial_asignaciones_realizadas')
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='historial_asignaciones_actualizados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Historial de Asignación'
        verbose_name_plural = 'Historial de Asignaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['paquete']),
            models.Index(fields=['perfil']),
            models.Index(fields=['usuario_asignado']),
        ]

    def __str__(self):
        return f'Historial: {self.paquete.id} - {self.get_tipo_accion_display()} - {self.fecha_creacion}'
