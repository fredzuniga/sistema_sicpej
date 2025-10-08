from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from ..models import OrganoJurisdiccional
from ..forms_files.organojurisdiccional_forms import OrganoJurisdiccionalForm

class OrganoJurisdiccionalListView(ListView):
    model = OrganoJurisdiccional
    template_name = 'organo_jurisdiccional/lista_organojurisdiccionales.html'
    context_object_name = 'organos_juridiccionales'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de organos jurisdiccionales'
        return context

class OrganoJurisdiccionalCreateView(CreateView):
    model = OrganoJurisdiccional
    form_class = OrganoJurisdiccionalForm
    template_name = 'organo_jurisdiccional/organojurisdiccional_form.html'
    success_url = reverse_lazy('administracion:lista_organosjurisdiccionales')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo organo jurisdiccional'
        context['accion'] = 'Crear'
        return context

    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)

class OrganoJurisdiccionalUpdateView(UpdateView):
    model = OrganoJurisdiccional
    form_class = OrganoJurisdiccionalForm
    template_name = 'organo_jurisdiccional/organojurisdiccional_form.html'
    success_url = reverse_lazy('administracion:lista_organosjurisdiccionales')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar organo jurisdiccional: {self.object.nombre}, {self.object.municipio.descripcion} '
        context['accion'] = 'Actualizar'
        return context
    
    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)