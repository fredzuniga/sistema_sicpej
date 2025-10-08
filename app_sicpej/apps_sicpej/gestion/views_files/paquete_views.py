from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, redirect, render
from django.contrib import messages
from django.urls import reverse
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps_sicpej.administracion.models import Juzgado, ArchivoRegional, UserConfig, Materia, OrganoJurisdiccional
from ..models import *
from ..forms_files.paquete_forms import PaqueteForm
from django.db.models import F, Count, Q, IntegerField, Func, Value
from django.db.models.functions import Cast
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from django.db import transaction
import json
from urllib.parse import urlparse, parse_qs, urlencode
from django.views.decorators.http import require_GET
from collections import defaultdict
from .tools import filtrar_y_paginar_queryset, parse_filtros_from_get
from string import ascii_uppercase
from django.http import JsonResponse, HttpResponseBadRequest
import re
from apps_sicpej.gestion.utils.bitacora import registrar_bitacora
from django.utils import timezone


class PaqueteBaseView:
    
    seleccion_archivo_url = 'gestion:seleccion_archivo'
    seleccion_organo_jurisdiccional = 'gestion:seleccion_organo_jurisdiccional'

    def dispatch(self, request, *args, **kwargs):
        #is_superuser
        if request.user.configuracion.es_usuario_consulta:
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
            if request.user.configuracion.es_capturista_regional:
                archivo_id = request.user.configuracion.archivo_regional.id
                request.session['archivo_seleccionado'] = archivo_id
                return super().dispatch(request, *args, **kwargs)
                #return redirect(reverse('gestion:lista_paquetes'))
                #passpaquetes/lista

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
                organo_jurisdiccional_id = request.session.get('organo_jurisdiccional_seleccionado')
                if not organo_jurisdiccional_id:
                    # Intentar obtener de la configuración del usuario
                    if request.user.configuracion.organo_jurisdiccional:
                        organo_jurisdiccional = request.user.configuracion.organo_jurisdiccional.id
                        request.session['organo_jurisdiccional_seleccionado'] = organo_jurisdiccional
                    else:
                        messages.warning(request, 'Debe seleccionar un organo jurisdiccional')
                        return redirect(reverse(
                            self.seleccion_organo_jurisdiccional, 
                            args=[request.session.get('archivo_seleccionado')]
                        ))
            else:
                if not request.session.get('organo_jurisdiccional_seleccionado'):
                    messages.warning(request, 'Debe seleccionar un organo jurisdiccional')
                    return redirect(reverse('gestion:seleccion_organo_jurisdiccional', args=[request.session.get('archivo_seleccionado')]))
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener objetos completos para el template
        
        archivo_id = self.request.session.get('archivo_seleccionado')
        organo_jurisdiccional_id = self.request.session.get('organo_jurisdiccional_seleccionado')
        
        if archivo_id is not None and organo_jurisdiccional_id is not None:
            context['archivo_actual'] = ArchivoRegional.objects.get(pk=archivo_id)
            context['organo_jurisdiccional_actual'] = OrganoJurisdiccional.objects.get(pk=organo_jurisdiccional_id)
        else:
            # manejar el caso cuando no existe la variable de sesión
            context['archivo_actual'] = None
            context['organo_jurisdiccional_actual'] = None

        if self.request.user.configuracion.es_capturista_regional:
            context['archivo_actual'] = ArchivoRegional.objects.get(pk=archivo_id)
            context['organo_jurisdiccional_actual'] = None
        
        return context
    
# Se aplica solo para administradores
class PaqueteCreateViewAdmin(PaqueteBaseView, CreateView):
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

class PaqueteUpdateView(PaqueteBaseView, UpdateView):
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

class PaqueteDetailView(PaqueteBaseView, DetailView):
    model = Paquete
    template_name = 'paquete/paquete_detalle.html'
    context_object_name = 'paquete'

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
        context['per_page_options'] = [5, 10, 15, 20, 30, 50, 100]
        context['search'] = search
        context['fecha_inicio'] = fecha_inicio
        context['fecha_fin'] = fecha_fin
        context['paquetes_disponibles'] = Paquete.objects.filter(archivo_regional_id=self.request.session.get('archivo_seleccionado'))

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
    
