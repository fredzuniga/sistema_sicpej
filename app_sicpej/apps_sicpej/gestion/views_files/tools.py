from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.db import models

from datetime import datetime
from collections import defaultdict

def filtrar_y_paginar_queryset(queryset, filtros, request):
    for f in filtros:
        if f.get('activo', 'true') not in ['true', True, '1', 1]:
            continue

        campo = f.get('campo')
        tipo  = f.get('tipo')
        valor = f.get('valor')
        valor_fin = f.get('valor_fin')
        rango = f.get('rango', False)

        """if not campo or valor in [None, '']:
            continue """
        # 26 - 05 - 2025
        
        if tipo == 'text':
            print("campo --->" , valor)
            print("condición text")
            if valor == '' or valor is None:
                print("vacio")
                queryset = queryset.filter(Q(**{f"{campo}": ''}) | Q(**{f"{campo}__isnull": True}))
            else:
                print("text")
                queryset = queryset.filter(**{f"{campo}__icontains": valor})
                print(f"{campo}__icontains: {valor}")

        elif tipo == 'date':
            fecha_inicio_parsed = parse_date(valor)
            print("fecha_inicio_parsed:", fecha_inicio_parsed)

            # Si es un rango
            if str(rango).lower() == 'true' and valor_fin:
                fecha_fin_parsed = parse_date(valor_fin)
                if fecha_inicio_parsed and fecha_fin_parsed:
                    queryset = queryset.filter(**{f"{campo}__range": (fecha_inicio_parsed, fecha_fin_parsed)})

            # Si es una fecha única
            elif fecha_inicio_parsed:
                # ✅ Identificamos si es DateField o DateTimeField
                field_obj = queryset.model._meta.get_field(campo)

                if isinstance(field_obj, models.DateField) and not isinstance(field_obj, models.DateTimeField):
                    # Campo DateField
                    queryset = queryset.filter(**{campo: fecha_inicio_parsed})
                elif isinstance(field_obj, models.DateTimeField):
                    # Campo DateTimeField
                    queryset = queryset.filter(**{f'{campo}__date': fecha_inicio_parsed})
                else:
                    # Por si acaso otros tipos de campo
                    queryset = queryset.filter(**{campo: fecha_inicio_parsed})

        elif tipo == 'bool':
            bool_value = str(valor).lower() in ['true', '1', 'yes']
            queryset = queryset.filter(**{campo: bool_value})

    # Paginación
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except (ValueError, TypeError):
        per_page = 10

    paginator = Paginator(queryset.order_by('-fecha_registro'), per_page)
    #print("queryset.order_by('-fecha_registro') -->" , queryset.order_by('-fecha_registro'))
    #print("paginator ---> ", paginator)
    try:
        queryset_page = paginator.page(page)
        #print("queryset_page ---> ", queryset_page)
    except PageNotAnInteger:
        queryset_page = paginator.page(1)
        #print(queryset_page)
        #print("PageNotAnInteger ---> ", queryset_page)
    except EmptyPage:
        queryset_page = paginator.page(paginator.num_pages)
        #print("EmptyPage ---> ", queryset_page)

    return queryset_page, paginator


def parse_filtros_from_get(get_data):
        """Parsea los filtros en formato filtros[index][campo]."""
        filtros_dict = defaultdict(dict)
        for key, value in get_data.items():
            if key.startswith('filtros['):
                try:
                    base = key.split('[')[1].split(']')[0]
                    field = key.split('[')[2].split(']')[0]
                    filtros_dict[base][field] = value
                except IndexError:
                    continue
        return list(filtros_dict.values())
