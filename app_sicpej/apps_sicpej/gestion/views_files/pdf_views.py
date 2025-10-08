from django.http import HttpResponse
from reportlab.lib.pagesizes import LETTER, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
from ..models import Expediente, Paquete

import io
import os
from django.conf import settings
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
#from yourapp.models import Expediente  # Ajusta el import a tu app
"""
def generar_pdf_paquete(request, paquete_id):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="paquete_{paquete_id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(LETTER),
                            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []

    styles = getSampleStyleSheet()
    centered_style = ParagraphStyle(name='centered', parent=styles['Normal'], alignment=1)

    # Encabezado centrado
    encabezado = [
        Paragraph("<b>PODER JUDICIAL DEL ESTADO DE TABASCO</b>", centered_style),
        Paragraph("ARCHIVO GENERAL DE CONCENTRACIÓN PERIFERICO", centered_style),
        Spacer(1, 10),
        Paragraph("JUZGADO TERCERO FAMILIAR", styles["Normal"]),
        Paragraph(f"PAQ: {paquete_id}", styles["Normal"]),
        Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%y %I:%M %p')}", styles["Normal"]),
        Spacer(1, 12),
    ]
    elements.extend(encabezado)

    # Datos de la tabla
    data = [["No. EXPEDIENTE", "AÑO", "ACTOR", "DEMANDADO"]]
    expedientes = Expediente.objects.filter(paquete=paquete_id)

    for exp in expedientes:
        data.append([
            str(exp.numero),
            str(exp.fecha_creacion),
            exp.actor[:40],
            exp.demandado[:40],
        ])

    table = Table(data, colWidths=[100, 60, 200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    elements.append(table)
    doc.build(elements)
    return response 

import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from django.http import HttpResponse

def generar_pdf_paquete(request, paquete_id):

    # Crear un buffer de memoria para el PDF
    buffer = io.BytesIO()

    # Configurar el canvas con orientación horizontal
    page_width, page_height = landscape(A4)
    pdf = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    # Márgenes
    margen_izq = 40
    margen_der = 40
    margen_sup = 40

    # Ancho disponible y proporciones de columnas
    ancho_disponible = page_width - margen_izq - margen_der
    ratio_total = 20 + 80 + 20
    ancho_col1 = ancho_disponible * 20 / ratio_total
    ancho_col2 = ancho_disponible * 80 / ratio_total
    ancho_col3 = ancho_disponible * 20 / ratio_total

    # Posición vertical del header
    y_header = page_height - margen_sup
    alto_header = 30  # Altura del encabezado para los bordes

    # Coordenadas X de cada columna
    x_col1 = margen_izq
    x_col2 = x_col1 + ancho_col1
    x_col3 = x_col2 + ancho_col2

    # Contenido del header
    #texto_header = 
    fecha_str = datetime.now().strftime("%d/%m/%Y")

    # Dibujar bordes de las columnas
    pdf.setLineWidth(0.5)
    pdf.rect(x_col1, y_header - alto_header, ancho_col1, alto_header)  # Columna 1
    pdf.rect(x_col2, y_header - alto_header, ancho_col2, alto_header)  # Columna 2
    pdf.rect(x_col3, y_header - alto_header, ancho_col3, alto_header)  # Columna 3

    # Dibujar contenido
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(x_col2 + 150, y_header - 14, "PODER JUDICIAL DEL ESTADO DE TABASCO")

    pdf.drawString(x_col2 + 120, y_header - 25, "ARCHIVO GENERAL DE CONCENTRACIÓN PERIFERICO")

    pdf.setFont("Helvetica", 10)
    fecha_texto = f"Fecha: {fecha_str}"
    ancho_texto = pdf.stringWidth(fecha_texto, "Helvetica", 10)
    x_centrada = x_col3 + (ancho_col3 - ancho_texto) / 2
    pdf.drawString(x_centrada, y_header - 12, fecha_texto)

    # Línea inferior del header (opcional si ya hay bordes)
    # pdf.line(margen_izq, y_header - 20, page_width - margen_der, y_header - 20)

    # Finalizar página y guardar PDF
    pdf.showPage()
    pdf.save()

    # Preparar respuesta HTTP
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf') """

