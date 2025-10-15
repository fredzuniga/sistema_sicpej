from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Expediente, Paquete
from apps_sicpej.administracion.models import Juzgado, ArchivoRegional, OrganoJurisdiccional
from ..forms_files.expediente_forms import ExpedienteForm
from ..views_files.paquete_views import PaqueteBaseView
from django.db.models import F, Count, Q
from django.core.paginator import Paginator
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
#----
from django.http import HttpResponse
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
from collections import defaultdict
from .tools import filtrar_y_paginar_queryset, parse_filtros_from_get
from django.http import JsonResponse
from django.template.loader import render_to_string

def get_elided_page_range(paginator, number, on_each_side=2, on_ends=1):
    number = int(number)
    if paginator.num_pages <= (on_each_side + on_ends) * 2:
        return paginator.page_range

    result = []

    left_edge = range(1, on_ends + 1)
    left_middle = range(max(number - on_each_side, on_ends + 1), number)
    right_middle = range(number + 1, min(number + on_each_side + 1, paginator.num_pages - on_ends + 1))
    right_edge = range(paginator.num_pages - on_ends + 1, paginator.num_pages + 1)

    last = 0
    for part in [left_edge, left_middle, [number], right_middle, right_edge]:
        for page in part:
            if page - last > 1:
                result.append("...")
            result.append(page)
            last = page
    return result

class CrearExpedienteRedireccionView(PaqueteBaseView, View):
    def get(self, request, *args, **kwargs):
        paquete_id = kwargs.get('paquete_id')
        archivo_regional_seleccionado = request.session.get('archivo_seleccionado')
        organo_jurisdiccional_seleccionado = request.session.get('organo_jurisdiccional_seleccionado')
        user = request.user

        archivo_regional = get_object_or_404(ArchivoRegional, pk=archivo_regional_seleccionado)
        if organo_jurisdiccional_seleccionado:
            organo_jurisdiccional = get_object_or_404(OrganoJurisdiccional, pk=organo_jurisdiccional_seleccionado)
        else:
            paquete = get_object_or_404(Paquete, pk=paquete_id)
            organo_jurisdiccional = paquete.organo_jurisdiccional

        expediente = Expediente.objects.create(
            paquete_id=paquete_id,
            archivo_regional=archivo_regional,
            organo_jurisdiccional=organo_jurisdiccional,
            municipio=organo_jurisdiccional.municipio,
            materia = organo_jurisdiccional.materia,
            instancia = organo_jurisdiccional.instancia,
            distrito_judicial = organo_jurisdiccional.distrito_judicial,
            creado_por=user,
            actualizado_por=user
        )

        return redirect(reverse('gestion:editar_expediente', kwargs={'pk': expediente.pk}))


class ExpedienteCreateView( PaqueteBaseView, CreateView):
    model = Expediente
    form_class = ExpedienteForm
    template_name = 'expediente/expediente_form.html'
    
    def get_success_url(self):
        return reverse_lazy('gestion:ver_paquete', kwargs={'pk': self.kwargs['paquete_id']})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        juzgado_id = self.request.session.get('juzgado_seleccionado')
        
        form.instance.paquete_id = self.kwargs['paquete_id']
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        juzgado = Juzgado.objects.get(pk=juzgado_id)
        form.instance.juzgado = juzgado
        form.instance.municipio = juzgado.municipio
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo expediente'
        context['accion'] = 'Registrar'
        context['paquete'] = Paquete.objects.get(pk=self.kwargs['paquete_id'])
        return context

class ExpedienteUpdateView( PaqueteBaseView, UpdateView):
    model = Expediente
    form_class = ExpedienteForm
    template_name = 'expediente/expediente_form.html'
    
    def get_success_url(self):
        return reverse_lazy('gestion:ver_paquete', kwargs={'pk': self.object.paquete.id})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        form.instance.avocamiento = True
        form.instance.cuadernillo = True
        form.instance.acumulado = True
        id_organo_jurisdiccional= self.request.session.get('organo_jurisdiccional_seleccionado')
        if id_organo_jurisdiccional:
            organo_jurisdiccional = OrganoJurisdiccional.objects.get(pk=id_organo_jurisdiccional)
        else:
            paquete = Paquete.objects.get(pk=self.object.paquete.id)
            organo_jurisdiccional = paquete.organo_jurisdiccional
        form.instance.organo_jurisdiccional = organo_jurisdiccional
        form.instance.instancia = organo_jurisdiccional.instancia
        form.instance.materia = organo_jurisdiccional.materia
        form.instance.distrito_judicial = organo_jurisdiccional.distrito_judicial
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Modificar expediente'
        context['accion'] = 'Finalizar'
        context['paquete'] = Paquete.objects.get(pk=self.object.paquete.id)
        return context

