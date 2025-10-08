from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, TemplateView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, redirect, render
from django.contrib import messages
from django.urls import reverse
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps_sicpej.administracion.models import *
from ..models import *
from ..forms_files.paquete_forms import PaqueteForm
from django.db.models import F, Count, Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from django.db import transaction
import json
from urllib.parse import urlparse, parse_qs, urlencode
from django.views.decorators.http import require_GET
from collections import defaultdict
from .tools import filtrar_y_paginar_queryset, parse_filtros_from_get
from string import ascii_uppercase
from django.http import JsonResponse, HttpResponseBadRequest
from ..forms_files.usarioperfil_forms import UsuarioPerfilForm  # Este formulario debe existir

class UsuarioPerfilListView(LoginRequiredMixin, ListView):
    model = UsuarioPerfil
    template_name = 'usuario_perfil/lista_usuariosperfiles.html'
    context_object_name = 'usuarios_perfiles'

    def get_queryset(self):
        archivo_regional_usuario = self.request.user.configuracion.archivo_regional
        if archivo_regional_usuario:
            return UsuarioPerfil.objects.filter(archivo_regional=archivo_regional_usuario)
        return UsuarioPerfil.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de asignaciones de usuarios a perfiles'
        return context

class UsuarioPerfilCreateView(LoginRequiredMixin, CreateView):
    model = UsuarioPerfil
    form_class = UsuarioPerfilForm
    template_name = 'usuario_perfil/usuario_perfil_form.html'
    success_url = reverse_lazy('gestion:lista_usuariosperfiles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nueva asignación de perfil a usuario'
        context['accion'] = 'Crear'
        return context

    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)

class UsuarioPerfilUpdateView(LoginRequiredMixin, UpdateView):
    model = UsuarioPerfil
    form_class = UsuarioPerfilForm
    template_name = 'usuario_perfil/usuario_perfil_form.html'
    success_url = reverse_lazy('gestion:lista_usuariosperfiles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar asignación: {self.object.usuario.username} como {self.object.perfil.nombre}'
        context['accion'] = 'Actualizar'
        return context

    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)