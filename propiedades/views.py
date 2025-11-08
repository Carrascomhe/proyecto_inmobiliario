# propiedades/views.py

from django.shortcuts import render, get_object_or_404
from .models import Propiedad, Cliente, Contrato, Pago  # Importamos nuestro modelo Propiedad
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Esta es la función que conectamos en urls.py
def pagina_inicio(request):
    
    # 1. Consultar la base de datos
    # Pedimos las propiedades que estén Disponibles Y sean de Renta
    propiedades_renta = Propiedad.objects.filter(
        estado='Disponible',
        tipo_operacion='Renta'
    ).order_by('-id')[:6] # '-id' = de la más nueva a la más vieja, [:6] = solo 6
    
    # Pedimos las propiedades que estén Disponibles Y sean de Venta
    propiedades_venta = Propiedad.objects.filter(
        estado='Disponible',
        tipo_operacion='Venta'
    ).order_by('-id')[:6]
    
    # 2. Preparar el "contexto" (los datos para el HTML)
    contexto = {
        'listado_renta': propiedades_renta,
        'listado_venta': propiedades_venta,
    }
    
    # 3. Renderizar la plantilla HTML
    # Le decimos a Django que dibuje el archivo 'index.html'
    # y le pasamos los datos del 'contexto'
    return render(request, 'propiedades/index.html', contexto)

def detalle_propiedad(request, pk):
    # 1. Buscamos la propiedad con el 'pk' (ID) que vino de la URL
    #    get_object_or_404: Intenta buscar la propiedad. Si no existe,
    #    automáticamente muestra una página de Error 404 (No Encontrado).
    prop = get_object_or_404(Propiedad, pk=pk)
    
    # 2. Preparamos el contexto (solo esta propiedad)
    contexto = {
        'propiedad': prop
    }
    
    # 3. Renderizamos la *nueva* plantilla 'detalle.html'
    return render(request, 'propiedades/detalle.html', contexto)

# ¡NUEVA VISTA!
# Este 'decorador' protege la vista.
# Si un usuario no logueado intenta entrar, lo manda a la página de LOGIN_URL
@login_required 
def portal_inquilino(request):

    cliente_perfil = None
    lista_contratos = []

    # --- ¡NUEVAS VARIABLES DE NOTIFICACIÓN! ---
    pagos_vencidos = None
    proximo_pago = None
    hoy = timezone.now().date() # Obtenemos la fecha de hoy

    try:
        # 1. Busca el perfil de cliente
        cliente_perfil = Cliente.objects.get(user=request.user)

        # 2. Busca los contratos de ESE cliente
        lista_contratos = Contrato.objects.filter(
            inquilino=cliente_perfil
        ).select_related('propiedad')

        # 3. ¡NUEVA LÓGICA DE BÚSQUEDA DE PAGOS!

        # Buscamos pagos VENCIDOS (estado 'Pendiente' Y fecha pasada)
        pagos_vencidos = Pago.objects.filter(
            contrato__inquilino=cliente_perfil, # Pagos de este cliente
            estado='Pendiente',
            fecha_vencimiento__lt=hoy # __lt = "less than" (menor que hoy)
        ).order_by('fecha_vencimiento') # Del más antiguo al más nuevo

        # Buscamos el PRÓXIMO pago (estado 'Pendiente' Y fecha futura)
        proximo_pago = Pago.objects.filter(
            contrato__inquilino=cliente_perfil, # Pagos de este cliente
            estado='Pendiente',
            fecha_vencimiento__gte=hoy # __gte = "greater than or equal" (mayor o igual que hoy)
        ).order_by('fecha_vencimiento').first() # .first() toma solo el primero

    except Cliente.DoesNotExist:
        pass # Si no hay cliente, las variables se quedan en None

    contexto = {
        'usuario': request.user,
        'cliente': cliente_perfil,
        'contratos': lista_contratos,
        'pagos_vencidos': pagos_vencidos,   # <-- ¡NUEVO!
        'proximo_pago': proximo_pago         # <-- ¡NUEVO!
    }

    return render(request, 'propiedades/portal.html', contexto)

def pagina_renta(request):
    
    # 1. Buscamos TODAS las propiedades que sean 'Renta' y 'Disponible'
    listado_renta = Propiedad.objects.filter(
        estado='Disponible',
        tipo_operacion='Renta'
    ).order_by('-id') # '-id' = de la más nueva a la más vieja
    
    # 2. Preparamos el contexto
    contexto = {
        'titulo_pagina': 'Propiedades en Renta',
        'listado_propiedades': listado_renta,
    }
    
    # 3. Renderizamos una NUEVA plantilla
    return render(request, 'propiedades/listado.html', contexto)

def pagina_venta(request):
    
    # 1. Buscamos TODAS las propiedades que sean 'Venta' y 'Disponible'
    listado_venta = Propiedad.objects.filter(
        estado='Disponible',
        tipo_operacion='Venta'  # <-- ¡Este es el único cambio!
    ).order_by('-id')
    
    # 2. Preparamos el contexto
    contexto = {
        'titulo_pagina': 'Propiedades en Venta', # <-- Título nuevo
        'listado_propiedades': listado_venta,
    }
    
    # 3. ¡REUTILIZAMOS la plantilla 'listado.html'!
    return render(request, 'propiedades/listado.html', contexto)