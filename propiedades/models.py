# propiedades/models.py

from django.db import models
from django.contrib.auth.models import User

# --- Modelo 1: Cliente (Inquilino o Propietario) ---
class Cliente(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, # Si se borra el User, no se borra el Cliente
        null=True,                 # Permite que esté vacío en la BD
        blank=True                 # Permite que esté vacío en el Admin
    )
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField(unique=True) # unique=True para evitar emails duplicados
    telefono = models.CharField(max_length=20, blank=True) # blank=True = no es obligatorio

    def __str__(self):
        return self.nombre_completo

# --- Modelo 2: Propiedad (La casa o depto) ---
class Propiedad(models.Model):
    
    # Opciones para los menús desplegables
    OPERACION_CHOICES = [
        ('Renta', 'Renta'),
        ('Venta', 'Venta'),
    ]
    ESTADO_CHOICES = [
        ('Disponible', 'Disponible'),
        ('Rentada', 'Rentada'),
        ('Vendida', 'Vendida'),
    ]

    # Campos de la base de datos
    titulo = models.CharField(max_length=250)
    descripcion = models.TextField(blank=True) # blank=True = no es obligatorio
    
    tipo_operacion = models.CharField(max_length=10, choices=OPERACION_CHOICES)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Disponible')
    
    precio = models.DecimalField(max_digits=12, decimal_places=2) # Para guardar dinero
    
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    
    num_habitaciones = models.PositiveIntegerField(default=1) # Número positivo
    num_baños = models.PositiveIntegerField(default=1)
    metros_cuadrados = models.PositiveIntegerField(default=50)

    foto_principal = models.ImageField(upload_to='propiedades/', blank=True, null=True)

    def __str__(self):
        # Esto es lo que veremos en el panel de admin (ej: "Renta: Depto 2 recámaras en Centro")
        return f"{self.tipo_operacion}: {self.titulo}"

class FotoPropiedad(models.Model):
    propiedad = models.ForeignKey(
        Propiedad,
        on_delete=models.CASCADE, # Si se borra la propiedad, se borran sus fotos
        related_name='fotos_galeria' # Nos permitirá acceder a las fotos desde la propiedad
    )
    imagen = models.ImageField(upload_to='propiedades/galeria/')
    descripcion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Foto de Galería"
        verbose_name_plural = "Fotos de Galería"

    def __str__(self):
        return f"Foto de {self.propiedad.titulo}"

# --- Modelo 3: Contrato (La magia que une todo) ---
class Contrato(models.Model):
    propiedad = models.ForeignKey(
        Propiedad, 
        on_delete=models.PROTECT, # No deja borrar una propiedad si tiene un contrato
        limit_choices_to={'tipo_operacion': 'Renta', 'estado': 'Disponible'} # Solo rentar disponibles
    )
    inquilino = models.ForeignKey(
        Cliente, 
        on_delete=models.PROTECT # No deja borrar un cliente si tiene un contrato
    )
    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    monto_renta_actual = models.DecimalField(max_digits=10, decimal_places=2)
    dia_pago_mensual = models.PositiveIntegerField(default=1) # ej. Pagar los días "1"

    # Tus reglas de aumento
    frecuencia_aumento_meses = models.PositiveIntegerField(
        default=12, # Aumento cada 12 meses
        help_text="¿Cada cuántos meses se aplica el aumento? (ej. 12)"
    )
    porcentaje_aumento = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.00, # Aumento del 10%
        help_text="Porcentaje de aumento (ej. 10 para 10%)"
    )
    
    # fecha_proximo_aumento = models.DateField(blank=True, null=True) # Este lo calcularemos luego

    def __str__(self):
        return f"Contrato de {self.propiedad.titulo} para {self.inquilino.nombre_completo}"
    
class Pago(models.Model):
    ESTADO_PAGO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Pagado', 'Pagado'),
        ('Vencido', 'Vencido'),
    ]

    contrato = models.ForeignKey(
        Contrato,
        on_delete=models.CASCADE, # Si se borra el contrato, se borran sus pagos
        related_name='pagos' # Para hacer contrato.pagos.all()
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(
        max_length=10, 
        choices=ESTADO_PAGO_CHOICES, 
        default='Pendiente'
    )
    fecha_pago = models.DateField(
        blank=True, 
        null=True, # Solo se llena cuando 'estado' es 'Pagado'
        help_text="Fecha en que se confirmó el pago"
    )

    class Meta:
        # Ordena los pagos por fecha de vencimiento (el más nuevo primero)
        ordering = ['fecha_vencimiento']
        verbose_name = "Pago Mensual"
        verbose_name_plural = "Pagos Mensuales"

    def __str__(self):
        return f"Pago de {self.contrato.propiedad.titulo} - {self.fecha_vencimiento}"
