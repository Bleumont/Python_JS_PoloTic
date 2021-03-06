from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Pacientes(models.Model):
    nombre = models.CharField(max_length=30)
    dni = models.IntegerField()
    historial = models.TextField(max_length=255, blank=True)

    def __str__(self):
	    return self.nombre

class Profesionales(models.Model):
    nombre = models.CharField(max_length=30, primary_key=True, verbose_name='Nombre')
    dni = models.IntegerField()

    def __str__(self):
        return self.nombre

class Turnos(models.Model):
    profesional = models.ForeignKey(Profesionales, verbose_name='Profesional', on_delete=models.CASCADE)
    paciente = models.ForeignKey(Pacientes, verbose_name='Paciente', on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    asistencia = models.BooleanField(default=False, verbose_name='Asistió al Turno ')

    def __str__(self):
        return f"{self.fecha} {self.profesional}"
    
class Productos(models.Model):
    LENTES = (('LI', 'Lejos Izquierda'),('LD', 'Lejos Derecha'),('CI', 'Cerca Izquierda'),('CD', 'Cerca Derecha'))
    es_lente = models.BooleanField(default=False)
    precio = models.FloatField()
    nombre = models.CharField(max_length=30)
    clasificacion = models.CharField(max_length=2, choices=LENTES, blank=True)
    armazon = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.nombre

class Pedidos(models.Model):
    TIPO_DE_PAGO = (
        ('Tarjeta de credito', 'Tarjeta de credito'),
        ('Tarjeta de debito', 'Tarjeta de debito'),
        ('Billetera virtual', 'Billetera virtual'),
        ('Efectivo', 'Efectivo')
    )
    ESTADO = models.TextChoices('ESTADO', 'Pendiente Pedido Taller Finalizado')
    producto = models.ForeignKey(Productos, verbose_name='Producto', on_delete=models.SET_DEFAULT, default='No disponible')
    cantidad = models.IntegerField()
    fecha_de_compra = models.DateTimeField(auto_now_add=True)
    tipo_pago = models.CharField(max_length=18, choices=TIPO_DE_PAGO)
    estado_pedido = models.CharField(max_length=10, choices=ESTADO.choices, default='Pendiente')
    comprador = models.ForeignKey(Pacientes, verbose_name=('Paciente Comprador'), on_delete=models.SET_DEFAULT, default='Cliente')
    vendedor = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
    def _get_importe(self):
        return self.cantidad*self.producto.precio
    subtotal = property(_get_importe)


    

