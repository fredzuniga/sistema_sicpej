from django.views.generic import TemplateView
from django.db.models import Count, Avg, F, ExpressionWrapper, fields, Value
from django.db.models.functions import ExtractMonth, ExtractYear, Concat
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict
from apps_sicpej.gestion.models import Paquete, Expediente
#from apps_sicpej.administracion.models import Juzgado, ArchivoRegional
class EstadisticasDashboardView(TemplateView):
    template_name = 'estadisticas/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        hoy = now.date()
        current_year = now.year
        current_month = now.month
        
        user = self.request.user
        archivo_regional = None
        if not user.is_superuser:
            try:
                archivo_regional = user.configuracion.archivo_regional
            except AttributeError:
                archivo_regional = None

        print(archivo_regional)

        # 1. Datos básicos
        context.update(self.get_basic_stats(hoy, current_year,archivo_regional))
        # 2. Tendencias temporales
        context.update(self.get_temporal_trends(current_year,archivo_regional))
        
        # 3. Eficiencia de procesamiento
        #context.update(self.get_processing_efficiency())
        
        # 4. Distribución geográfica
        #context.update(self.get_geographic_distribution())
        
        # 5. Tendencias temporales
        
        
        return context
    
    def get_basic_stats(self, hoy, current_year, archivo_regional):
        """Datos básicos del dashboard"""
        filters = {}
        if archivo_regional:
            filters['archivo_regional'] = archivo_regional
        
        return {
            'ultimo_paquete': Paquete.objects.filter(**filters).order_by('-fecha_creacion').first(),
            'paquetes_hoy': Paquete.objects.filter(fecha_creacion__date=hoy, **filters).count(),
            'expedientes_hoy': Expediente.objects.filter(fecha_creacion__date=hoy, **filters).count(),
            'total_paquetes': Paquete.objects.filter(**filters).count(),
            'total_expedientes': Expediente.objects.filter(**filters).count(),
            'current_year': current_year,
            'archivo_regional': archivo_regional.nombre if archivo_regional else 'Todos los archivos',
            'paquetes_regionales_data': self.calculate_paquetes_archivo_regional(current_year),
            'paquetes_organo_usuario': self.calculate_paquetes_organo_usuario(current_year,archivo_regional),
            'expedientes_municipio_captura' : self.calculate_expedientes_municipio_estatus(current_year,archivo_regional,1),
            'expedientes_municipio_cerrada' : self.calculate_expedientes_municipio_estatus(current_year,archivo_regional,3)
        }
    
    def get_temporal_trends(self, current_year, archivo_regional):
        """Tendencias temporales"""
        filters = {}
        if archivo_regional:
            filters['archivo_regional'] = archivo_regional
        
        dato_anio_actual_paquetes = Paquete.objects.filter(
            fecha_creacion__year=current_year,**filters
        ).annotate(
            month=ExtractMonth('fecha_creacion')
        ).values('month').annotate(
            total=Count('id')
        ).order_by('month')
        
        data = {item['month']: item['total'] for item in dato_anio_actual_paquetes}
        print(data)
        
        paquetes_por_mes_data = []
        for month in range(1, 13):
            paquetes_por_mes_data.append({
                'month': month,
                'total': data.get(month, 0)
            })

        dato_anio_anterior_paquetes = Paquete.objects.filter(
            fecha_creacion__year=current_year-1,**filters
        ).annotate(
            month=ExtractMonth('fecha_creacion')
        ).values('month').annotate(
            total=Count('id')
        ).order_by('month')

        data_anio_anterior = {item['month']: item['total'] for item in dato_anio_anterior_paquetes}
        
        paquetes_por_mes_data_anio_anterior = []
        for month in range(1, 13):
            paquetes_por_mes_data_anio_anterior.append({
                'month': month,
                'total': data_anio_anterior.get(month, 0)
            })
        
        # Proyección de crecimiento
        filters_growth_rate = {}
        if archivo_regional:
            filters_growth_rate['archivo_regional'] = archivo_regional
        tasa_crecimiento_anual = self.calculate_growth_rate(current_year, current_year-1,filters_growth_rate)
        return {
            'paquetes_por_mes_anio_actual': list(paquetes_por_mes_data),
            'paquetes_por_mes_anio_anterior': list(paquetes_por_mes_data_anio_anterior),
            'tasa_crecimiento_anual': tasa_crecimiento_anual,
        }
    
    def calculate_growth_rate(self, current_year, last_year, filters):
        """Calcula la tasa de crecimiento interanual"""
        current_count = Paquete.objects.filter(fecha_creacion__year=current_year,**filters).count()
        last_count = Paquete.objects.filter(fecha_creacion__year=last_year,**filters).count()
        
        if last_count == 0:
            return 0
        return ((current_count - last_count) / last_count) * 100
    

    def calculate_paquetes_archivo_regional(self, current_year):
        data = Paquete.objects.filter(fecha_creacion__year=current_year).values('archivo_regional__nombre').annotate(total=Count('id')).order_by('archivo_regional__nombre')
        

        labels = [d['archivo_regional__nombre'] for d in data]
        series = [d['total'] for d in data]
        total_general = sum(series)

        paquetes_regionales_data = {
            'labels': labels,
            'series': series,
            'anio': current_year,
            'total': total_general
        }

        return paquetes_regionales_data

    def calculate_paquetes_organo_usuario(self, current_year, archivo_regional_id):
        if archivo_regional_id:
            data = (
            Paquete.objects.filter(
                    fecha_creacion__year=current_year,
                    organo_jurisdiccional__archivo_regional_id=archivo_regional_id
                )
                .annotate(
                    nombre_completo=Concat(
                        'organo_jurisdiccional__nombre',
                        Value(', '),
                        'organo_jurisdiccional__municipio__descripcion'
                    )
                )
                .values('nombre_completo')  # 👈 usamos el campo concatenado
                .annotate(total=Count('id'))  # agrupamos por el nombre completo
                .order_by('nombre_completo')
            )
        else:
            data = (
                Paquete.objects.filter(
                    fecha_creacion__year=current_year,
                    # organo_jurisdiccional__archivo_regional_id=archivo_regional_id
                )
                .annotate(
                    nombre_completo=Concat(
                        'organo_jurisdiccional__nombre',
                        Value(', '),
                        'organo_jurisdiccional__municipio__descripcion'
                    )
                )
                .values('nombre_completo')  # 👈 usamos el campo concatenado
                .annotate(total=Count('id'))  # agrupamos por el nombre completo
                .order_by('nombre_completo')
            )

        #print("archivo_regional_id: ", archivo_regional_id)
        #print("calculate_paquetes_organo_usuario: " , data)

        labels = [d['nombre_completo'] for d in data]
        series = [d['total'] for d in data]
        total_general = sum(series)

        paquetes_por_organo_data = {
            'labels': labels,
            'series': series,
            'anio': current_year,
            'total': total_general,
        }

        return paquetes_por_organo_data
    
    def calculate_expedientes_municipio_estatus(self, current_year, archivo_regional_id, estatus_expediente):
        if archivo_regional_id:
            data = (
                Expediente.objects.filter(
                    fecha_creacion__year=current_year,
                    estatus_expediente= estatus_expediente,  # 👈 solo en estatus "Captura"
                    organo_jurisdiccional__archivo_regional_id=archivo_regional_id
                )
                .values('organo_jurisdiccional__municipio__descripcion')  # 👈 agrupación por municipio
                .annotate(total=Count('id'))  # contar expedientes por municipio
                .order_by('organo_jurisdiccional__municipio__descripcion')
            )
        else:
            data = (
                Expediente.objects.filter(
                    fecha_creacion__year=current_year,
                    estatus_expediente=estatus_expediente  # 👈 solo en estatus "Captura"
                )
                .values('organo_jurisdiccional__municipio__descripcion')
                .annotate(total=Count('id'))
                .order_by('organo_jurisdiccional__municipio__descripcion')
            )

        # Preparar los datos
        labels = [d['organo_jurisdiccional__municipio__descripcion'] for d in data]
        series = [d['total'] for d in data]
        total_general = sum(series)

        expedientes_por_municipio = {
            'labels': labels,
            'series': series,
            'anio': current_year,
            'total': total_general,
        }

        return expedientes_por_municipio

    
    # ------------------------------------------------------------------------------------
    
    def get_processing_efficiency(self):
        """Eficiencia de procesamiento"""
        # Tiempo promedio de procesamiento
        avg_processing = Procesamiento.objects.annotate(
            processing_time=ExpressionWrapper(
                F('fecha_fin') - F('fecha_inicio'),
                output_field=fields.DurationField()
            )
        ).aggregate(avg_time=Avg('processing_time'))
        
        # Paquetes procesados dentro del tiempo estimado
        on_time_packages = Paquete.objects.filter(
            procesamiento__fecha_fin__lte=F('procesamiento__fecha_estimada')
        ).count()
        total_processed = Paquete.objects.filter(procesamiento__isnull=False).count()
        on_time_percentage = (on_time_packages / total_processed * 100) if total_processed > 0 else 0
        
        return {
            'avg_processing_time': avg_processing['avg_time'],
            'on_time_percentage': round(on_time_percentage, 2),
            'on_time_packages': on_time_packages,
            'total_processed': total_processed,
        }
    
    def get_geographic_distribution(self):
        """Distribución geográfica"""
        paquetes_por_region = Paquete.objects.values('region__nombre').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        expedientes_por_municipio = Expediente.objects.values('municipio__nombre').annotate(
            total=Count('id')
        ).order_by('-total')[:5]
        
        return {
            'paquetes_por_region': paquetes_por_region,
            'expedientes_por_municipio': expedientes_por_municipio,
        }
    