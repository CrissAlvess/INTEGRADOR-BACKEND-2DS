from django.db import models

class Ambiente(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Sensor(models.Model):
    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
    )

    nome = models.CharField(max_length=100)
    mac_address = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.SET_NULL, null=True, blank=True, related_name='sensores')

    def __str__(self):
        return self.nome

class DadoSensor(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='dados')
    ambiente = models.ForeignKey(Ambiente, on_delete=models.SET_NULL, null=True, blank=True)
    temperatura = models.FloatField(null=True, blank=True)
    umidade = models.FloatField(null=True, blank=True)
    luminosidade = models.FloatField(null=True, blank=True)
    contador = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sensor.nome} - {self.timestamp}"