class SeleccionOrganoJurisdiccionalView( TemplateView):
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
                f'El archivo "{archivo.nombre}" no tiene organos jurisdiccionales disponibles'
            )
            return redirect(reverse('gestion:seleccion_archivo'))

        request.session['archivo_seleccionado'] = archivo_id
        return super().get(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        archivo_id = self.request.session.get('archivo_seleccionado')
        context['organo_jurisdiccional'] = OrganoJurisdiccional.objects.filter(
            archivo_regional_id=archivo_id,
            estatus=1
        )
        context['materias'] = Materia.objects.filter(estatus=1)
        context['archivo']  = ArchivoRegional.objects.get(pk=archivo_id)
        return context
    
    def post(self, request, *args, **kwargs):
        organo_jurisdiccional_id = request.POST.get('organo_jurisdiccional')
        if organo_jurisdiccional_id:
            request.session['organo_jurisdiccional_seleccionado'] = organo_jurisdiccional_id
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

@require_GET
def lista_organos_jurisdiccionales(request):
    organosjurisdiccionales = OrganoJurisdiccional.objects.all().values('id', 'nombre')
    results = [{'id': j['id'], 'text': j['nombre']} for j in organosjurisdiccionales]
    return JsonResponse({'results': results})

@require_GET
def lista_tipos_cuadernillos(request):
    tipos_cuadernillo = TipoCuadernillo.objects.all().values('id', 'nombre')
    results = [{'id': j['id'], 'text': j['nombre']} for j in tipos_cuadernillo]
    return JsonResponse({'results': results})

@require_GET
def nombre_usuario_perfil(request):
    id_usuario_perfil = request.GET.get('id_usuario_perfil')

    if not id_usuario_perfil:
        return HttpResponseBadRequest("Falta el parámetro 'id_usuario_perfil'.")

    try:
        usuario_perfil = UsuarioPerfil.objects.select_related('usuario', 'perfil').get(id=id_usuario_perfil)
        
        nombre_usuario = f"{usuario_perfil.usuario.first_name} {usuario_perfil.usuario.last_name}"
        nombre_perfil = usuario_perfil.perfil.nombre if usuario_perfil.perfil else 'Perfil desconocido'
        
        results = [{
            'id': usuario_perfil.id,
            'text': f'{nombre_usuario} - {nombre_perfil}'
        }]

        return JsonResponse({'results': results})

    except UsuarioPerfil.DoesNotExist:
        return JsonResponse({'results': []}, status=404)
    

@require_GET
def paquetes_mismo_archivo_regional(request):
    try:
        archivo_regional = request.session['archivo_seleccionado']
        paquetes = Paquete.objects.filter(archivo_regional_id=archivo_regional)
        paquetes_data = [
            {
                'id': paquete.id,
                'clave_paquete': paquete.clave_paquete,
                'nombre': paquete.nombre,
                'estatus': paquete.get_estatus_display(),
                'organo_jurisdiccional': paquete.organo_jurisdiccional.nombre if paquete.organo_jurisdiccional else ''
            }
            for paquete in paquetes
        ]

        return JsonResponse({
            'archivo_regional': archivo_regional.nombre,
            'total_paquetes': paquetes.count(),
            'paquetes': paquetes_data
        })

    except UsuarioPerfil.DoesNotExist:
        return JsonResponse({'error': 'UsuarioPerfil no encontrado'}, status=404)


# --------------------------------------------------------------------------------------------------------------
# Ordenar por clave_paquete de forma prorietaria
def sort_clave_paquete(val):
    tiene_c = val.endswith("-C")
    base = val.replace("-C", "")

    m = re.match(r'(\d+)([A-Z]*)', base)
    if m:
        num, suf = m.groups()
        # sufijo en negativo para que sea DESC
        return (tiene_c, -int(num), -ord(suf[0]) if suf else 0)
    return (tiene_c, 0, 0)

class CambiarSeleccionView(TemplateView):
    template_name = 'gestion/paquete/cambiar_seleccion.html'
    
    def get(self, request, *args, **kwargs):
        # Limpiar selección actual
        if 'organo_jurisdiccional_seleccionado' in request.session:
            del request.session['organo_jurisdiccional_seleccionado']
        if 'archivo_seleccionado' in request.session:
            del request.session['archivo_seleccionado']
        return redirect('gestion:seleccion_archivo')

#aquí debe mandar al detalle del paquete para agregar expedientes
class PaqueteCreateView(PaqueteBaseView, CreateView):
    model = Paquete
    form_class = PaqueteForm
    template_name = 'paquete/paquete_form_capturista.html'
    
    def get(self, request, *args, **kwargs):
        
        if not request.session.get('organo_jurisdiccional_seleccionado'):
            messages.warning(request, 'Primero debe seleccionar un organo jurisdiccional')
            return redirect('gestion:seleccion_archivo')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organo_jurisdiccional_seleccionado_id = self.request.session.get('organo_jurisdiccional_seleccionado')
        context['paquetes'] = Paquete.objects.filter(organo_jurisdiccional=organo_jurisdiccional_seleccionado_id).order_by('-fecha_registro')[:10]
        return context

    def form_valid(self, form):
        organo_jurisdiccional_seleccionado_id = self.request.session.get('organo_jurisdiccional_seleccionado')
        form.instance.organo_jurisdiccional = OrganoJurisdiccional.objects.get(pk=organo_jurisdiccional_seleccionado_id)
        
        # Asignar número consecutivo
        ultimo_paquete = Paquete.objects.filter(
            organo_jurisdiccional_id=organo_jurisdiccional_seleccionado_id
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

class PaqueteCreateMultipleView(PaqueteBaseView, FormView):
    form_class = PaqueteForm
    template_name = 'paquete/paquete_form_capturista.html'

    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        organo_jurisdiccional_seleccionado_id = request.session.get('organo_jurisdiccional_seleccionado')
        if not organo_jurisdiccional_seleccionado_id:
            messages.warning(request, 'Primero debe seleccionar un órgano jurisdiccional')
            return redirect('gestion:seleccion_archivo')

        try:
            cantidad = int(request.POST.get('cantidad_paquetes', 1))
        except ValueError:
            cantidad = 1

        clasificacion = request.POST.get('id_clasificacion_paquete', 'N')

        form = self.get_form()
        if form.is_valid():
            paquetes_creados = []
            datos_formulario = form.cleaned_data

            try:
                with transaction.atomic():
                    for i in range(cantidad):
                        nuevo_paquete = Paquete(
                            **datos_formulario,
                            clasificacion_paquete=clasificacion,
                            organo_jurisdiccional_id=organo_jurisdiccional_seleccionado_id,
                            creado_por=request.user,
                            actualizado_por=request.user,
                        )

                        # Guardamos primero el paquete
                        nuevo_paquete.save()

                        # Solo si se guardó exitosamente, registramos la bitácora
                        registrar_bitacora(
                            instancia=nuevo_paquete,
                            accion="creado",
                            usuario_accion=request.user,
                            valores_anteriores= {},
                            descripcion= f"Se creó el paquete {nuevo_paquete.clave_paquete}"
                        )

                        paquetes_creados.append(nuevo_paquete)

            except Exception as e:
                messages.error(request, f'Error al crear paquetes: {e}')
                return redirect('gestion:lista_paquetes')

            # Mensajes de éxito según tipo de usuario
            if usuario.configuracion.es_capturista_regional:
                mensaje = f'<p>{cantidad} paquete(s) creado(s) exitosamente.</p>'
                items = ''
                for p in paquetes_creados:
                    url = reverse('gestion:ver_paquete', args=[p.id])
                    items += f'<li><a href="{url}" target="_blank">Paquete #{p.clave_paquete}</a></li>'
                mensaje += f'<ul>{items}</ul>'
                messages.success(request, mensaje)
                return redirect('gestion:ver_paquete', paquetes_creados[0].id)
            else:
                return redirect('gestion:lista_paquetes')

        return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organo_jurisdiccional_seleccionado_id = self.request.session.get('organo_jurisdiccional_seleccionado')
        context['paquetes'] = Paquete.objects.filter(organo_jurisdiccional=organo_jurisdiccional_seleccionado_id).order_by('-fecha_registro')[:10]
        return context
    
class CrearExtensionPaqueteAutoView(TemplateView):
    def get(self, request, paquete_id):
        paquete_padre = get_object_or_404(Paquete, id=paquete_id)
        paquete_padre.ultimo = False
        paquete_padre.save()

        # Si es extensión de una extensión, retroceder al paquete original
        if paquete_padre.tipo_paquete == 2:
            paquete_padre = paquete_padre.paquete_padre

        # Obtener todas las letras usadas para ese número de paquete y órgano
        extensiones = Paquete.objects.filter(
            paquete_padre=paquete_padre,
            organo_jurisdiccional=paquete_padre.organo_jurisdiccional
        ).exclude(letra__isnull=True).order_by('letra')

        letras_usadas = [p.letra.upper() for p in extensiones if p.letra]
        letras_disponibles = ascii_uppercase[1:]  # omite 'A', que es la del original
        siguiente_letra = next((l for l in letras_disponibles if l not in letras_usadas), None)

        if not siguiente_letra:
            messages.error(request, 'No hay más letras disponibles para este número de paquete.')
            return redirect('gestion:ver_paquete', paquete_id)

        # Sufijo por clasificación (solo si no es NORMAL)
        clasificacion = paquete_padre.clasificacion_paquete
        sufijo = f"-{clasificacion}" if clasificacion != 'N' else ''

        clave_paquete = f"{paquete_padre.numero_paquete_letra}{siguiente_letra}{sufijo}"

        nuevo_paquete = Paquete.objects.create(
            letra=siguiente_letra,
            numero_paquete_letra=paquete_padre.numero_paquete_letra,
            clave_paquete=clave_paquete,
            tipo_paquete=2,
            juzgado=paquete_padre.juzgado,
            organo_jurisdiccional=paquete_padre.organo_jurisdiccional,
            archivo_regional=paquete_padre.organo_jurisdiccional.archivo_regional,
            paquete_padre=paquete_padre,
            clasificacion_paquete=clasificacion,
            creado_por=request.user,
            actualizado_por=request.user,
            ultimo=True
        )

        registrar_bitacora(
            instancia=nuevo_paquete,
            accion="creado",
            usuario_accion=request.user,
            valores_anteriores= {}
        )

        messages.success(request, f'Se ha creado la extensión {nuevo_paquete.clave_paquete}')
        return redirect('gestion:ver_paquete', nuevo_paquete.id)



class PaqueteListView(LoginRequiredMixin, PaqueteBaseView, ListView):
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
        usuario = self.request.user
        ##organo_jurisdiccional = self.request.session.get('organo_jurisdiccional_seleccionado')
        ##queryset = Paquete.objects.filter(organo_jurisdiccional_id=organo_jurisdiccional)
        organo_jurisdiccional = self.request.GET.get('organo_id') or self.request.POST.get('organo_id')

        if not organo_jurisdiccional:
            organo_jurisdiccional = self.request.session.get('organo_jurisdiccional_seleccionado')

        if organo_jurisdiccional:
            if usuario.configuracion.es_capturista_regional:
                #queryset = Paquete.objects.filter(organo_jurisdiccional_id=organo_jurisdiccional)
                queryset = Paquete.objects.filter(
                    estatus = 2,
                    #organo_jurisdiccional_id=organo_jurisdiccional,
                    asignaciones_perfiles__usuario_perfil__usuario=usuario,
                    paquete_padre=None
                ).distinct()
            else:
                queryset = Paquete.objects.filter(organo_jurisdiccional_id=organo_jurisdiccional,paquete_padre=None)
        else:
            queryset = Paquete.objects.all()

        if usuario.configuracion.es_capturista_regional:
            #queryset = Paquete.objects.filter(organo_jurisdiccional_id=organo_jurisdiccional)
            queryset = Paquete.objects.filter(
                estatus = 2,
                #organo_jurisdiccional_id=organo_jurisdiccional,
                asignaciones_perfiles__usuario_perfil__usuario=usuario,
                paquete_padre=None
            ).distinct()
        
        search = self.request.GET.get('search')
        if search:
            if organo_jurisdiccional:
                if usuario.configuracion.es_capturista_regional:
                   queryset = Paquete.objects.filter(
                        estatus = 2,
                        asignaciones_perfiles__usuario_perfil__usuario=usuario
                    ).distinct()
                else:
                    queryset = Paquete.objects.filter(organo_jurisdiccional_id=organo_jurisdiccional)

            if usuario.configuracion.es_capturista_regional:
                queryset = Paquete.objects.filter(
                    estatus = 2,
                    asignaciones_perfiles__usuario_perfil__usuario=usuario,
                ).distinct()

            filters = (
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(clave_paquete__icontains=search)
            )

            # Si es número entero, añadimos filtro por numero_paquete
            try:
                filters |= Q(numero_paquete=int(search))
            except ValueError:
                pass

            queryset = queryset.filter(filters)
        
        estatus = self.request.GET.get('estatus')
        if estatus:
            queryset = queryset.filter(estatus=estatus)
        
        clasificacion_paquete = self.request.GET.get('clasificacion_paquete', '')
        if clasificacion_paquete:
            queryset = queryset.filter(clasificacion_paquete=clasificacion_paquete)

        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(
                fecha_registro__date__gte=fecha_inicio,
                fecha_registro__date__lte=fecha_fin
            )
        
        qs = list(queryset)
        qs.sort(key=lambda x: sort_clave_paquete(x.clave_paquete))
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['per_page_options'] = [5,10, 15, 20, 30, 50, 100]
        context['per_page'] = self.get_paginate_by(None)
        context['search'] = self.request.GET.get('search', '')
        context['clasificacion_paquete'] = self.request.GET.get('clasificacion_paquete', '')
        context['estatus_selected'] = self.request.GET.get('estatus', '')
        context['fecha_inicio'] = self.request.GET.get('fecha_inicio', '')
        context['fecha_fin'] = self.request.GET.get('fecha_fin', '')
        context['usuarios_capturistas'] = UsuarioPerfil.objects.filter(perfil__tipo_perfil=1, archivo_regional_id= self.request.session.get('archivo_seleccionado'))
        
        context['estatus_options'] = Paquete.ESTATUS
        
        page_obj = context['page_obj']
        context['paginator_range'] = page_obj.paginator.get_elided_page_range(
            page_obj.number,
            on_each_side=2,
            on_ends=1
        )

        organo_id = self.request.GET.get('organo_id')
        # Si viene vacio o None, no hacemos filtro
        organo_jurisdiccional = None
        if organo_id and organo_id.isdigit():
            organo_jurisdiccional = OrganoJurisdiccional.objects.filter(pk=organo_id).first()

        archivo_id = self.request.session.get('archivo_seleccionado')
        organos_disponibles = []
        if archivo_id:
            #archivo_actual = ArchivoRegional.objects.filter(pk=archivo_id).first()
            organos_disponibles = OrganoJurisdiccional.objects.filter(archivo_regional_id=archivo_id)
        context['organos_disponibles'] = organos_disponibles
        context['organo_jurisdiccional'] = organo_jurisdiccional
        
        return context
    
"""class AsignarPaquetePerfilView(PaqueteBaseView, View):
    def post(self, request, *args, **kwargs):
        expedientes = request.POST.getlist('expediente')
        id_usuario_perfil = request.POST.get('id_usuario_perfil')

        if not id_usuario_perfil:
            messages.error(request, "Falta el ID del perfil de usuario.")
            return redirect(reverse('gestion:lista_paquetes'))

        try:
            usuario_perfil = UsuarioPerfil.objects.get(pk=id_usuario_perfil)
        except UsuarioPerfil.DoesNotExist:
            messages.error(request, "El perfil de usuario no existe.")
            return redirect(reverse('gestion:lista_paquetes'))

        paquetes = Paquete.objects.filter(id__in=expedientes)
        usuario = request.user
        paquetes_asignados_ids = []
        duplicados = []

        with transaction.atomic():
            for paquete in paquetes:
                existe = AsignacionPaquetePerfil.objects.filter(
                    paquete=paquete,
                    usuario_perfil=usuario_perfil
                ).exists()

                if not existe:
                    try:
                        asignacion = AsignacionPaquetePerfil.objects.create(
                            paquete=paquete,
                            usuario_perfil=usuario_perfil,
                            estatus=1, tipo_asignacion='M', prioridad=1,
                            asignado_por=usuario, actualizado_por=usuario
                        )

                        if not HistorialAsignacionPaquete.objects.filter( paquete=paquete, perfil=usuario_perfil.perfil, usuario_asignado=usuario_perfil.usuario, tipo_accion='A' ).exists():
                            HistorialAsignacionPaquete.objects.create(
                                paquete=paquete, perfil=usuario_perfil.perfil, usuario_asignado=usuario_perfil.usuario,
                                tipo_accion='A', estado_anterior='Sin asignar', estado_nuevo='Asignado',
                                observaciones='Asignación inicial del paquete.', asignado_por=usuario,  actualizado_por=usuario,
                            )

                        if asignacion.pk:
                            paquetes_asignados_ids.append(str(paquete.id))
                            if paquete.estatus != 2:
                                paquete.estatus = 2
                                paquete.save()
                    except Exception as e:
                        print(f"Error al asignar el paquete {paquete.id}: {e}")
                        raise  # Esto asegura que se deshaga toda la transacción en caso de error
                else:
                    duplicados.append(str(paquete.id))

        if paquetes_asignados_ids:
            messages.success(request, f"{len(paquetes_asignados_ids)} paquete(s) asignado(s) correctamente.")
        if duplicados:
            messages.warning(request, f"{len(duplicados)} paquete(s) ya estaban asignados y fueron omitidos.")

        # Obtener filtros originales desde el referer
        referer_url = request.META.get('HTTP_REFERER', '')
        parsed_url = urlparse(referer_url)
        query_params = parse_qs(parsed_url.query)

        if paquetes_asignados_ids:
            query_params['expediente'] = paquetes_asignados_ids

        query_string = urlencode(query_params, doseq=True)

        # Construir URL con reverse
        base_url = reverse('gestion:lista_paquetes')
        redirect_url = f"{base_url}?{query_string}" if query_string else base_url

        return redirect(redirect_url)
"""

class AsignarPaquetePerfilView(PaqueteBaseView, View):
    def post(self, request, *args, **kwargs):
        expedientes = request.POST.getlist('expediente')
        id_usuario_perfil = request.POST.get('id_usuario_perfil')

        if not id_usuario_perfil:
            messages.error(request, "Falta el ID del perfil de usuario.")
            return redirect(reverse('gestion:lista_paquetes'))

        try:
            usuario_perfil = UsuarioPerfil.objects.get(pk=id_usuario_perfil)
        except UsuarioPerfil.DoesNotExist:
            messages.error(request, "El perfil de usuario no existe.")
            return redirect(reverse('gestion:lista_paquetes'))

        paquetes = Paquete.objects.filter(id__in=expedientes)
        usuario = request.user
        paquetes_asignados_ids = []
        reasignados = []

        with transaction.atomic():
            for paquete in paquetes:
                asignacion_existente = AsignacionPaquetePerfil.objects.filter(paquete=paquete).first()

                if asignacion_existente:
                    # Ya existe asignación previa → verificar si es el mismo usuario_perfil
                    if asignacion_existente.usuario_perfil == usuario_perfil:
                        continue  # Ya está asignado a este perfil

                    # Registrar en historial la reasignación
                    HistorialAsignacionPaquete.objects.create(
                        paquete=paquete,
                        perfil=asignacion_existente.usuario_perfil.perfil,
                        usuario_asignado=asignacion_existente.usuario_perfil.usuario,
                        tipo_accion='R',
                        estado_anterior=f"Asignado a {asignacion_existente.usuario_perfil.usuario}",
                        estado_nuevo=f"Reasignado a {usuario_perfil.usuario}",
                        observaciones=f"Reasignado del perfil {asignacion_existente.usuario_perfil.perfil} al perfil {usuario_perfil.perfil}.",
                        asignado_por=usuario,
                        actualizado_por=usuario,
                    )

                    # Actualizar la asignación con el nuevo perfil
                    asignacion_existente.usuario_perfil = usuario_perfil
                    asignacion_existente.actualizado_por = usuario
                    asignacion_existente.fecha_actualizacion = timezone.now()
                    asignacion_existente.save()

                    reasignados.append(str(paquete.id))

                else:
                    # Crear una nueva asignación si no existe
                    AsignacionPaquetePerfil.objects.create(
                        paquete=paquete,
                        usuario_perfil=usuario_perfil,
                        estatus=1,
                        tipo_asignacion='M',
                        prioridad=1,
                        asignado_por=usuario,
                        actualizado_por=usuario
                    )

                    # Registrar en historial la nueva asignación
                    HistorialAsignacionPaquete.objects.create(
                        paquete=paquete,
                        perfil=usuario_perfil.perfil,
                        usuario_asignado=usuario_perfil.usuario,
                        tipo_accion='A',
                        estado_anterior='Sin asignar',
                        estado_nuevo='Asignado',
                        observaciones='Asignación inicial del paquete.',
                        asignado_por=usuario,
                        actualizado_por=usuario,
                    )

                # Asegurar que el paquete tenga estatus de asignado
                if paquete.estatus != 2:
                    paquete.estatus = 2
                    paquete.save()

                paquetes_asignados_ids.append(str(paquete.id))

        # --- Mensajes combinados ---
        mensajes = []
        if paquetes_asignados_ids:
            mensajes.append(f"{len(paquetes_asignados_ids)} paquete(s) asignado(s) correctamente.")
        if reasignados:
            mensajes.append(f"{len(reasignados)} paquete(s) fueron reasignados a otro perfil.")

        if mensajes:
            messages.success(request, " ".join(mensajes))

        # --- Mantener filtros del referer ---
        referer_url = request.META.get('HTTP_REFERER', '')
        parsed_url = urlparse(referer_url)
        query_params = parse_qs(parsed_url.query)

        if paquetes_asignados_ids:
            query_params['expediente'] = paquetes_asignados_ids

        query_string = urlencode(query_params, doseq=True)
        base_url = reverse('gestion:lista_paquetes')
        redirect_url = f"{base_url}?{query_string}" if query_string else base_url

        return redirect(redirect_url)


class MoverExpedientesAPaqueteView(View):
    def post(self, request, *args, **kwargs):
        expediente_ids = request.POST.getlist('expediente')
        paquete_destino_id = request.POST.get('paquete_destino_id')
        id_vista_redirect = int(request.POST.get('id_vista_redirect', 0))
        print("id_vista_redirect--->",id_vista_redirect)

        if not expediente_ids:
            messages.error(request, "Debe seleccionar al menos un expediente.")
            return redirect(reverse('gestion:lista_paquetes'))

        if not paquete_destino_id:
            messages.error(request, "Debe seleccionar un paquete de destino.")
            return redirect(reverse('gestion:lista_paquetes'))

        try:
            paquete_destino = Paquete.objects.get(id=paquete_destino_id)
        except Paquete.DoesNotExist:
            messages.error(request, "El paquete de destino no existe.")
            return redirect(reverse('gestion:lista_paquetes'))

        expedientes_movidos = 0

        with transaction.atomic():
            for expediente_id in expediente_ids:
                try:
                    expediente = Expediente.objects.get(id=expediente_id)
                    expediente.paquete = paquete_destino
                    expediente.organo_jurisdiccional = paquete_destino.organo_jurisdiccional
                    expediente.archivo_regional = paquete_destino.archivo_regional
                    expediente.save()
                    expedientes_movidos += 1
                except Expediente.DoesNotExist:
                    continue  # Opcional: loguear si un ID no existe

        messages.success(request, f"{expedientes_movidos} expediente(s) movido(s) al paquete #{paquete_destino.clave_paquete}.")

        if id_vista_redirect == 2:
            id_paquete = request.POST.get('id_paquete')
            return redirect('gestion:ver_paquete', id_paquete)
        
        return redirect(reverse('gestion:lista_expedientes'))
    

class PaquetesAsignadosUsuarioView(LoginRequiredMixin, ListView):
    model = AsignacionPaquetePerfil
    template_name = 'paquete/lista_paquetes_asignados_usuario.html'
    context_object_name = 'asignaciones'
    paginate_by = 10

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page', self.paginate_by)
        try:
            return int(per_page)
        except (ValueError, TypeError):
            return self.paginate_by

    def get_queryset(self):
        usuario = self.request.user
        perfiles_activos = UsuarioPerfil.objects.filter(usuario=usuario, estatus=1)

        queryset = AsignacionPaquetePerfil.objects.filter(
            usuario_perfil__in=perfiles_activos
        ).select_related('paquete', 'usuario_perfil__perfil')

        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(paquete__nombre__icontains=search) |
                Q(paquete__descripcion__icontains=search) |
                Q(paquete__clave_paquete__icontains=search) |
                Q(paquete__numero_paquete__icontains=search)
            )

        # Filtro por estatus
        estatus = self.request.GET.get('estatus')
        if estatus:
            queryset = queryset.filter(estatus=estatus)

        # Filtro por fecha límite
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(
                paquete__fecha_registro__date__gte=fecha_inicio,
                paquete__fecha_registro__date__lte=fecha_fin
            )

        return queryset.order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Mis paquetes asignados'
        context['per_page_options'] = [5, 10, 15, 20, 30, 50, 100]
        context['per_page'] = self.get_paginate_by(None)
        context['search'] = self.request.GET.get('search', '')
        context['estatus_selected'] = self.request.GET.get('estatus', '')
        context['fecha_inicio'] = self.request.GET.get('fecha_inicio', '')
        context['fecha_fin'] = self.request.GET.get('fecha_fin', '')
        context['estatus_options'] = AsignacionPaquetePerfil.ESTATUS

        page_obj = context['page_obj']
        context['paginator_range'] = page_obj.paginator.get_elided_page_range(
            page_obj.number,
            on_each_side=2,
            on_ends=1
        )

        return context
            
