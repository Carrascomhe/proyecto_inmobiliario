# propiedades/admin.py

from django.contrib import admin
from .models import Propiedad, Cliente, Contrato, FotoPropiedad, Pago

# --- Personalización para el modelo Propiedad ---
class FotoPropiedadInline(admin.TabularInline):
    model = FotoPropiedad
    extra = 1 # Muestra un campo vacío para añadir una foto extra
    max_num = 10 # Limita a un máximo de 10 fotos por propiedad

@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en la lista
    list_display = ('titulo', 'tipo_operacion', 'estado', 'precio', 'ciudad')
    
    # Filtros que aparecerán a la derecha
    list_filter = ('tipo_operacion', 'estado', 'ciudad')
    
    # Barra de búsqueda
    search_fields = ('titulo', 'descripcion', 'direccion', 'ciudad')

    inlines = [FotoPropiedadInline]

# --- Personalización para el modelo Cliente ---
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'email', 'telefono')
    search_fields = ('nombre_completo', 'email', 'user__username')
    raw_id_fields = ('user',)

# --- Personalización para el modelo Contrato ---
@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('get_propiedad_titulo', 'get_inquilino_nombre', 'fecha_inicio', 'fecha_fin', 'monto_renta_actual')
    list_filter = ('fecha_inicio', 'fecha_fin')
    search_fields = ('propiedad__titulo', 'inquilino__nombre_completo') # Buscar dentro de los modelos relacionados

    # Funciones para mostrar nombres legibles en la lista
    def get_propiedad_titulo(self, obj):
        return obj.propiedad.titulo
    get_propiedad_titulo.short_description = 'Propiedad' # Nombre de la columna

    def get_inquilino_nombre(self, obj):
        return obj.inquilino.nombre_completo
    get_inquilino_nombre.short_description = 'Inquilino' # Nombre de la columna

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', # Muestra el nombre descriptivo del pago
        'contrato', 
        'monto', 
        'fecha_vencimiento', 
        'estado', 
        'fecha_pago'
    )
    list_filter = ('estado', 'fecha_vencimiento') # ¡Filtros muy útiles!
    search_fields = ('contrato__propiedad__titulo', 'contrato__inquilino__nombre_completo')

    # Para hacer el campo 'estado' editable desde la lista
    list_editable = ('estado', 'fecha_pago') 

    # Optimización para el campo de contrato
    raw_id_fields = ('contrato',)
