from django.urls import path

from .views import (
    ArchivoRegionalListView, ArchivoRegionalCreateView, ArchivoRegionalUpdateView,
    JuzgadoListView, JuzgadoCreateView, JuzgadoUpdateView
)

from .views_files.instancia_views import InstanciaListView,InstanciaCreateView,InstanciaUpdateView
from .views_files.materia_views import MateriaListView,MateriaCreateView,MateriaUpdateView,MateriaDetailView
from .views_files.tipojuicio_views import TipoJuicioListView,TipoJuicioCreateView,TipoJuicioUpdateView,TipoJuicioDetailView
from .views_files.distritojudicial_views import DistritoJudicialListView,DistritoJudicialCreateView,DistritoJudicialUpdateView,DistritoJudicialDetailView
from .views_files.tipojuzgado_views import TipoJuzgadoListView,TipoJuzgadoCreateView,TipoJuzgadoUpdateView,TipoJuzgadoDetailView
from .views_files.usuario_configuracion_views import (
    UserListView, UserCreateView, 
    UserUpdateView, UserDetailView, 
    UserDeleteView
)
from .views_files.regionjudicial_views import RegionJudicialListView,RegionJudicialCreateView,RegionJudicialUpdateView,RegionJudicialDetailView 
from .views_files.organojurisdiccional_views import OrganoJurisdiccionalListView,OrganoJurisdiccionalCreateView,OrganoJurisdiccionalUpdateView 
from .views_files.estadisticas_view import EstadisticasDashboardView

app_name = 'administracion'

urlpatterns = [
    # Archivos Regionales
    path('archivos-regional/', ArchivoRegionalListView.as_view(), name='lista_archivos_regional'),
    path('archivos-regional/nuevo/', ArchivoRegionalCreateView.as_view(), name='nuevo_archivo_regional'),
    path('archivos-regional/editar/<int:pk>/', ArchivoRegionalUpdateView.as_view(), name='editar_archivo_regional'),
    
    # Juzgados
    path('juzgados/', JuzgadoListView.as_view(), name='lista_juzgados'),
    path('juzgados/nuevo/', JuzgadoCreateView.as_view(), name='nuevo_juzgado'),
    path('juzgados/editar/<int:pk>/', JuzgadoUpdateView.as_view(), name='editar_juzgado'),

    # Instancias
    path('instancias/', InstanciaListView.as_view(), name='lista_instancias'),
    path('instancias/nueva/', InstanciaCreateView.as_view(), name='nueva_instancia'),
    path('instancias/editar/<int:pk>/', InstanciaUpdateView.as_view(), name='editar_instancia'),

    # Materia
    path('materias/', MateriaListView.as_view(), name='lista_materias'),
    path('materias/nueva/', MateriaCreateView.as_view(), name='nueva_materia'),
    path('materias/editar/<int:pk>/', MateriaUpdateView.as_view(), name='editar_materia'),
    path('materias/ver/<int:pk>/', MateriaDetailView.as_view(), name='ver_materia'),

    # Juicios
    path('tipos-juicio/', TipoJuicioListView.as_view(), name='lista_tipos_juicio'),
    path('tipos-juicio/nuevo/', TipoJuicioCreateView.as_view(), name='nuevo_tipo_juicio'),
    path('tipos-juicio/editar/<int:pk>/', TipoJuicioUpdateView.as_view(), name='editar_tipo_juicio'),
    path('tipos-juicio/ver/<int:pk>/', TipoJuicioDetailView.as_view(), name='ver_tipo_juicio'),

    # Distrito Judicial
    path('distritos-judiciales/', DistritoJudicialListView.as_view(), name='lista_distritos'),
    path('distritos-judiciales/nuevo/', DistritoJudicialCreateView.as_view(), name='nuevo_distrito'),
    path('distritos-judiciales/editar/<int:pk>/', DistritoJudicialUpdateView.as_view(), name='editar_distrito'),
    path('distritos-judiciales/ver/<int:pk>/', DistritoJudicialDetailView.as_view(), name='ver_distrito'),

    # Tipo juzgado
    #path('tipos-juzgado/', TipoJuzgadoListView.as_view(), name='lista_tipos_juzgado'),
    #path('tipos-juzgado/nuevo/', TipoJuzgadoCreateView.as_view(), name='nuevo_tipo_juzgado'),
    #path('tipos-juzgado/editar/<int:pk>/', TipoJuzgadoUpdateView.as_view(), name='editar_tipo_juzgado'),
    #path('tipos-juzgado/ver/<int:pk>/', TipoJuzgadoDetailView.as_view(), name='ver_tipo_juzgado'),
    #path('tipos-juzgado/eliminar/<int:pk>/', TipoJuzgadoDeleteView.as_view(), name='eliminar_tipo_juzgado'),

    # Region judicial
    path('regiones-judiciales/', RegionJudicialListView.as_view(), name='lista_regiones'),
    path('regiones-judiciales/nuevo/', RegionJudicialCreateView.as_view(), name='nueva_region'),
    path('regiones-judiciales/editar/<int:pk>/', RegionJudicialUpdateView.as_view(), name='editar_region'),
    path('regiones-judiciales/ver/<int:pk>/', RegionJudicialDetailView.as_view(), name='ver_region'),

    # Organo juridiccial
    path('organo-juridiccial/', OrganoJurisdiccionalListView.as_view(), name='lista_organosjurisdiccionales'),
    path('organo-juridiccial/nuevo/', OrganoJurisdiccionalCreateView.as_view(), name='nuevo_organojurisdiccional'),
    path('organo-juridiccial/editar/<int:pk>/', OrganoJurisdiccionalUpdateView.as_view(), name='editar_organojurisdiccional'),

    path('estadisticas/', EstadisticasDashboardView.as_view(), name='dashboard_estadisticas'),

    #Usuarios
    path('usuarios/', UserListView.as_view(), name='lista_usuarios'),
    path('usuario/nuevo/', UserCreateView.as_view(), name='nuevo_usuario'),
    path('usuario/<int:pk>/', UserDetailView.as_view(), name='ver_usuario'),
    path('usuario/<int:pk>/editar/', UserUpdateView.as_view(), name='editar_usuario'),
    path('usuario/<int:pk>/eliminar/', UserDeleteView.as_view(), name='eliminar_usuario'),

]