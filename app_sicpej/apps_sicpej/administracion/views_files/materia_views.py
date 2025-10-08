from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from ..models import Materia
from ..forms_files.materia_forms import MateriaForm

class MateriaListView(ListView):
    model = Materia
    template_name = 'materia/lista_materia.html'
    context_object_name = 'materias'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        estatus = self.request.GET.get('estatus')
        
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        if estatus:
            queryset = queryset.filter(estatus=estatus)
            
        return queryset.order_by('nombre')

class MateriaCreateView(CreateView):
    model = Materia
    form_class = MateriaForm
    template_name = 'materia/materia_form.html'
    success_url = reverse_lazy('administracion:lista_materias')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nueva Materia'
        context['accion'] = 'Crear'
        return context
    
    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)

class MateriaUpdateView(UpdateView):
    model = Materia
    form_class = MateriaForm
    template_name = 'materia/materia_form.html'
    success_url = reverse_lazy('administracion:lista_materias')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Materia: {self.object.nombre}'
        context['accion'] = 'Actualizar'
        return context
    
    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)

class MateriaDetailView(DetailView):
    model = Materia
    template_name = 'materia/detalle.html'
    context_object_name = 'materia'