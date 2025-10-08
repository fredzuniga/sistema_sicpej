from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from apps_sicpej.administracion.models import Juzgado, ArchivoRegional, UserConfig, Materia, OrganoJurisdiccional
from ..models import Paquete
from ..forms_files.paquete_forms import PaqueteForm
from django.db.models import F, Count, Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
import json
from django.views.decorators.http import require_GET
from collections import defaultdict
from .tools import filtrar_y_paginar_queryset

#from ..models import TipoJuicio
#from ..forms_files.tipojuicio_forms import TipoJuicioForm

"""class PaqueteListView( ListView):
    model = Paquete
    template_name = 'paquete/lista_paquetes.html'
    context_object_name = 'paquetes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('juzgado').annotate(
            num_expedientes=Count('expedientes')
        )
        search = self.request.GET.get('search')
        estatus = self.request.GET.get('estatus')
        juzgado_id = self.request.GET.get('juzgado')
        
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        if estatus:
            queryset = queryset.filter(estatus=estatus)
        if juzgado_id:
            queryset = queryset.filter(juzgado_id=juzgado_id)
            
        return queryset.order_by('-fecha_registro')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['juzgados'] = Juzgado.objects.filter(estatus=1)
        return context 

class PaqueteBaseView(LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Verificar que el usuario está autenticado (gracias a LoginRequiredMixin)
        user = self.request.user
        
        try:
            # Obtener la configuración del usuario
            user_config = user.config
            
            # Intentar obtener primero de la sesión, luego de la configuración del usuario
            juzgado_id = self.request.session.get('juzgado_seleccionado') or (user_config.juzgado.id if user_config.juzgado else None)
            archivo_id = self.request.session.get('archivo_seleccionado') or (user_config.archivo_regional.id if user_config.archivo_regional else None)
            
            # Agregar al contexto
            if juzgado_id:
                context['juzgado_actual'] = Juzgado.objects.get(pk=juzgado_id)
            if archivo_id:
                context['archivo_actual'] = ArchivoRegional.objects.get(pk=archivo_id)
            
            # Agregar la configuración completa del usuario al contexto
            context['user_config'] = user_config
            
        except UserConfig.DoesNotExist:
            # Si el usuario no tiene configuración, crear una básica
            user_config = UserConfig.objects.create(user=user, creado_por=user)
            context['user_config'] = user_config
            # Puedes agregar un mensaje para informar al administrador
            #if user.is_staff:
            #    messages.info(self.request, "Se creó una configuración inicial para tu usuario.")
        
        return context

    def dispatch(self, request, *args, **kwargs):
        # Verificación adicional (aunque LoginRequiredMixin ya hace esto)
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Verificar si el usuario tiene configuración
        if not hasattr(request.user, 'config'):
            # Crear configuración básica si no existe
            UserConfig.objects.get_or_create(
                user=request.user,
                defaults={'creado_por': request.user}
            )
        
        return super().dispatch(request, *args, **kwargs) 

class PaqueteBaseView(LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obtener IDs - Jerarquía: Sesión > BD (UserConfig)
        juzgado_id, archivo_id = self._obtener_ids_seleccion()
        
        # Obtener objetos completos
        context.update(self._obtener_objetos_seleccion(juzgado_id, archivo_id))
        
        # Agregar configuración de usuario al contexto
        context['user_config'] = getattr(user, 'config', None)
        
        return context
    
    def _obtener_ids_seleccion(self):
        #Obtiene los IDs de juzgado y archivo con la jerarquía correcta
        user = self.request.user
        session = self.request.session
        
        # 1. Intentar obtener de la sesión
        juzgado_id = session.get('juzgado_seleccionado')
        archivo_id = session.get('archivo_seleccionado')
        
        # 2. Si no hay en sesión, buscar en la BD (UserConfig)
        if not juzgado_id or not archivo_id:
            try:
                user_config = user.config
                if not juzgado_id and user_config.juzgado:
                    juzgado_id = user_config.juzgado.id
                    session['juzgado_seleccionado'] = juzgado_id
                
                if not archivo_id and user_config.archivo_regional:
                    archivo_id = user_config.archivo_regional.id
                    session['archivo_seleccionado'] = archivo_id
                    
            except (UserConfig.DoesNotExist, AttributeError):
                pass
        
        return juzgado_id, archivo_id
    
    def _obtener_objetos_seleccion(self, juzgado_id, archivo_id):
        
        result = {}
        
        if juzgado_id:
            try:
                result['juzgado_actual'] = Juzgado.objects.get(pk=juzgado_id)
            except Juzgado.DoesNotExist:
                del self.request.session['juzgado_seleccionado']
        
        if archivo_id:
            try:
                result['archivo_actual'] = ArchivoRegional.objects.get(pk=archivo_id)
            except ArchivoRegional.DoesNotExist:
                del self.request.session['archivo_seleccionado']
        
        return result 

class PaqueteBaseView(LoginRequiredMixin):
    # URLs para redirección (pueden ser sobrescritas en clases hijas)
    seleccion_archivo_url = 'gestion:seleccion_archivo'
    seleccion_juzgado_url = 'gestion:seleccion_juzgado'
    
    def dispatch(self, request, *args, **kwargs):
        # 1. Verificar archivo regional
        archivo_id = request.session.get('archivo_seleccionado')
        if not archivo_id:
            # Intentar obtener de la configuración del usuario
            if hasattr(request.user, 'config') and request.user.config.archivo_regional:
                archivo_id = request.user.config.archivo_regional.id
                request.session['archivo_seleccionado'] = archivo_id
            else:
                messages.warning(request, 'Debe seleccionar un archivo regional')
                return redirect(reverse(self.seleccion_archivo_url))
        
        # 2. Verificar juzgado
        juzgado_id = request.session.get('juzgado_seleccionado')
        if not juzgado_id:
            # Intentar obtener de la configuración del usuario
            if hasattr(request.user, 'config') and request.user.config.juzgado:
                juzgado_id = request.user.config.juzgado.id
                request.session['juzgado_seleccionado'] = juzgado_id
            else:
                messages.warning(request, 'Debe seleccionar un juzgado')
                return redirect(reverse(
                    self.seleccion_juzgado_url, 
                    args=[request.session.get('archivo_seleccionado')]
                ))
        
        # 3. Verificar que los IDs existen en la BD
        try:
            ArchivoRegional.objects.get(pk=archivo_id)
            Juzgado.objects.get(pk=juzgado_id)
        except (ArchivoRegional.DoesNotExist, Juzgado.DoesNotExist):
            # Limpiar sesión si los IDs no son válidos
            if ArchivoRegional.objects.filter(pk=archivo_id).exists():
                request.session.pop('juzgado_seleccionado', None)
                messages.warning(request, 'El juzgado seleccionado ya no existe')
                return redirect(reverse(
                    self.seleccion_juzgado_url,
                    args=[archivo_id]
                ))
            else:
                request.session.pop('archivo_seleccionado', None)
                request.session.pop('juzgado_seleccionado', None)
                messages.warning(request, 'El archivo regional seleccionado ya no existe')
                return redirect(reverse(self.seleccion_archivo_url))
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener objetos completos para el template
        archivo_id = self.request.session['archivo_seleccionado']
        juzgado_id = self.request.session['juzgado_seleccionado']
        
        context['archivo_actual'] = ArchivoRegional.objects.get(pk=archivo_id)
        context['juzgado_actual'] = Juzgado.objects.get(pk=juzgado_id)
        context['user_config'] = getattr(self.request.user, 'config', None)
        
        return context  """

