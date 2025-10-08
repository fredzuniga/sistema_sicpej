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
from ..forms_files.perfiles_forms import PerfilForm  # Este formulario debe existir

class PerfilListView(LoginRequiredMixin, ListView):
    model = Perfil
    template_name = 'perfil/lista_perfiles.html'
    context_object_name = 'perfiles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de perfiles'
        return context

class PerfilCreateView(LoginRequiredMixin, CreateView):
    model = Perfil
    form_class = PerfilForm
    template_name = 'perfil/perfil_form.html'
    success_url = reverse_lazy('gestion:lista_perfiles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nuevo perfil'
        context['accion'] = 'Crear'
        return context

    def form_valid(self, form):
        if not form.instance.pk and not form.instance.creado_por:
            form.instance.creado_por = self.request.user
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)

class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    model = Perfil
    form_class = PerfilForm
    template_name = 'perfil/perfil_form.html'
    success_url = reverse_lazy('gestion:lista_perfiles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar perfil: {self.object.nombre}'
        context['accion'] = 'Actualizar'
        return context

    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user
        return super().form_valid(form)