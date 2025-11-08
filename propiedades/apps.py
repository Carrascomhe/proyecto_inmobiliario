from django.apps import AppConfig


class PropiedadesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'propiedades'

    def ready(self):
        # Esta línea importa nuestras señales y las "conecta"
        import propiedades.signals
