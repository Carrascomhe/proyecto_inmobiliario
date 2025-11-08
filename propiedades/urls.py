# propiedades/urls.py

from django.urls import path
from . import views  # Importamos las vistas (las crearemos en el sig. paso)

urlpatterns = [
    # Esta es nuestra página de inicio
    path('', views.pagina_inicio, name='inicio'),
    path('propiedad/<int:pk>/', views.detalle_propiedad, name='detalle'),
    path('portal/', views.portal_inquilino, name='portal'),
    path('renta/', views.pagina_renta, name='pagina-renta'),
    path('venta/', views.pagina_venta, name='pagina-venta'),
]