from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    sexo = models.CharField(max_length=10, blank=True, null=True)
    fecha_nacimiento = models.DateTimeField(blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    notas_adicionales = models.TextField(blank=True, null=True)
    comentarios = models.TextField(blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    email=models.EmailField(primary_key=True, max_length=254)

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class CodigosPromocionales(models.Model):
    codigo = models.CharField(primary_key=True, max_length=50)
    descuento = models.IntegerField()

    class Meta:
        db_table = 'codigos_promocionales'
        verbose_name = 'Código Promocional'
        verbose_name_plural = 'Códigos Promocionales'

    def __str__(self):
        return f'{self.codigo} - {self.descuento}%'


class HorarioDisponible(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    disponible = models.BooleanField(default=True)

    class Meta:
        db_table = 'horarios_disponibles'
        unique_together = ('fecha', 'hora')
        verbose_name = 'Horario Disponible'
        verbose_name_plural = 'Horarios Disponibles'

    def __str__(self):
        return f'{self.fecha} {self.hora} {"Disponible" if self.disponible else "No Disponible"}'


class Servicio(models.Model):
    id_servicios = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_servicio = models.CharField(max_length=255)
    precio_UYU = models.CharField(null=True, blank=True)
    precio_USD = models.CharField(null=True, blank=True)
    precio_EUR = models.CharField(null=True, blank=True)
    duracion = models.IntegerField()
    descripcion = models.TextField()

    def __str__(self):
        return f'{self.nombre_servicio} - {self.descripcion}'

    class Meta:
        db_table = 'servicios'
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'



class Especialista(models.Model):
    id_especialista = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    cedula = models.CharField(max_length=255)
    especialidad = models.CharField(max_length=255, null=True, blank=True)
    sexo = models.CharField(max_length=2)
    fecha_nacimiento = models.DateField()
    edad = models.IntegerField(null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(max_length=255)
    foto_url = models.URLField(max_length=500, blank=True, null=True)
    descripcion = models.TextField()
    
    def edad(self):
        if self.fecha_nacimiento:
            return date.today().year - self.fecha_nacimiento.year
        return None

    class Meta:
        db_table = 'especialistas'
        verbose_name = 'Especialista'
        verbose_name_plural = 'Especialistas'

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"


class Cita(models.Model):
    id_citas = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paciente_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, db_column='paciente_id')  # db_column añadido para asegurar que coincide con la tabla
    fecha = models.DateField()
    hora = models.TimeField()
    servicio = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notas_adicionales = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'citas'
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'

    def __str__(self):
        return f'{self.paciente_id} - {self.fecha} {self.hora}'
