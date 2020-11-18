from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Pacientes(models.Model):
    nombre = models.CharField(max_length=30)
    dni = models.IntegerField(primary_key=True)
    historial = models.TextField(max_length=255)

class Profesionales(models.Model):
    nombre = models.CharField(max_length=30)
    dni = models.IntegerField(primary_key=True)

class Turnos(models.Model):
    profesional = models.ForeignKey(Profesionales, verbose_name='Profesional', on_delete=models.CASCADE)
    dni = models.IntegerField(default=12345678, verbose_name='DNI del Paciente')
    fecha = models.DateTimeField()
    asistencia = models.BooleanField(default=False, verbose_name='Asistió al Turno')
    
class Productos(models.Model):
    LENTES = (('LI', 'Lejos Izquierda'),('LD', 'Lejos Derecha'),('CI', 'Cerca Izquierda'),('CD', 'Cerca Derecha'))
    clasificacion = models.CharField(max_length=2, choices=LENTES)
    nombre = models.CharField(max_length=30)
    precio = models.FloatField()
    armazon = models.BooleanField(default=False)

class Pedidos(models.Model):
    TIPO_DE_PAGO = (
        ('TC', 'Tarjeta de credito'),
        ('TD', 'Tarjeta de debito'),
        ('BV', 'Billetera virtual'),
        ('EF', 'Efectivo')
    )
    ESTADO = models.TextChoices('ESTADO', 'Pendiente Pedido Taller Finalizado')
    producto = models.ForeignKey(Productos, verbose_name='ID del Producto', on_delete=models.SET_DEFAULT, default='No disponible')
    cantidad = models.IntegerField()
    fecha_de_compra = models.DateTimeField(default=timezone.now)
    subtotal = models.FloatField()
    tipo_pago = models.CharField(max_length=2, choices=TIPO_DE_PAGO)
    estado_pedido = models.CharField(max_length=10, choices=ESTADO.choices)
    comprador = models.ForeignKey(Pacientes, verbose_name=('DNI Paciente Comprador'), on_delete=models.SET_DEFAULT, default='Cliente')
    vendedor = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default='Vendedor')