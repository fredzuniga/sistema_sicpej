from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Cuadernillo, Acumulado, Avocamiento, Paquete, Expediente
from .serializers_expedientes import CuadernilloSerializer, AcumuladoSerializer, AvocamientoSerializer, ExpedienteSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView


# CUADERNILLO
@api_view(['GET'])
def cuadernillos_por_expediente(request, expediente_id):
    cuadernillos = Cuadernillo.objects.filter(expediente_id=expediente_id)
    serializer = CuadernilloSerializer(cuadernillos, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_cuadernillo(request):
    data = request.data.copy()
    data['creado_por'] = request.user.id
    data['actualizado_por'] = request.user.id
    serializer = CuadernilloSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_cuadernillo(request, pk):
    try:
        cuadernillo = Cuadernillo.objects.get(pk=pk)
    except Cuadernillo.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['actualizado_por'] = request.user.id  # Solo se actualiza este campo

    serializer = CuadernilloSerializer(cuadernillo, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_cuadernillo(request, pk):
    try:
        cuadernillo = Cuadernillo.objects.get(pk=pk)
        cuadernillo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Cuadernillo.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

# ACUMULADO

@api_view(['GET'])
def acumulado_por_expediente(request, expediente_id):
    acumulados = Acumulado.objects.filter(expediente_id=expediente_id)
    serializer = AcumuladoSerializer(acumulados, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_acumulado(request):
    data = request.data.copy()
    data['creado_por'] = request.user.id
    data['actualizado_por'] = request.user.id
    serializer = AcumuladoSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_acumulado(request, pk):
    try:
        acumulado = Acumulado.objects.get(pk=pk)
    except Acumulado.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['actualizado_por'] = request.user.id

    serializer = AcumuladoSerializer(acumulado, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_acumulado(request, pk):
    try:
        acumulado = Acumulado.objects.get(pk=pk)
        acumulado.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Acumulado.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
# AVOCAMIENTO

@api_view(['GET'])
def avocamientos_por_expediente(request, expediente_id):
    avocamientos = Avocamiento.objects.filter(expediente_id=expediente_id)
    serializer = AvocamientoSerializer(avocamientos, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_avocamiento(request):
    data = request.data.copy()
    data['creado_por'] = request.user.id
    data['actualizado_por'] = request.user.id
    serializer = AvocamientoSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_avocamiento(request, pk):
    try:
        avocamiento = Avocamiento.objects.get(pk=pk)
    except Avocamiento.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['actualizado_por'] = request.user.id

    serializer = AvocamientoSerializer(avocamiento, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_avocamiento(request, pk):
    try:
        avocamiento = Avocamiento.objects.get(pk=pk)
        avocamiento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Avocamiento.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def cambiar_estatus_paquete(request):
    paquete_id = request.data.get('paquete_id')
    nuevo_estatus = request.data.get('nuevo_estatus', 3)

    if not paquete_id or nuevo_estatus is None:
        return Response(
            {"detail": "Se requiere 'paquete_id' y 'nuevo_estatus'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    paquete = get_object_or_404(Paquete, pk=paquete_id)

    try:
        nuevo_estatus = int(nuevo_estatus)
        if nuevo_estatus not in dict(Paquete.ESTATUS).keys():
            return Response(
                {"detail": f"Estatus inválido: {nuevo_estatus}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    except (ValueError, TypeError):
        return Response(
            {"detail": "El valor de 'nuevo_estatus' debe ser un número entero válido."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Manejo de errores al guardar
    try:
        paquete.estatus = nuevo_estatus
        paquete.fecha_concluido = timezone.now()
        paquete.actualizado_por = request.user
        paquete.save()
    except Exception as e:
        return Response(
            {"detail": "Error interno al actualizar el paquete.", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response({
        "id": paquete.id,
        "estatus": paquete.estatus,
        "estatus_display": paquete.get_estatus_display(),
        "actualizado_por": paquete.actualizado_por.username if paquete.actualizado_por else None
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def validar_expediente_tomo(request):
    expediente_toca = request.data.get('expediente_toca')
    numero_tomo = request.data.get('numero_tomo')
    current_id = request.data.get('id_expediente')  # ID del registro en edición

    # Buscamos un registro con la misma combinación
    registro = Expediente.objects.filter(
        expediente_toca=expediente_toca,
        numero_tomo=numero_tomo
    ).first()

    if registro:
        # Si existe y el ID es diferente al actual → duplicado
        if str(registro.id) != str(current_id):
            return Response({'valid': False})
        # Si el ID es igual → es el mismo registro, permitimos
        else:
            return Response({'valid': True})
    else:
        # No existe ningún registro con esa combinación → válido
        return Response({'valid': True})
    


class ExpedienteDetailAPIView(RetrieveAPIView):
    queryset = Expediente.objects.all()
    serializer_class = ExpedienteSerializer
    lookup_field = 'pk'  # o 'numero' si quieres buscar por número de expediente


class ExpedienteDetailPostAPIView(APIView):
    def post(self, request):
        pk = request.data.get('pk')  # obtenemos el pk del body
        if not pk:
            return Response({"error": "Debe proporcionar el 'pk' del expediente"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            expediente = Expediente.objects.get(pk=pk)
        except Expediente.DoesNotExist:
            return Response({"error": "No se encontró el expediente con el pk proporcionado"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExpedienteSerializer(expediente)
        return Response(serializer.data, status=status.HTTP_200_OK)


