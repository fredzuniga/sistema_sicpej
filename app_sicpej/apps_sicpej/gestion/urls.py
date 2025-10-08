from django.urls import path
from .views_files.paquete_views import * 
from .views_files.expediente_views import * 
from .views_files.pdf_views import *
from .views_files.api_views import *
#PaqueteListView,PaqueteCreateView, PaqueteUpdateView,PaqueteDetailView,PaqueteDeleteView, AsignarPaquetePerfilView
from .views_files.tipo_cuadernillo_views import *
from .views_files.perfiles_views import *
from .views_files.usuario_perfil_views import *

app_name = 'gestion'

urlpatterns = [
    # Gestión de paquetes
    #path('paquetes/nuevo/', PaqueteCreateView.as_view(), name='nuevo_paquete'),
    # PaqueteCreateMultipleView
    path('paquetes/nuevo/', PaqueteCreateMultipleView.as_view(), name='nuevo_paquete'),
    path('paquete/<int:paquete_id>/crear-extension-paquete/', CrearExtensionPaqueteAutoView.as_view(), name='crear_extension_paquete'),
    path('paquetes/nuevo/admin/', PaqueteCreateViewAdmin.as_view(), name='nuevo_paquete_admin'),

    # Paquetes
    #path('paquetes/', PaqueteListView.as_view(), name='lista_paquetes'),
    path('paquetes/editar/<int:pk>/', PaqueteUpdateView.as_view(), name='editar_paquete'),
    path('paquetes/ver/<int:pk>/detalle', PaqueteDetailView.as_view(), name='ver_paquete'),
    path('paquetes/eliminar/<int:pk>/', PaqueteDeleteView.as_view(), name='eliminar_paquete'),
    path('paquetes/lista/', PaqueteListView.as_view(), name='lista_paquetes'),
    path('paquetes/asignar/', AsignarPaquetePerfilView.as_view(), name='asignar_paquetes'),


    path('perfiles/', PerfilListView.as_view(), name='lista_perfiles'),
    path('perfiles/nuevo/', PerfilCreateView.as_view(), name='nuevo_perfil'),
    path('perfiles/<int:pk>/editar/', PerfilUpdateView.as_view(), name='editar_perfil'),
    path('usuarios-perfiles/', UsuarioPerfilListView.as_view(), name='lista_usuariosperfiles'),
    path('usuarios-perfiles/nuevo/', UsuarioPerfilCreateView.as_view(), name='nuevo_usuarioperfil'),
    path('usuarios-perfiles/<int:pk>/editar/', UsuarioPerfilUpdateView.as_view(), name='editar_usuarioperfil'),
    path('paquetes/asignados/', PaquetesAsignadosUsuarioView.as_view(), name='paquetes_asignados'),
    
    # Selección inicial
    #Solo admin
    path('paquetes/seleccion/', SeleccionArchivoRegionalView.as_view(), name='seleccion_archivo'),
    #Capturista
    path('paquetes/seleccion-juzgado/<int:archivo_id>/', SeleccionJuzgadoView.as_view(), name='seleccion_juzgado'),
    path('paquetes/organo-jurisdiccional/<int:archivo_id>/', SeleccionOrganoJurisdiccionalView.as_view(), name='seleccion_organo_jurisdiccional'),
    
    #path('paquetes/editar/<int:pk>/', PaqueteUpdateView.as_view(), name='editar_paquete'),
    # Cambiar selección
    path('paquetes/cambiar-seleccion/', CambiarSeleccionView.as_view(), name='cambiar_seleccion'),

    # ################################################################################################################

    # Tipos de cuadernillos
    path('tipo-cuadernillos/', TipoCuadernilloListView.as_view(), name='lista_tipo_cuadernillos'),
    path('tipo-cuadernillos/nuevo/', TipoCuadernilloCreateView.as_view(), name='nuevo_tipo_cuadernillo'),
    path('tipo-cuadernillos/<int:pk>/editar/', TipoCuadernilloUpdateView.as_view(), name='editar_tipo_cuadernillo'),
    path('tipo-cuadernillos/<int:pk>/', TipoCuadernilloDetailView.as_view(), name='detalle_tipo_cuadernillo'),

    path('expediente/paquete/<int:paquete_id>/registrar-expediente/', CrearExpedienteRedireccionView.as_view(), name='nuevo_expediente_rapido'),
    path('expediente/paquete/<int:paquete_id>/nuevo/', ExpedienteCreateView.as_view(), name='nuevo_expediente'),
    path('expediente/<int:pk>/editar/', ExpedienteUpdateView.as_view(), name='editar_expediente'),
    path('expediente/<int:pk>/', ExpedienteDetailView.as_view(), name='detalle_expediente'),
    path('expedientes/', ExpedienteListView.as_view(), name='lista_expedientes'),
    path('expedientes/<int:organo_id>/', ExpedienteListView.as_view(), name='lista_expedientes_por_organo'),
    path('expedientes/mover/paquete', MoverExpedientesAPaqueteView.as_view(), name='mover_expedientes_paquete'),

    # ################################################################################################################

    #reporte pdf
    path('paquete/<int:paquete_id>/pdf/', generar_pdf_paquete, name='generar_pdf_paquete'),
    
    # API endpoints
    path('api/juzgados/', juzgados_por_materia, name='api_juzgados_por_materia'),
    path('api/organos-jurisdiccionales/', organojurisdiccional_por_materia, name='api_organos_jurisdiccionales_por_materia'),
    #   lista_organos_jurisdiccionales
    path('api/organos-jurisdiccionales-general/', lista_organos_jurisdiccionales, name='api_lista_organos_jurisdiccionales'),
    path('api/tipos-cuadernillos/', lista_tipos_cuadernillos, name='api_lista_tipos_cuadernillos'),
    path('api/nombre-usuario-perfiles/', nombre_usuario_perfil, name='api_nombre_usuario_perfil'),
    path('api/paquete/cambiar-estatus/', cambiar_estatus_paquete, name='cambiar_estatus_paquete'),
    path('api/validar-expediente-tomo/', validar_expediente_tomo, name='api_validar_expediente_tomo'),
    path('api/expedientes/<int:pk>/detalle', ExpedienteDetailAPIView.as_view(), name='expediente-detalle'),
    path('api/expedientes/detalle/', ExpedienteDetailPostAPIView.as_view(), name='expediente-detalle-post'),

    
    # Cuadernillo endpoints
    path('cuadernillos/expediente/<int:expediente_id>/', cuadernillos_por_expediente, name='cuadernillos_por_expediente'),
    path('cuadernillo/create/', create_cuadernillo,name='crear_cuadernillo'),
    path('cuadernillo/update/<int:pk>/', update_cuadernillo,name='modificar_cuadernillo'),
    path('cuadernillo/delete/<int:pk>/', delete_cuadernillo,name='eliminar_cuadernillo'),

    # Acumulado
    path('acumulado/expediente/<int:expediente_id>/', acumulado_por_expediente, name='acumulados_por_expediente'),
    path('acumulado/create/', create_acumulado, name='crear_acumulado'),
    path('acumulado/update/<int:pk>/', update_acumulado,name='modificar_acumulado'),
    path('acumulado/delete/<int:pk>/', delete_acumulado,name='eliminar_acumulado'),

    # Avocamiento
    path('avocamiento/expediente/<int:expediente_id>/', avocamientos_por_expediente, name='avocamientos_por_expediente'),
    path('avocamiento/create/', create_avocamiento),
    path('avocamiento/update/<int:pk>/', update_avocamiento),
    path('avocamiento/delete/<int:pk>/', delete_avocamiento),
]