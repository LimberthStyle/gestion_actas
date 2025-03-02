from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mail = models.EmailField()
    psw = models.CharField(max_length=50)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

class Conductor(models.Model):
    dni = models.CharField(max_length=8)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    cat_licen = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class Vehiculo(models.Model):
    placa = models.CharField(max_length=10)
    def __str__(self):
        return self.placa

class Infraccion(models.Model):
    fecha_infrac = models.DateTimeField()
    retencion = models.CharField(max_length=50)
    id_driver = models.ForeignKey(Conductor, on_delete=models.CASCADE)
    id_vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Infracción de {self.id_driver} el {self.fecha_infrac}"

class Acta(models.Model):
    id = models.AutoField(primary_key=True)
    propietario = models.CharField(max_length=100)
    estado = models.CharField(max_length=50, choices=[
        ('absuelto', 'Absuelto'),
        ('pagado', 'Pagado'),
        ('no_pagado', 'No Pagado'),
        ('anulado', 'Anulado'),
        ('en_proceso', 'En Proceso'),
    ])
    fecha_reg = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    id_infrac = models.ForeignKey(Infraccion, on_delete=models.CASCADE)
    # No necesitamos un campo separado para el conductor

    def __str__(self):
        return f"Acta {self.id}"
    
class Apelacion(models.Model):
    acta = models.ForeignKey(Acta, on_delete=models.CASCADE)
    asunto = models.TextField()
    documentos = models.FileField(upload_to='apelaciones/')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Apelación {self.acta.id} - {self.fecha}"
