from django.db import models

# Create your models here.


# Definicion de la tabla en Django Admin 
class Empresa(models.Model):
    cliente=models.CharField(max_length=100)
    compania=models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True, blank=True, editable=False)
    logo=models.ImageField(upload_to='logos/', blank=True, null=True)
    telefono=models.CharField(max_length=15)
    correo=models.EmailField()
    pais=models.CharField(max_length=50)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)  
    fecha_actualizacion = models.DateTimeField(auto_now=True) 

    # Generar código único al guardar por primera vez
    def save(self, *args, **kwargs):
        creando = self.pk is None
        super().save(*args, **kwargs)
        if creando and not self.codigo:
            self.codigo = f"{self.id:04d}"
            super().save(update_fields=['codigo'])
    # 
    def __str__(self):
        return f"{self.cliente}  ({self.codigo})"