def generar_pdf_paquete(request, paquete_id):
    buffer = io.BytesIO()
    page_width, page_height = landscape(A4)

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(page_width, page_height),
        rightMargin=40, leftMargin=40, topMargin=30, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []
    
    paquete = Paquete.objects.get(pk=paquete_id)

    # Encabezados como tablas
    elements.append(crear_tabla_header("PODER JUDICIAL DEL ESTADO DE TABASCO", mostrar_bordes=False, derecha="fecha", font_size=9))
    elements.append(crear_tabla_header("ARCHIVO GENERAL DE CONCENTRACIÓN PERIFERICO", mostrar_bordes=False, font_size=9))
    nombre_organo = "{}, {}".format(paquete.organo_jurisdiccional.nombre, paquete.organo_jurisdiccional.municipio.descripcion)
    elements.append(crear_tabla_header(nombre_organo, mostrar_bordes=False, font_size=16))
    elements.append(Spacer(1, 25))

    # Tabla principal de expedientes
    encabezados = ["No", "No.Exp","JUICIO", "ACTOR", "DEMANDADO","ORIG", "DUPLI", "CUADE","TOMO","ACUM","OBSERVACIONES"]
    data = [encabezados]

    expedientes = Expediente.objects.filter(paquete=paquete_id)
    for i, exp in enumerate(expedientes, start=1):  # 👈 i será incremental desde 1
        style_pequeno = ParagraphStyle(
            name='Pequeno',
            parent=styles['Normal'],
            fontSize=8,
            leading=10
        )
        data.append([
            str(i),  # 👈 ahora es incremental
            #expediente_toca
            Paragraph(str(exp.expediente_toca) or '', style_pequeno),
            Paragraph(str(exp.juicio_delito) or '', style_pequeno),
            Paragraph(exp.actor or '', style_pequeno),
            Paragraph(exp.demandado or '', style_pequeno),
            Paragraph("x" if exp.original else "", style_pequeno),
            Paragraph("x" if exp.duplicado else "", style_pequeno),
            Paragraph("x" if exp.cuadernillos.exists() else "", style_pequeno),
            Paragraph("x" if not exp.tomo or exp.numero_tomo != 0 else "", style_pequeno),
            Paragraph("x" if exp.acumulados.exists() else "", style_pequeno),
            Paragraph(exp.observaciones or '', style_pequeno),
        ])

    table = Table(data, colWidths=[
        (page_width - 80) * 0.05,
        (page_width - 80) * 0.09,
        (page_width - 80) * 0.16,
        (page_width - 80) * 0.16,
        (page_width - 80) * 0.16,
        (page_width - 80) * 0.045,
        (page_width - 80) * 0.045,
        (page_width - 80) * 0.045,
        (page_width - 80) * 0.045,
        (page_width - 80) * 0.045,
        (page_width - 80) * 0.18,
    ])
    table.setStyle(TableStyle([
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0),  colors.lightgrey),
        ('FONTNAME',   (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('ALIGN',      (0, 0), (-1, 0),  'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'TOP'),
        ('ALIGN',      (0, 1), (1, -1),  'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING',(0, 0), (-1, -1), 4),
        ('FONTSIZE',   (0, 0), (-1, 0), 9),   # Tamaño encabezado
        ('FONTSIZE',   (0, 1), (-1, -1), 8),  # Tamaño contenido
    ]))
    elements.append(table)

    # Funciones de dibujo independientes
    texto_param = "{:^16}".format(f"PAQ: #{paquete.clave_paquete}")
    dibujar_texto = crear_funcion_dibujo(texto_param)
    dibujar_texto_asignado = crear_funcion_dibujo_asignado(paquete)
    #dibujar_logo = crear_funcion_con_imagen("/static/assets_sicpej/img/favicon-32x32.png", x=450, y=730, width=90, height=40)
    ruta_logo = os.path.join(settings.BASE_DIR, 'static/assets_sicpej/img/logo-tsj.jpg')
    print(ruta_logo)
    dibujar_logo = crear_funcion_con_imagen(ruta_logo, x=10, y=495, width=140, height=90)

    # Función que llama a ambas
    def encabezado_completo(canvas, doc):
        dibujar_logo(canvas, doc)
        dibujar_texto(canvas, doc)
        dibujar_texto_asignado(canvas, doc)

    # Construcción del documento con encabezado en todas las páginas
    doc.build(
        elements,
        onFirstPage=encabezado_completo,
        onLaterPages=encabezado_completo
    )

    buffer.seek(0)
    # Guardar en un archivo físico (por ejemplo en /tmp o media/pdf)
    with open(f"/tmp/paquete_{paquete_id}.pdf", "wb") as f:
        f.write(buffer.getvalue())

    # Respuesta al navegador (abrir inline en nueva pestaña si usas target="_blank" en el template)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="paquete_{paquete_id}.pdf"'
    return response


def crear_tabla_header(texto, derecha="", mostrar_bordes=True, font_size=9):
    page_width, _ = landscape(A4)
    fecha_str = (
        f"Fecha reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        if derecha == "fecha" 
        else derecha
    )
    data = [["", texto, fecha_str]]
    table = Table(data, colWidths=[
        (page_width - 80) * 0.2,
        (page_width - 80) * 0.6,
        (page_width - 80) * 0.2
    ])
    estilo = [
        ('VALIGN',  (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',   (1, 0), (1, 0),   'CENTER'),
        ('ALIGN',   (2, 0), (2, 0),   'CENTER'),
        ('FONTNAME',(1, 0), (1, 0),   'Helvetica-Bold'),
        ('FONTSIZE',(1, 0), (1, 0),   font_size),
    ]
    if mostrar_bordes:
        estilo += [
            ('BOX',       (0, 0), (-1, -1), 1,   colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]
    table.setStyle(TableStyle(estilo))
    return table


def crear_funcion_dibujo(texto_a_dibujar):
    def funcion(canvas, doc):
        canvas.setFont("Helvetica-Bold", 22)
        canvas.drawString(640, 522, texto_a_dibujar)
    return funcion

from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.pdfgen import canvas

def crear_funcion_dibujo_asignado(paquete):
    """
    Retorna una función para usar como onPage en ReportLab
    que dibuja en el PDF el nombre de la persona asignada al paquete
    junto con la fecha y hora de asignación.
    """
    # Obtener la asignación de forma segura
    asignacion = paquete.asignaciones_perfiles.first() if callable(getattr(paquete, 'asignacion', None)) else None
    fecha_hora_reporte = paquete.fecha_registro.strftime("%d/%m/%Y %H:%M") if paquete.fecha_registro else ""

    if asignacion and asignacion.usuario_perfil and asignacion.usuario_perfil.perfil:
        nombre_usuario = "{} {}".format(
            asignacion.usuario_perfil.usuario.first_name,
            asignacion.usuario_perfil.usuario.last_name
        )
        fecha_hora_asignacion = asignacion.fecha_asignacion.strftime("%d/%m/%Y %H:%M") if asignacion.fecha_asignacion else ""
        #fecha_hora = "test"
    else:
        nombre_usuario = ""
        fecha_hora_asignacion = ""
        
    def funcion(canvas_obj, doc):
        canvas_obj.setFont("Helvetica", 8)
        # Dibujar el nombre asignado
        canvas_obj.drawString(630, 505, "Fecha registro: {}".format(fecha_hora_reporte))
        if nombre_usuario:
            canvas_obj.drawString(630, 495, "Asignado: {}".format(nombre_usuario))
        if fecha_hora_asignacion:
            canvas_obj.drawString(630, 485, "Fecha asignación: {}".format(fecha_hora_asignacion))

    return funcion



"""
def crear_funcion_dibujo(texto_a_dibujar):
    def funcion(canvas, doc):
        # Definir posición y tamaño del área
        x = 620
        y = 490
        ancho = 160
        alto = 30
        
        # Fondo negro
        canvas.setFillColor(colors.black)
        canvas.rect(x, y, ancho, alto, fill=1, stroke=0)

        # Texto en blanco
        canvas.setFont("Helvetica-Bold", 24)
        canvas.setFillColor(colors.white)
        canvas.drawString(x + 10, y + 5, texto_a_dibujar)

    return funcion """

def crear_funcion_dibujo_test(texto_a_dibujar):
    def funcion(canvas, doc):
        canvas.setFont("Helvetica-Bold", 18)  # Negrita y mayor tamaño
        ancho_pagina = doc.pagesize[0]
        texto_ancho = canvas.stringWidth(texto_a_dibujar, "Helvetica-Bold", 18)
        x_centro = (ancho_pagina - texto_ancho) / 2
        y_posicion = 520  # Puedes ajustar la altura si es necesario
        canvas.drawString(x_centro, y_posicion, texto_a_dibujar)
    return funcion


def crear_funcion_con_imagen(ruta_imagen, x, y, width, height):
    def funcion(canvas, doc):
        try:
            canvas.drawImage(ruta_imagen, x, y, width=width, height=height, preserveAspectRatio=True)
        except Exception as e:
            # Loguear o manejar error según tu configuración
            print(f"No se pudo cargar la imagen: {e}")
    return funcion



