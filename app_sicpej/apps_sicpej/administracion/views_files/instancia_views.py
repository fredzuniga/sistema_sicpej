from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from ..models import Instancia
from ..forms_files.instancia_forms import InstanciaForm

class InstanciaListView(ListView):
    model = Instancia
    template_name = 'instancia/lista_instancia.html'
    context_object_name = 'instancias'
    paginate_by = 10
    
    def get_queryset(self):
        return Instancia.objects.all().order_by('nombre')

class InstanciaCreateView(CreateView):
    model = Instancia
    form_class = InstanciaForm
    template_name = 'instancia/instancia_form.html'
    success_url = reverse_lazy('administracion:lista_instancias')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nueva instancia'
        context['accion'] = 'Crear'
        return context

    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)

class InstanciaUpdateView(UpdateView):
    model = Instancia
    form_class = InstanciaForm
    template_name = 'instancia/instancia_form.html'
    success_url = reverse_lazy('administracion:lista_instancias')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Instancia: {self.object.nombre}'
        context['accion'] = 'Actualizar'
        return context

    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)

class InstanciaDetailView(DetailView):
    model = Instancia
    template_name = 'instancia/instancia_detalle.html'
    context_object_name = 'instancia'