class ExpedienteDetailView(DetailView):
    model = Expediente
    template_name = 'expediente/expediente_detalle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Construye el formulario con los campos deshabilitados
        form = ExpedienteForm(instance=self.object)
        for field in form.fields.values():
            field.disabled = True  # Desactiva el campo
        
        context['form'] = form
        context['titulo'] = 'Detalle del expediente'
        context['paquete'] = Paquete.objects.get(pk=self.object.paquete.id)
        return context

class ExpedienteListView(PaqueteBaseView, ListView):
    model = Expediente
    template_name = 'expediente/lista_expediente.html'
    context_object_name = 'expedientes'

    def get_queryset(self):
        """Construye el queryset inicial para filtrar en get_context_data."""
        organo_id = self.request.GET.get('organo_id')
        if organo_id:
            return Expediente.objects.filter(
                    paquete__organo_jurisdiccional_id=organo_id
                ).order_by('-fecha_registro')
        return Expediente.objects.filter(
            #organo_jurisdiccional_id=self.request.session.get('organo_jurisdiccional_seleccionado')
            archivo_regional_id=self.request.session.get('archivo_seleccionado'),
        ).order_by('-fecha_registro')

    def get_context_data(self, **kwargs):
        """Construye el contexto para la plantilla."""
        context = super().get_context_data(**kwargs)

        context['filtros_disponibles'] = [
            {'name': 'juez', 'type': 'text', 'label': 'Juez'},
            {'name': 'expediente_toca', 'type': 'text', 'label': 'Número de expediente'},
            {'name': 'clave_expediente', 'type': 'text', 'label': 'Clave expediente'},
            {'name': 'original', 'type': 'bool', 'label': 'Original'},
            {'name': 'fecha_creacion', 'type': 'date', 'label': 'Fecha creación'},
            {'name': 'fecha_inicio', 'type': 'date', 'label': 'Fecha inicio'},
        ]

        expedientes = self.get_queryset()
        # Filtros básicos
        search = self.request.GET.get('search', '')
        fecha_inicio = self.request.GET.get('fecha_inicio', '')
        fecha_fin = self.request.GET.get('fecha_fin', '')
        filtros = parse_filtros_from_get(self.request.GET)

        if search:
            expedientes = expedientes.filter(
                Q(descripcion__icontains=search) |
                Q(clave_expediente__icontains=search) |
                 Q(paquete__clave_paquete__icontains=search)
            )
        if fecha_inicio and fecha_fin:
            expedientes = expedientes.filter(
                fecha_registro__date__gte=fecha_inicio,
                fecha_registro__date__lte=fecha_fin
            )

        # Resultado final con la utilidad de paginación
        expedientes_page, paginator = filtrar_y_paginar_queryset(expedientes, filtros, self.request)
        
        context['expedientes'] = expedientes_page
        context['paginator_range'] = get_elided_page_range(
            expedientes_page.paginator,
            expedientes_page.number,
            on_each_side=2,
            on_ends=1
        )
        context['per_page'] = self.request.GET.get('per_page', 10)
        context['per_page_options'] = [5, 10, 15, 20, 30, 50, 100]
        context['search'] = search
        context['fecha_inicio'] = fecha_inicio
        context['fecha_fin'] = fecha_fin

        # Organos para selección
        organo_id = self.request.GET.get('organo_id')
        # Si viene vacio o None, no hacemos filtro
        organo_jurisdiccional = None
        if organo_id and organo_id.isdigit():
            organo_jurisdiccional = OrganoJurisdiccional.objects.filter(pk=organo_id).first()

        archivo_id = self.request.session.get('archivo_seleccionado')
        archivo_actual = None
        organos_disponibles = []
        if archivo_id:
            archivo_actual = ArchivoRegional.objects.filter(pk=archivo_id).first()
            organos_disponibles = OrganoJurisdiccional.objects.filter(archivo_regional_id=archivo_id)

        context['organo_jurisdiccional'] = organo_jurisdiccional
        context['archivo_actual'] = archivo_actual
        context['organos_disponibles'] = organos_disponibles
        context['paquetes_disponibles'] = Paquete.objects.filter(archivo_regional_id=self.request.session.get('archivo_seleccionado'))

        return context

    def get(self, request, *args, **kwargs):
        """Si la solicitud es AJAX, devuelve solo la tabla de expedientes."""
        self.object = None
        self.object_list = self.get_queryset()  # ✅ Ahora asignamos object_list
        context = self.get_context_data()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            tabla_html = render_to_string('expediente/_tabla_expedientes.html', context, request=request)
            if context['organo_jurisdiccional'] is None:
                return JsonResponse({
                    'tabla': tabla_html,
                    'organo_nombre': "",
                    'organo_municipio': "",
                    'archivo_nombre': context['archivo_actual'].nombre,
                })
            else:
                return JsonResponse({
                    'tabla': tabla_html,
                    'organo_nombre': context['organo_jurisdiccional'].nombre,
                    'organo_municipio': context['organo_jurisdiccional'].municipio.descripcion,
                    'archivo_nombre': context['archivo_actual'].nombre,
                })
        return self.render_to_response(context)



