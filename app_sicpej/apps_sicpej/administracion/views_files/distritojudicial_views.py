from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
#from .models import DistritoJudicial
#from .forms import DistritoJudicialForm
from ..models import DistritoJudicial
from ..forms_files.distritojudicial_forms import DistritoJudicialForm

class DistritoJudicialListView(ListView):
    model = DistritoJudicial
    template_name = 'distrito_judicial/lista_distritojudicial.html'
    context_object_name = 'distritos'
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

class DistritoJudicialCreateView(CreateView):
    model = DistritoJudicial
    form_class = DistritoJudicialForm
    template_name = 'distrito_judicial/distritojudicial_form.html'
    success_url = reverse_lazy('administracion:lista_distritos')
    
    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        messages.success(self.request, 'Distrito Judicial creado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo distrito judicial'
        context['accion'] = 'Crear'
        return context

class DistritoJudicialUpdateView(UpdateView):
    model = DistritoJudicial
    form_class = DistritoJudicialForm
    template_name = 'distrito_judicial/distritojudicial_form.html'
    success_url = reverse_lazy('administracion:lista_distritos')
    
    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        messages.success(self.request, 'Distrito Judicial actualizado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Distrito Judicial: {self.object.nombre}'
        context['accion'] = 'Actualizar'
        return context

class DistritoJudicialDetailView(DetailView):
    model = DistritoJudicial
    template_name = 'distrito_judicial/detalle.html'
    context_object_name = 'distrito'