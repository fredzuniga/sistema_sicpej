# views/tipo_cuadernillo_views.py

from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import TipoCuadernillo
from ..forms_files.tipo_cuadernillo_forms import TipoCuadernilloForm

class TipoCuadernilloListView(ListView):
    model = TipoCuadernillo
    template_name = 'tipo_cuadernillo/lista_tipo_cuadernillo.html'
    context_object_name = 'tipos_cuadernillo'
    paginate_by = 10

    def get_queryset(self):
        return TipoCuadernillo.objects.all().order_by('nombre')

class TipoCuadernilloCreateView(CreateView):
    model = TipoCuadernillo
    form_class = TipoCuadernilloForm
    template_name = 'tipo_cuadernillo/tipo_cuadernillo_form.html'
    success_url = reverse_lazy('gestion:lista_tipo_cuadernillos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo tipo de cuadernillo'
        context['accion'] = 'Crear'
        return context

    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)

class TipoCuadernilloUpdateView(UpdateView):
    model = TipoCuadernillo
    form_class = TipoCuadernilloForm
    template_name = 'tipo_cuadernillo/tipo_cuadernillo_form.html'
    success_url = reverse_lazy('gestion:lista_tipo_cuadernillos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar tipo de cuadernillo: {self.object.nombre}'
        context['accion'] = 'Actualizar'
        return context

    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)

class TipoCuadernilloDetailView(DetailView):
    model = TipoCuadernillo
    template_name = 'tipo_cuadernillo/tipo_cuadernillo_detalle.html'
    context_object_name = 'cuadernillo'
