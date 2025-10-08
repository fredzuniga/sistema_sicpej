from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import TipoJuicio
from ..forms_files.tipojuicio_forms import TipoJuicioForm

class TipoJuicioListView(ListView):
    model = TipoJuicio
    template_name = 'tipo_juicio/lista_tiposjuicio.html'
    context_object_name = 'tipos_juicio'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('materia')
        search = self.request.GET.get('search')
        estatus = self.request.GET.get('estatus')
        materia_id = self.request.GET.get('materia')
        
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        if estatus:
            queryset = queryset.filter(estatus=estatus)
        if materia_id:
            queryset = queryset.filter(materia_id=materia_id)
            
        return queryset.order_by('nombre')

class TipoJuicioCreateView(CreateView):
    model = TipoJuicio
    form_class = TipoJuicioForm
    template_name = 'tipo_juicio/tipojuicio_form.html'
    success_url = reverse_lazy('administracion:lista_tipos_juicio')
    
    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        messages.success(self.request, 'Tipo de juicio creado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo juicio'
        context['accion'] = 'Crear'
        return context

class TipoJuicioUpdateView(UpdateView):
    model = TipoJuicio
    form_class = TipoJuicioForm
    template_name = 'tipo_juicio/tipojuicio_form.html'
    success_url = reverse_lazy('administracion:lista_tipos_juicio')
    
    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        messages.success(self.request, 'Tipo de juicio actualizado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Tipo de Juicio: {self.object.nombre}'
        context['accion'] = 'Actualizar'
        return context

class TipoJuicioDetailView(DetailView):
    model = TipoJuicio
    template_name = 'tipo_juicio/detalle.html'
    context_object_name = 'tipo_juicio'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materias_relacionadas'] = self.object.materia.all() if hasattr(self.object, 'materia') else []
        return context