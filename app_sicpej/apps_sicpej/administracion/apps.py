from django.apps import AppConfig
from django.db.models.signals import pre_save, post_save

class AdministracionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps_sicpej.administracion'

    def ready(self):
        from .signals import pre_save_handler, post_save_handler
        from django.apps import apps

        for model in apps.get_models():
            try:
                pre_save.connect(pre_save_handler, sender=model, weak=False)
                post_save.connect(post_save_handler, sender=model, weak=False)
            except Exception:
                continue  # Evitar modelos incompatibles