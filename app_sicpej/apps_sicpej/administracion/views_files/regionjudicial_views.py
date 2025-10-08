from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import RegionJudicial
from ..forms_files.regionjudicial_forms import RegionJudicialForm

class RegionJudicialListView(ListView):
    model = RegionJudicial
    template_name = 'region_judicial/lista_regionjudicial.html'
    context_object_name = 'regiones'
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

class RegionJudicialCreateView(CreateView):
    model = RegionJudicial
    form_class = RegionJudicialForm
    template_name = 'region_judicial/regionjudicial_form.html'
    success_url = reverse_lazy('administracion:lista_regiones')
    
    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        messages.success(self.request, 'Región Judicial creado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nueva región judicial'
        context['accion'] = 'Crear'
        return context

class RegionJudicialUpdateView(UpdateView):
    model = RegionJudicial
    form_class = RegionJudicialForm
    template_name = 'region_judicial/regionjudicial_form.html'
    success_url = reverse_lazy('administracion:lista_regiones')
    
    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        messages.success(self.request, 'Región Judicial actualizado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Región judicial: {self.object.nombre}'
        context['accion'] = 'Actualizar'
        return context

class RegionJudicialDetailView(DetailView):
    model = RegionJudicial
    template_name = 'region_judicial/detalle.html'
    context_object_name = 'regionjudicial'