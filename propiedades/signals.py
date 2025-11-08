# propiedades/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Contrato, Pago
from dateutil.relativedelta import relativedelta # La herramienta que instalamos
from decimal import Decimal

# Esta es la función que se "disparará"
# @receiver le dice a Django: "Escucha la señal 'post_save' del modelo 'Contrato'"
@receiver(post_save, sender=Contrato)
def crear_pagos_mensuales(sender, instance, created, **kwargs):
    """
    Crea automáticamente los registros de Pago mensuales 
    cuando se crea un nuevo Contrato.
    (Versión Corregida)
    """
    
    if created:
        
        print(f"--- SEÑAL RECIBIDA: Creando pagos para el contrato de {instance.propiedad.titulo} ---")
        
        contrato = instance
        fecha_actual = contrato.fecha_inicio
        fecha_fin = contrato.fecha_fin
        dia_pago = contrato.dia_pago_mensual
        
        # --- LÓGICA DE MONTO CORREGIDA ---
        # Usamos 'monto_base' para el cálculo y 'monto_a_pagar' para el pago
        monto_base = contrato.monto_renta_actual
        monto_a_pagar = contrato.monto_renta_actual # <--- Esta es la variable que usaremos
        
        frecuencia_aumento = contrato.frecuencia_aumento_meses
        porcentaje_aumento = Decimal(contrato.porcentaje_aumento / 100)
        mes_contador = 0
        # --- FIN LÓGICA CORREGIDA ---
        
        pagos_a_crear = []
        
        try:
            fecha_pago_actual = fecha_actual.replace(day=dia_pago)
        except ValueError:
            primer_dia_mes_siguiente = fecha_actual.replace(day=1) + relativedelta(months=1)
            fecha_pago_actual = primer_dia_mes_siguiente - relativedelta(days=1)

        if fecha_actual.day > dia_pago:
            fecha_pago_actual += relativedelta(months=1)
        
        while fecha_pago_actual <= fecha_fin:
            
            mes_contador += 1
            
            if mes_contador > 1 and (mes_contador - 1) % frecuencia_aumento == 0:
                # Calculamos el aumento sobre el monto base
                aumento = monto_base * porcentaje_aumento
                # Actualizamos el monto base Y el monto a pagar
                monto_base = (monto_base + aumento).quantize(Decimal('0.01'))
                monto_a_pagar = monto_base # Asignamos el nuevo monto
                
                print(f"--- ¡AUMENTO APLICADO! Nuevo monto {monto_a_pagar} en el mes {mes_contador} ---")
            else:
                # Si no hay aumento, nos aseguramos de usar el monto actual
                monto_a_pagar = monto_base
            
            pagos_a_crear.append(
                Pago(
                    contrato=contrato,
                    monto=monto_a_pagar, # <--- Usamos la variable 'monto_a_pagar'
                    fecha_vencimiento=fecha_pago_actual,
                    estado='Pendiente'
                )
            )
            
            fecha_pago_actual += relativedelta(months=1)
        
        if pagos_a_crear:
            Pago.objects.bulk_create(pagos_a_crear)
            print(f"--- ÉXITO: Se crearon {len(pagos_a_crear)} pagos. ---")
        else:
            print("--- ADVERTENCIA: No se generaron pagos (revisar fechas). ---")