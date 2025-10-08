# Register your models here.
from django.contrib import admin
from django.contrib import messages
from .models import *
from .models import LogCambio


"""
class AdminMovimientosExhortos(admin.ModelAdmin):
    # con esto muestras los campos que deses al mostrar la lista en admin
    list_display= ['assigned_to','juzgado','observacion','acuerdo_id','exhorto_id']
    # con esto añades un campo de texto que te permite realizar la busqueda, puedes añadir mas de un atributo por el cual se filtrará
    search_fields = ['assigned_to__first_name','assigned_to__last_name','exhorto__pk','acuerdo__pk','observacion','juzgado__nombre']
    # con esto añadiras una lista desplegable con la que podras filtrar (activo es un atributo booleano)
    list_filter = ['exhorto_id','acuerdo_id']
    
class AdminOficios(admin.ModelAdmin):
    # con esto muestras los campos que deses al mostrar la lista en admin
    list_display= ['tipo','documento','folio','exhorto','juzgado','firma_secretario','firma_juez']
    # con esto añades un campo de texto que te permite realizar la busqueda, puedes añadir mas de un atributo por el cual se filtrará
    search_fields = ['tipo','contenido']
    # con esto añadiras una lista desplegable con la que podras filtrar (activo es un atributo booleano)
    list_filter = ['tipo']

class AdminAcuerdoActuario(admin.ModelAdmin):
    list_display= ['actuario','acuerdo','acuerdo_folio','acuerdo_estatus', 'acuerdo_tipo', 'asignado_at', 'asignado_por', 'acuerdo_juzgado']
    search_fields = ['actuario__first_name','actuario__last_name','acuerdo__exhorto__folio_origen' ]
    #pass
    def acuerdo_folio(self, obj):
        return obj.acuerdo.folio if obj.acuerdo else None
    
    def acuerdo_estatus(self, obj):
        return obj.acuerdo.get_estatus_display() if obj.acuerdo else None
    
    def acuerdo_tipo(self, obj):
        return obj.acuerdo.get_tipo_display() if obj.acuerdo else None
    
    def acuerdo_juzgado(self, obj):
        return obj.acuerdo.created_by.juzgado if obj.acuerdo else None
    
    def asignado_por(self, obj):
        return obj.created_by
"""
#admin.site.register(AcuerdoActuario, AdminAcuerdoActuario)

class AdminUserConfig(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__first_name', 'user__last_name']
    list_filter = ['user_id']

admin.site.register(Estado)
admin.site.register(Municipio)
admin.site.register(ArchivoRegional)
admin.site.register(Juzgado)
admin.site.register(NombreJuzgadoHistorico)
admin.site.register(Instancia)
admin.site.register(Materia)
admin.site.register(DistritoJudicial)
admin.site.register(TipoJuicio)
admin.site.register(RegionJudicial)
admin.site.register(OrganoJurisdiccional)
#admin.site.register(UserConfig)
admin.site.register(UserConfig, AdminUserConfig) 
#admin.site.register(UserConfig, AdminUserConfig)
#admin.site.register(LogCambio)


@admin.register(LogCambio)
class LogCambioAdmin(admin.ModelAdmin):
    list_display = ['modelo', 'instancia_id', 'accion', 'usuario', 'fecha_accion']
    actions = ['restaurar_objeto']

    def restaurar_objeto(self, request, queryset):
        restaurados = 0
        errores = 0
        
        for log in queryset:
            try:
                log.restaurar_instancia()
                restaurados += 1
            except Exception as e:
                errores += 1
                self.message_user(request, f'Error al restaurar {log}: {e}', messages.ERROR)

        if restaurados:
            self.message_user(request, f'{restaurados} objeto(s) restaurado(s) correctamente.', messages.SUCCESS)

    restaurar_objeto.short_description = "Restaurar objetos eliminados"