from django.contrib import admin
from .models import *

from django.utils.html import format_html

class ExpedienteAdmin(admin.ModelAdmin):
    """
    list_display = (
        'clave_expediente',
        'fecha_creacion',
        'fecha_actualizacion',
        'clonar_link',
    )
    """
    #readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    actions = ['clonar_registros']

    def clonar_registros(self, request, queryset):
        for obj in queryset:
            obj.pk = None  # Setea pk a None para crear un nuevo registro
            obj.save()
        self.message_user(request, "Registros clonados correctamente.")
    clonar_registros.short_description = "Clonar registros seleccionados"

    def clonar_link(self, obj):
        return format_html(
            '<a href="{}clone/">Clonar</a>',
            obj.id
        )
    clonar_link.short_description = 'Clonar'

admin.site.register(Expediente, ExpedienteAdmin)

# Paquete con campo solo lectura
@admin.register(Paquete)
class PaqueteAdmin(admin.ModelAdmin):
    readonly_fields = ('fecha_registro',)

# los demás modelos sin personalización
admin.site.register(Acumulado)
admin.site.register(Cuadernillo)
admin.site.register(Avocamiento)
admin.site.register(TipoCuadernillo)
admin.site.register(Perfil)
admin.site.register(UsuarioPerfil)
admin.site.register(AsignacionPaquetePerfil)
admin.site.register(HistorialAsignacionPaquete)
admin.site.register(BitacoraInstancias)