class PaqueteBaseView:
    """def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener selección actual de la sesión
        juzgado_id = self.request.session.get('juzgado_seleccionado')
        archivo_id = self.request.session.get('archivo_seleccionado')
        
        if juzgado_id and archivo_id:
            context['juzgado_actual'] = Juzgado.objects.get(pk=juzgado_id)
            context['archivo_actual'] = ArchivoRegional.objects.get(pk=archivo_id)
        
        return context """
    
    seleccion_archivo_url = 'gestion:seleccion_archivo'
    seleccion_juzgado_url = 'gestion:seleccion_juzgado'
    
    def dispatch(self, request, *args, **kwargs):
        #is_superuser
        if not request.user.is_superuser: 
            archivo_id = request.session.get('archivo_seleccionado')
            if not archivo_id:
                # Intentar obtener de la configuración del usuario
                if request.user.configuracion.archivo_regional:
                    archivo_id = request.user.configuracion.archivo_regional.id
                    request.session['archivo_seleccionado'] = archivo_id
                else:
                    messages.warning(request, 'Debe seleccionar un archivo regional')
                    return redirect(reverse(self.seleccion_archivo_url))
        else:
            if not request.session.get('archivo_seleccionado'):
                messages.warning(request, 'Debe seleccionar un archivo regional')
                return redirect(reverse(self.seleccion_archivo_url))
        
        
        # 2. Verificar juzgado
        if not request.user.is_superuser:
            juzgado_id = request.session.get('juzgado_seleccionado')
            if not juzgado_id:
                # Intentar obtener de la configuración del usuario
                if request.user.configuracion.juzgado:
                    print("request.user.configuracion.juzgado --->", request.user.configuracion.juzgado)
                    juzgado_id = request.user.configuracion.juzgado.id
                    request.session['juzgado_seleccionado'] = juzgado_id
                else:
                    print("messages")
                    messages.warning(request, 'Debe seleccionar un juzgado')
                    return redirect(reverse(
                        self.seleccion_juzgado_url, 
                        args=[request.session.get('archivo_seleccionado')]
                    ))
        else:
            if not request.session.get('juzgado_seleccionado'):
                messages.warning(request, 'Debe seleccionar un juzgado')
                return redirect(reverse('gestion:seleccion_juzgado', args=[request.session.get('archivo_seleccionado')]))
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener objetos completos para el template
        
        archivo_id = self.request.session.get('archivo_seleccionado')
        juzgado_id = self.request.session.get('juzgado_seleccionado')

        if archivo_id is not None and juzgado_id is not None:
            context['archivo_actual'] = ArchivoRegional.objects.get(pk=archivo_id)
            context['juzgado_actual'] = Juzgado.objects.get(pk=juzgado_id)
        else:
            # manejar el caso cuando no existe la variable de sesión
            context['archivo_actual'] = None
            context['juzgado_actual'] = None
        
        return context
    
