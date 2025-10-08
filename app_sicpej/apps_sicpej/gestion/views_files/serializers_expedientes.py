# serializers.py
from rest_framework import serializers
from ..models import *

class PaqueteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paquete
        fields = '__all__'

class InstanciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instancia
        fields = '__all__'

class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = '__all__'

class DistritoJudicialSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistritoJudicial
        fields = '__all__'

class TipoJuicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoJuicio
        fields = '__all__'

class MunicipioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipio
        fields = '__all__'

class JuzgadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Juzgado
        fields = '__all__'

class ArchivoRegionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivoRegional
        fields = '__all__'

class OrganoJurisdiccionalSerializer(serializers.ModelSerializer):
    municipio = MunicipioSerializer(read_only=True)  # Para mostrar el detalle
    municipio_id = serializers.PrimaryKeyRelatedField(
        queryset=Municipio.objects.all(), source="municipio", write_only=True
    )  # Para poder asignarlo al crear/editar

    class Meta:
        model = OrganoJurisdiccional
        fields = '__all__'

class CuadernilloSerializer(serializers.ModelSerializer):
    # Este campo permite enviar y guardar el ID
    """organo_jurisdiccional = serializers.PrimaryKeyRelatedField(
        queryset=OrganoJurisdiccional.objects.all()
    )
    # Este campo opcional muestra el detalle completo (solo lectura)
    organo_jurisdiccional_detalle = OrganoJurisdiccionalSerializer(
        source='organo_jurisdiccional', read_only=True
    ) """
    #tipo_cuadernillo = serializers.StringRelatedField()  # o crea serializer si quieres detalle

    class Meta:
        model = Cuadernillo
        fields = '__all__'

class AcumuladoSerializer(serializers.ModelSerializer):
    organo_jurisdiccional = serializers.PrimaryKeyRelatedField(
        queryset=OrganoJurisdiccional.objects.all()
    )
    organo_jurisdiccional_detalle = OrganoJurisdiccionalSerializer(
        source='organo_jurisdiccional', read_only=True
    )

    class Meta:
        model = Acumulado
        fields = '__all__'


class AvocamientoSerializer(serializers.ModelSerializer):
    organo_jurisdiccional = serializers.PrimaryKeyRelatedField(
        queryset=OrganoJurisdiccional.objects.all()
    )
    organo_jurisdiccional_detalle = OrganoJurisdiccionalSerializer(
        source='organo_jurisdiccional', read_only=True
    )

    class Meta:
        model = Avocamiento
        fields = '__all__'


class ExpedienteSerializer(serializers.ModelSerializer):
    paquete = PaqueteSerializer(read_only=True)
    instancia = InstanciaSerializer(read_only=True)
    materia = MateriaSerializer(read_only=True)
    distrito_judicial = DistritoJudicialSerializer(read_only=True)
    tipo_juicio = TipoJuicioSerializer(read_only=True)
    municipio = MunicipioSerializer(read_only=True)  # Para mostrar el detalle
    municipio_id = serializers.PrimaryKeyRelatedField(
        queryset=Municipio.objects.all(), source="municipio", write_only=True
    )  # Para poder asignarlo al crear/editar
    juzgado = JuzgadoSerializer(read_only=True)
    archivo_regional = ArchivoRegionalSerializer(read_only=True)
    organo_jurisdiccional = OrganoJurisdiccionalSerializer(read_only=True)

    cuadernillos = CuadernilloSerializer(many=True, read_only=True)
    acumulados = AcumuladoSerializer(many=True, read_only=True)
    avocamientos = AvocamientoSerializer(many=True, read_only=True)

    estatus_display = serializers.CharField(source='get_estatus_expediente_display', read_only=True)

    class Meta:
        model = Expediente
        fields = '__all__'

