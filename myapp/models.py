from django.db import models

# Create your models here.


# Definicion de la tabla en Django Admin 
class Empresa(models.Model):
    cliente = models.CharField(max_length=100)
    compania = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True, blank=True, editable=False)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField()
    pais = models.CharField(max_length=50)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)  
    fecha_actualizacion = models.DateTimeField(auto_now=True) 

    def save(self, *args, **kwargs):
        creando = self.pk is None
        super().save(*args, **kwargs)
        
        if creando and not self.codigo:
            # Obtener el último código numérico existente
            ultimo_codigo = Empresa.objects.exclude(codigo='').exclude(pk=self.pk).order_by('-codigo').first()
            
            if ultimo_codigo and ultimo_codigo.codigo:
                try:
                    # Extraer el número del último código (ej: "0020" -> 20)
                    ultimo_num = int(ultimo_codigo.codigo)
                    nuevo_num = ultimo_num + 1
                except ValueError:
                    # Si no se puede convertir, usar el ID
                    nuevo_num = self.id
            else:
                # Si no hay códigos, empezar desde 1
                nuevo_num = 1
            
            self.codigo = f"{nuevo_num:04d}"
            super().save(update_fields=['codigo'])

    def __str__(self):
        return f"{self.cliente} ({self.codigo})"