# Se aplica solo para administradores
class PaqueteCreateViewAdmin(  PaqueteBaseView, CreateView):
    model = Paquete
    form_class = PaqueteForm
    template_name = 'paquete/paquete_form.html'
    success_url = reverse_lazy('gestion:lista_paquetes')
    
    def form_valid(self, form):
        messages.success(self.request, 'Paquete creado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo paquete'
        context['accion'] = 'Crear'
        context['juzgados'] = Juzgado.objects.filter(estatus=1)
        return context

class PaqueteUpdateView(  PaqueteBaseView, UpdateView):
    model = Paquete
    form_class = PaqueteForm
    template_name = 'paquete/paquete_form.html'
    success_url = reverse_lazy('gestion:lista_paquetes')
    
    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        messages.success(self.request, 'Paquete actualizado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar paquete: #{self.object.numero_paquete}'
        context['accion'] = 'Actualizar'
        context['juzgados'] = Juzgado.objects.filter(estatus=1)
        return context

"""
class PaqueteDetailView( PaqueteBaseView, DetailView):
    model = Paquete
    template_name = 'paquete/paquete_detalle.html'
    context_object_name = 'paquete'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paquete = self.object

        # Campos disponibles para filtro: nombre del campo y tipo
        context['filtros_disponibles'] = [
            {'name': 'juez', 'type': 'text'},
            {'name': 'fecha_convenio', 'type': 'date'},
            {'name': 'fecha_inicio', 'type': 'date'},
        ]

        expedientes = paquete.expedientes.all()

        search = self.request.GET.get('search', '')
        fecha_inicio = self.request.GET.get('fecha_inicio', '')
        fecha_fin = self.request.GET.get('fecha_fin', '')

        if search:
            expedientes = expedientes.filter(
                Q(descripcion__icontains=search) |
                Q(expediente_toca__icontains=search)
            )

        if fecha_inicio and fecha_fin:
            expedientes = expedientes.filter(
                fecha_concluido__date__gte=fecha_inicio,
                fecha_concluido__date__lte=fecha_fin
            )

        # Paginación
        page = self.request.GET.get('page', 1)
        per_page = self.request.GET.get('per_page', 10)
        try:
            per_page = int(per_page)
        except (ValueError, TypeError):
            per_page = 10

        paginator = Paginator(expedientes.order_by('-fecha_registro'), per_page)

        try:
            expedientes_page = paginator.page(page)
        except PageNotAnInteger:
            expedientes_page = paginator.page(1)
        except EmptyPage:
            expedientes_page = paginator.page(paginator.num_pages)

        context['expedientes'] = expedientes_page
        context['paginator_range'] = paginator.get_elided_page_range(
            expedientes_page.number,
            on_each_side=2,
            on_ends=1
        )
        context['per_page'] = per_page
        context['per_page_options'] = [1, 10, 15, 20, 30, 50, 100]
        context['search'] = search
        context['fecha_inicio'] = fecha_inicio
        context['fecha_fin'] = fecha_fin

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()  # carga el objeto Paquete
        context = self.get_context_data()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            tabla_html = render_to_string('paquete/_tabla_expedientes.html', context, request=request)
            return JsonResponse({'tabla': tabla_html})

        return self.render_to_response(context)

class PaqueteDetailView( PaqueteBaseView, DetailView):
    model = Paquete
    template_name = 'paquete/paquete_detalle.html'
    context_object_name = 'paquete'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paquete = self.object
        expedientes = paquete.expedientes.all()

        # Paginación
        page = self.request.GET.get('page', 1)
        per_page = self.request.GET.get('per_page', 10)
        try:
            per_page = int(per_page)
        except (ValueError, TypeError):
            per_page = 10

        # Filtros avanzados
        filter_data = self.request.GET.getlist('filters')
        filters = []

        # parse filters[0]=JSON o lista de strings tipo dict
        for raw_filter in filter_data:
            try:
                f = json.loads(raw_filter) if isinstance(raw_filter, str) else raw_filter
                if not all(k in f for k in ['field', 'operator', 'value']):
                    continue
                field = f['field']
                operator = f['operator']
                value = f['value']
                filter_type = f.get('type', 'text')

                if operator == 'range' and filter_type == 'date':
                    date_values = value.split(',')
                    if len(date_values) == 2:
                        start = parse_date(date_values[0])
                        end = parse_date(date_values[1])
                        if start and end:
                            filters.append((f"{field}__range", (start, end)))
                else:
                    filters.append((f"{field}__{operator}", value))
            except Exception:
                continue  # filtro malformado, lo ignoramos

        # Aplicar los filtros dinámicos
        filter_kwargs = {k: v for k, v in filters}
        if filter_kwargs:
            expedientes = expedientes.filter(**filter_kwargs)

        # Paginación
        paginator = Paginator(expedientes.order_by('-fecha_registro'), per_page)

        try:
            expedientes_page = paginator.page(page)
        except PageNotAnInteger:
            expedientes_page = paginator.page(1)
        except EmptyPage:
            expedientes_page = paginator.page(paginator.num_pages)

        context['expedientes'] = expedientes_page
        context['paginator_range'] = paginator.get_elided_page_range(
            expedientes_page.number,
            on_each_side=2,
            on_ends=1
        )
        context['per_page'] = per_page
        context['per_page_options'] = [1, 10, 15, 20, 30, 50, 100]
        context['filters_applied'] = filter_kwargs

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            tabla_html = render_to_string('paquete/_tabla_expedientes.html', context, request=request)
            return JsonResponse({'tabla': tabla_html})
        return self.render_to_response(context) """

class PaqueteDetailView( PaqueteBaseView, DetailView):
    model = Paquete
    template_name = 'paquete/paquete_detalle.html'
    context_object_name = 'paquete'

    def parse_filtros_from_get(self, get_data):
        filtros_dict = defaultdict(dict)
        for key, value in get_data.items():
            if key.startswith('filtros['):
                try:
                    base = key.split('[')[1].split(']')[0]  # índice
                    field = key.split('[')[2].split(']')[0]  # nombre del campo
                    filtros_dict[base][field] = value
                except IndexError:
                    continue
        return list(filtros_dict.values())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paquete = self.object

        context['filtros_disponibles'] = [
            {'name': 'juez', 'type': 'text', 'label': 'Juez'},
            {'name': 'original', 'type': 'bool', 'label': 'Original'},
            {'name': 'fecha_convenio', 'type': 'date', 'label': 'Fecha convenio'},
            {'name': 'fecha_inicio', 'type': 'date', 'label': 'Fecha inicio'},
        ]

        expedientes = paquete.expedientes.all()

        search = self.request.GET.get('search', '')
        fecha_inicio = self.request.GET.get('fecha_inicio', '')
        fecha_fin = self.request.GET.get('fecha_fin', '')
        filtros = parse_filtros_from_get(self.request.GET)
        
        if search:
            expedientes = expedientes.filter(
                Q(descripcion__icontains=search) |
                Q(expediente_toca__icontains=search)
            )

        if fecha_inicio and fecha_fin:
            expedientes = expedientes.filter(
                fecha_concluido__date__gte=fecha_inicio,
                fecha_concluido__date__lte=fecha_fin
            )

        expedientes_page, paginator = filtrar_y_paginar_queryset(expedientes,filtros, self.request)

        context['expedientes'] = expedientes_page
        context['paginator_range'] = paginator.get_elided_page_range(
            expedientes_page.number,
            on_each_side=2,
            on_ends=1
        )
        
        context['per_page'] = self.request.GET.get('per_page', 10)
        context['per_page_options'] = [1, 10, 15, 20, 30, 50, 100]
        context['search'] = search
        context['fecha_inicio'] = fecha_inicio
        context['fecha_fin'] = fecha_fin

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            tabla_html = render_to_string('paquete/_tabla_expedientes.html', context, request=request)
            return JsonResponse({'tabla': tabla_html})
        return self.render_to_response(context)


class PaqueteDeleteView(DeleteView):
    model = Paquete
    template_name = 'paquete/eliminar.html'
    success_url = reverse_lazy('gestion:lista_paquetes')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Paquete eliminado exitosamente')
        return super().delete(request, *args, **kwargs)

# ------------------------------------------------------------------------------------

class SeleccionArchivoRegionalView(TemplateView):
    template_name = 'paquete/seleccion_archivo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['archivos'] = ArchivoRegional.objects.filter(estatus=1)
        return context

class SeleccionJuzgadoView(TemplateView):
    template_name = 'paquete/seleccion_juzgado.html'
    
    def get(self, request, *args, **kwargs):
        archivo_id = kwargs.get('archivo_id')
        
        juzgados_disponibles = Juzgado.objects.filter(
            archivo_regional_id=archivo_id,
            estatus=1
        )
        if not juzgados_disponibles.exists():
            archivo = get_object_or_404(ArchivoRegional, pk=archivo_id)
            messages.warning(
                request,
                f'El archivo "{archivo.nombre}" no tiene juzgados disponibles'
            )
            return redirect(reverse('gestion:seleccion_archivo'))

        request.session['archivo_seleccionado'] = archivo_id
        return super().get(request, *args, **kwargs)
    
class SeleccionOrganoJurisdiccionalView(TemplateView):
    template_name = 'paquete/seleccion_organo_jurisdiccional.html'
    
    def get(self, request, *args, **kwargs):
        archivo_id = kwargs.get('archivo_id')
        
        organos_jurisdiccionales = OrganoJurisdiccional.objects.filter(
            archivo_regional_id=archivo_id,
            estatus=1
        )
        if not organos_jurisdiccionales.exists():
            archivo = get_object_or_404(ArchivoRegional, pk=archivo_id)
            messages.warning(
                request,
                f'El archivo "{archivo.nombre}" no tiene juzgados disponibles'
            )
            return redirect(reverse('gestion:seleccion_archivo'))

        request.session['archivo_seleccionado'] = archivo_id
        return super().get(request, *args, **kwargs)
    

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        archivo_id = self.request.session.get('archivo_seleccionado')
        context['juzgados'] = Juzgado.objects.filter(
            archivo_regional_id=archivo_id,
            estatus=1
        )
        context['materias'] = Materia.objects.filter(estatus=1)
        context['archivo'] = ArchivoRegional.objects.get(pk=archivo_id)
        return context
    
    def post(self, request, *args, **kwargs):
        juzgado_id = request.POST.get('juzgado')
        if juzgado_id:
            request.session['juzgado_seleccionado'] = juzgado_id
            return redirect('gestion:nuevo_paquete')
        return redirect('gestion:seleccion_archivo')
    
@require_GET
def juzgados_por_materia(request):
    materia_id = request.GET.get('materia')
    archivo_id = request.session.get('archivo_seleccionado')

    if not materia_id:
        return JsonResponse({'error': 'El parámetro "materia" es requerido.'}, status=400)

    if not archivo_id:
        return JsonResponse({'error': 'No hay archivo regional seleccionado en la sesión.'}, status=400)

    try:
        archivo_regional = ArchivoRegional.objects.get(pk=archivo_id)
    except ArchivoRegional.DoesNotExist:
        return JsonResponse({'error': 'Archivo regional no encontrado.'}, status=404)

    juzgados = Juzgado.objects.filter(
        materia_id=materia_id,
        archivo_regional=archivo_regional
    ).values('id', 'nombre')

    results = [{'id': j['id'], 'text': j['nombre']} for j in juzgados]

    return JsonResponse({'results': results})

@require_GET
def organojurisdiccional_por_materia(request):
    materia_id = request.GET.get('materia')
    archivo_id = request.session.get('archivo_seleccionado')

    if not materia_id:
        return JsonResponse({'error': 'El parámetro "materia" es requerido.'}, status=400)

    if not archivo_id:
        return JsonResponse({'error': 'No hay archivo regional seleccionado en la sesión.'}, status=400)

    try:
        archivo_regional = ArchivoRegional.objects.get(pk=archivo_id)
    except ArchivoRegional.DoesNotExist:
        return JsonResponse({'error': 'Archivo regional no encontrado.'}, status=404)

    organosjurisdiccionales = OrganoJurisdiccional.objects.filter(
        materia_id=materia_id,
        archivo_regional=archivo_regional
    ).values('id', 'nombre')

    results = [{'id': j['id'], 'text': j['nombre']} for j in organosjurisdiccionales]

    return JsonResponse({'results': results})


# --------------------------------------------------------------------------------------------------------------

class CambiarSeleccionView(TemplateView):
    template_name = 'gestion/paquete/cambiar_seleccion.html'
    
    def get(self, request, *args, **kwargs):
        # Limpiar selección actual
        if 'juzgado_seleccionado' in request.session:
            del request.session['juzgado_seleccionado']
        if 'archivo_seleccionado' in request.session:
            del request.session['archivo_seleccionado']
        return redirect('gestion:seleccion_archivo')

#aquí debe mandar al detalle del paquete para agregar expedientes
class PaqueteCreateView( PaqueteBaseView, CreateView):
    model = Paquete
    form_class = PaqueteForm
    template_name = 'paquete/paquete_form_capturista.html'
    
    def get(self, request, *args, **kwargs):
        if not request.session.get('juzgado_seleccionado'):
            messages.warning(request, 'Primero debe seleccionar un juzgado')
            return redirect('gestion:seleccion_archivo')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        juzgado_id = self.request.session.get('juzgado_seleccionado')
        context['paquetes'] = Paquete.objects.filter(juzgado_id=juzgado_id).order_by('-fecha_registro')[:10]
        return context

    def form_valid(self, form):
        juzgado_id = self.request.session.get('juzgado_seleccionado')
        form.instance.juzgado_id = juzgado_id
        
        # Asignar número consecutivo
        ultimo_paquete = Paquete.objects.filter(
            juzgado_id=juzgado_id
        ).order_by('-numero_paquete').first()
        
        form.instance.numero_paquete = (ultimo_paquete.numero_paquete + 1) if ultimo_paquete else 1
        
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user

        response = super().form_valid(form)
        messages.success(self.request, 'Paquete creado exitosamente')
        return response
    
    def get_success_url(self):
        #return reverse('gestion:ver_paquete')
        return reverse('gestion:ver_paquete', args=[self.object.id])

class PaqueteListView( PaqueteBaseView, ListView):
    model = Paquete
    template_name = 'paquete/lista_paquetes.html'
    context_object_name = 'paquetes'
    paginate_by = 10  # Número de elementos por página
    
    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page', self.paginate_by)
        try:
            return int(per_page)
        except (ValueError, TypeError):
            return self.paginate_by
        
    """def dispatch(self, request, *args, **kwargs):
        if not request.session.get('archivo_seleccionado'):
            messages.warning(request, 'Debe seleccionar un archivo regional')
            return redirect(reverse('gestion:seleccion_archivo'))
        
        if not request.session.get('juzgado_seleccionado'):
            messages.warning(request, 'Debe seleccionar un juzgado')
            return redirect(reverse('gestion:seleccion_juzgado', args=[request.session.get('archivo_seleccionado')]))
        return super().dispatch(request, *args, **kwargs) """

    def get_queryset(self):
        juzgado_id = self.request.session.get('juzgado_seleccionado')
        queryset = Paquete.objects.filter(juzgado_id=juzgado_id)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(clave__icontains=search)|
                Q(numero_paquete=search)
            )
        
        estatus = self.request.GET.get('estatus')
        if estatus:
            queryset = queryset.filter(estatus=estatus)
        
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(
                fecha_registro__date__gte=fecha_inicio,
                fecha_registro__date__lte=fecha_fin
            )
        
        return queryset.order_by('-fecha_registro')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['per_page_options'] = [5,10, 15, 20, 30, 50, 100]
        context['per_page'] = self.get_paginate_by(None)
        context['search'] = self.request.GET.get('search', '')
        context['estatus_selected'] = self.request.GET.get('estatus', '')
        context['fecha_inicio'] = self.request.GET.get('fecha_inicio', '')
        context['fecha_fin'] = self.request.GET.get('fecha_fin', '')
        
        context['estatus_options'] = Paquete.ESTATUS
        
        page_obj = context['page_obj']
        context['paginator_range'] = page_obj.paginator.get_elided_page_range(
            page_obj.number,
            on_each_side=2,
            on_ends=1
        )
        
        return context