from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import TipoJuzgado
from ..forms_files.tipojuzgado_forms import TipoJuzgadoForm

class TipoJuzgadoListView(ListView):
    model = TipoJuzgado
    template_name = 'tipo_juzgado/lista_tipojuzgado.html'
    context_object_name = 'tipos_juzgado'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        estatus = self.request.GET.get('estatus')
        
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        if estatus:
            queryset = queryset.filter(estatus=estatus)
            
        return queryset.order_by('nombre')

class TipoJuzgadoCreateView(CreateView):
    model = TipoJuzgado
    form_class = TipoJuzgadoForm
    template_name = 'tipo_juzgado/tipojuzgado_form.html'
    success_url = reverse_lazy('administracion:lista_tipos_juzgado')
    
    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        messages.success(self.request, 'Tipo de juzgado creado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nueva materia juzgado'
        context['accion'] = 'Crear'
        return context

class TipoJuzgadoUpdateView(UpdateView):
    model = TipoJuzgado
    form_class = TipoJuzgadoForm
    template_name = 'tipo_juzgado/tipojuzgado_form.html'
    success_url = reverse_lazy('administracion:lista_tipos_juzgado')
    
    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        messages.success(self.request, 'Tipo de juzgado actualizado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Tipo de Juzgado: {self.object.nombre}'
        context['accion'] = 'Actualizar'
        return context

class TipoJuzgadoDetailView(DetailView):
    model = TipoJuzgado
    template_name = 'tipo_juzgado/detalle.html'
    context_object_name = 'tipo_juzgado'

class TipoJuzgadoDeleteView(DeleteView):
    model = TipoJuzgado
    template_name = 'tipo_juzgado/eliminar.html'
    success_url = reverse_lazy('administracion:lista_tipos_juzgado')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tipo de juzgado eliminado exitosamente')
        return super().delete(request, *args, **kwargs)