# propiedades/management/commands/revisar_pagos.py

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from propiedades.models import Pago
import datetime

# --- ¡Importaciones actualizadas! ---
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string # Para usar plantillas HTML
from django.utils.html import strip_tags # Para crear la versión de solo-texto

class Command(BaseCommand):
    help = 'Revisa pagos, marca vencidos y envía recordatorios por email HTML.'

    def handle(self, *args, **options):
        
        hoy = timezone.now().date()
        self.stdout.write(f"--- [REVISAR PAGOS] Iniciando (Fecha de hoy: {hoy}) ---")
        
        # --- TAREA 1: MARCAR PAGOS VENCIDOS (Sin cambios) ---
        pagos_vencidos = Pago.objects.filter(
            estado='Pendiente',
            fecha_vencimiento__lt=hoy
        )
        count_vencidos = pagos_vencidos.count()

        if count_vencidos > 0:
            self.stdout.write(f"¡Se encontraron {count_vencidos} pagos vencidos!")
            pagos_vencidos.update(estado='Vencido')
            self.stdout.write(self.style.SUCCESS(f"--- ÉXITO: {count_vencidos} pagos marcados como 'Vencido'. ---"))
        else:
            self.stdout.write("--- No se encontraron pagos vencidos. Todo en orden. ---")

        
        # --- TAREA 2: ENVIAR RECORDATORIOS (¡Versión HTML!) ---
        self.stdout.write("\n--- Buscando pagos para enviar recordatorios ---")
        
        dias_de_aviso = 5
        fecha_recordatorio = hoy + datetime.timedelta(days=dias_de_aviso)
        
        pagos_proximos = Pago.objects.filter(
            estado='Pendiente',
            fecha_vencimiento=fecha_recordatorio
        ).select_related('contrato__inquilino__user')

        count_recordatorios = pagos_proximos.count()
        
        if count_recordatorios > 0:
            self.stdout.write(f"¡Se encontraron {count_recordatorios} pagos que vencen en 5 días!")
            
            for pago in pagos_proximos:
                inquilino = pago.contrato.inquilino
                
                if inquilino.email:
                    
                    asunto = f"Recordatorio de Pago - Contrato {pago.contrato.propiedad.titulo}"
                    
                    # 1. Definimos el "contexto" (las variables para la plantilla)
                    contexto = {
                        'pago': pago,
                        'inquilino': inquilino,
                    }
                    
                    # 2. Renderizamos la plantilla HTML en un string
                    html_message = render_to_string('propiedades/emails/recordatorio_pago.html', contexto)
                    
                    # 3. (Buena práctica) Creamos una versión de solo-texto
                    plain_message = strip_tags(html_message)
                    
                    # 4. ¡Enviamos el email!
                    send_mail(
                        asunto,
                        plain_message, # El mensaje de solo-texto
                        settings.DEFAULT_FROM_EMAIL, # "De:"
                        [inquilino.email],             # "Para:"
                        html_message=html_message, # ¡Aquí adjuntamos la versión HTML!
                        fail_silently=False,
                    )
                    
                    self.stdout.write(f" -> Email (HTML) enviado a {inquilino.email} por pago de {pago.monto}")
                
                else:
                    self.stdout.write(f" -> ADVERTENCIA: Inquilino {inquilino.nombre_completo} no tiene email.")
            
            self.stdout.write(self.style.SUCCESS(f"--- ÉXITO: {count_recordatorios} recordatorios procesados. ---"))
        
        else:
            self.stdout.write("--- No se encontraron pagos que venzan en 5 días. ---")