from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db import transaction

from .models import ArchivoRegional, Juzgado, Municipio
from .forms import ArchivoRegionalForm, JuzgadoForm

class ArchivoRegionalListView(ListView):
    model = ArchivoRegional
    template_name = 'archivo_regional/lista_archivos.html'
    context_object_name = 'archivos'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Archivos Regionales'
        return context

class ArchivoRegionalCreateView(View):
    template_name = 'archivo_regional/archivo_form.html'
    success_url = reverse_lazy('administracion:lista_archivos_regional')

    def get(self, request):
        context = {
            'titulo': 'Nuevo archivo regional',
            #'descripcion': f'Registro de nuevo Archivo regional',
            'accion': 'Crear',
            'municipios': Municipio.objects.all()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        nombre = request.POST.get('nombre')
        locacion = request.POST.get('locacion')
        descripcion = request.POST.get('descripcion')
        id_municipio = request.POST.get('id_municipio')
        clave = request.POST.get('clave')
        #archivo.usuario = request.user  # ← Aquí se asigna el usuario autenticado
        nombre_corto = request.POST.get('nombre_corto')
        rgb_color_identificacion = request.POST.get('rgb_color_identificacion')

        errors = {}
        if not nombre:
            errors['nombre'] = 'El nombre es obligatorio.'

        if errors:
            context = {
                'titulo': 'Nuevo archivo regional',
                'accion': 'Crear',
                'errors': errors,
                'nombre': nombre,
                'descripcion': descripcion,
                'locacion': locacion,
                'clave': clave,
                'nombre_corto': nombre_corto,
                'rgb_color_identificacion': rgb_color_identificacion
            }
            return render(request, self.template_name, context)

        try:
            municipio = Municipio.objects.get(pk=id_municipio)
            with transaction.atomic():
                ArchivoRegional.objects.create(
                    nombre=nombre,
                    locacion=locacion,
                    municipio = municipio,
                    descripcion=descripcion,
                    clave=clave,
                    nombre_corto=nombre_corto,
                    rgb_color_identificacion=rgb_color_identificacion,
                    creado_por = self.request.user
                )
        except Exception as e:
            print(f"Error al crear el registro: {e}")
            
            errors['general'] = 'Ocurrió un error al guardar el registro. Intenta nuevamente.'
            context = {
                'titulo': 'Nuevo archivo Regional',
                'accion': 'Crear',
                'errors': errors,
                'nombre': nombre,
                'descripcion': descripcion,
                'locacion': locacion,
                'clave': clave,
                'nombre_corto': nombre_corto,
                'rgb_color_identificacion': rgb_color_identificacion
            }
            return render(request, self.template_name, context)

        return redirect(self.success_url)

class ArchivoRegionalUpdateView(View):
    template_name = 'archivo_regional/archivo_form.html'
    success_url = reverse_lazy('administracion:lista_archivos_regional')

    def get(self, request, pk):
        archivo = get_object_or_404(ArchivoRegional, pk=pk)
        context = {
            'titulo': f'Editar archivo regional: {archivo.nombre}',
            #'descripcion': f'Edición de Archivo regional: {archivo.nombre_corto}',
            'municipios': Municipio.objects.all(),
            'accion': 'Actualizar',
            'archivo': archivo
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        archivo = get_object_or_404(ArchivoRegional, pk=pk)
        municipio = Municipio.objects.get(pk=request.POST.get('id_municipio'))

        archivo.nombre = request.POST.get('nombre')
        archivo.locacion = request.POST.get('locacion')
        archivo.descripcion = request.POST.get('descripcion')
        archivo.municipio = municipio
        archivo.clave = request.POST.get('clave')
        archivo.nombre_corto = request.POST.get('nombre_corto')
        archivo.rgb_color_identificacion = request.POST.get('rgb_color_identificacion')
        archivo.actualizado_por = self.request.user
        archivo.save()

        return redirect(self.success_url)
    

# ---------------------------------------------------------------------------------------------------------


class JuzgadoListView(ListView):
    model = Juzgado
    template_name = 'juzgado/lista_juzgados.html'
    context_object_name = 'juzgados'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de Juzgados'
        return context

class JuzgadoCreateView(CreateView):
    model = Juzgado
    form_class = JuzgadoForm
    template_name = 'juzgado/juzgado_form.html'
    success_url = reverse_lazy('administracion:lista_juzgados')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo juzgado'
        context['accion'] = 'Crear'
        return context

    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)

class JuzgadoUpdateView(UpdateView):
    model = Juzgado
    form_class = JuzgadoForm
    template_name = 'juzgado/juzgado_form.html'
    success_url = reverse_lazy('administracion:lista_juzgados')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Juzgado: {self.object.nombre}, {self.object.municipio.descripcion} '
        context['accion'] = 'Actualizar'
        return context
    
    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)