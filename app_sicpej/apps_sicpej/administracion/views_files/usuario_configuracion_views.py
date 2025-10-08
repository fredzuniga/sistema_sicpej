from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse
User = get_user_model()
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

from ..models import UserConfig
from ..forms_files.usuario_forms import UserWithConfigForm

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'usuarios/lista_usuarios.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.prefetch_related('configuracion').all()

class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserWithConfigForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('administracion:lista_usuarios')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        form.save(request_user=self.request.user)
        messages.success(self.request, f"Usuario {self.object.username} creado exitosamente.")
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo usuario'
        context['accion'] = 'Crear'
        return context

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserWithConfigForm
    template_name = 'usuarios/usuario_form.html'
    #success_url = reverse_lazy('administracion:lista_usuarios')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        # Guarda el formulario personalizado
        form.save(request_user=self.request.user)

        # Si el usuario editado es el mismo que el logueado y cambió la contraseña
        if self.object == self.request.user and form.cleaned_data.get('password1'):
            update_session_auth_hash(self.request, self.object)
            messages.info(self.request, "Tu contraseña ha sido cambiada. Se ha actualizado tu sesión.")
        #else:
        #    messages.success(self.request, f"Usuario {self.object.username} actualizado exitosamente.")
        
        # Mensaje general de éxito
        messages.success(self.request, 'Los datos del usuario se han guardado correctamente.')

        # Solo se llama una vez a super()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('administracion:editar_usuario', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Modificar usuario'
        context['accion'] = 'Modificar'
        return context

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'usuarios/usuario_detalle.html'
    context_object_name = 'user_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_config'] = getattr(self.object, 'config', None)
        return context

class UserDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    permission_required = 'auth.delete_user'
    success_url = reverse_lazy('user_list')