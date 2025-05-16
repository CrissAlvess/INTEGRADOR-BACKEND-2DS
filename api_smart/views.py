from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import viewsets, status, filters, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.serializers import ModelSerializer
from django_filters.rest_framework import DjangoFilterBackend
import pandas as pd
from .models import Ambiente, Sensor, DadoSensor
from .serializers import AmbienteSerializer, SensorSerializer, DadoSensorSerializer

class UserSignupSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSignupSerializer

class AmbienteViewSet(viewsets.ModelViewSet):
    queryset = Ambiente.objects.all()
    serializer_class = AmbienteSerializer
    permission_classes = [IsAuthenticated]

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['mac_address', 'nome', 'tipo', 'status']
    search_fields = ['nome', 'mac_address', 'tipo', 'status']
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def importar_planilha_sensores(self, request):
        arquivo_excel = request.FILES.get('file')
        if not arquivo_excel:
            return Response({"detail": "Arquivo não enviado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(arquivo_excel)
        except Exception:
            return Response({"detail": "Erro ao ler o arquivo Excel."}, status=status.HTTP_400_BAD_REQUEST)

        required_columns = {'nome', 'mac_address', 'tipo', 'status'}
        if not required_columns.issubset(df.columns):
            return Response({"detail": f"Colunas obrigatórias ausentes: {required_columns - set(df.columns)}"}, status=status.HTTP_400_BAD_REQUEST)

        sensores_criados = []
        erros = []
        for _, row in df.iterrows():
            try:
                status_val = row['status']
                if status_val not in ['ativo', 'inativo']:
                    raise ValueError(f"Status inválido: {status_val}")

                sensor, created = Sensor.objects.update_or_create(
                    mac_address=row['mac_address'],
                    defaults={
                        'nome': row['nome'],
                        'tipo': row['tipo'],
                        'status': status_val,
                    }
                )
                if created:
                    sensores_criados.append(sensor.nome)
            except Exception as e:
                erros.append(str(e))

        if erros:
            return Response({"detail": "Erros ao importar sensores", "errors": erros}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": f"Sensores importados/atualizados com sucesso: {sensores_criados}"})

class DadoSensorViewSet(viewsets.ModelViewSet):
    queryset = DadoSensor.objects.all()
    serializer_class = DadoSensorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['sensor', 'temperatura', 'luminosidade', 'umidade', 'contador']
    search_fields = ['sensor__nome']
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def importar_planilha(self, request):
        arquivo_excel = request.FILES.get('file')
        if not arquivo_excel:
            return Response({"detail": "Arquivo não enviado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(arquivo_excel)
        except Exception:
            return Response({"detail": "Erro ao ler o arquivo Excel."}, status=status.HTTP_400_BAD_REQUEST)

        required_columns = {'sensor_id', 'temperatura', 'luminosidade', 'umidade', 'contador'}
        if not required_columns.issubset(df.columns):
            return Response({"detail": f"Colunas obrigatórias ausentes: {required_columns - set(df.columns)}"}, status=status.HTTP_400_BAD_REQUEST)

        dados_criados = []
        erros = []
        for _, row in df.iterrows():
            try:
                sensor_id = row['sensor_id']
                sensor = get_object_or_404(Sensor, id=sensor_id)

                dado = DadoSensor.objects.create(
                    sensor=sensor,
                    temperatura=row['temperatura'],
                    luminosidade=row['luminosidade'],
                    umidade=row['umidade'],
                    contador=row['contador']
                )
                dados_criados.append(dado.id)
            except Exception as e:
                erros.append(str(e))

        if erros:
            return Response({"detail": "Erros ao importar dados do sensor", "errors": erros}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": f"Dados importados com sucesso: {dados_criados}"})
