"""
Signals for core app - Site configuration
"""
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.conf import settings
import os


@receiver(post_migrate)
def update_site_config(sender, **kwargs):
    """
    Actualiza la configuración del Site después de las migraciones.
    Esto asegura que el nombre del sitio esté correcto en los emails.
    """
    if sender.name == 'sites':
        try:
            site = Site.objects.get(pk=settings.SITE_ID)
            site.domain = os.environ.get('SITE_DOMAIN', 'localhost:8000')
            site.name = os.environ.get('SITE_NAME', 'Agenda Personal')
            site.save()
        except Site.DoesNotExist:
            # Si no existe, se creará automáticamente
            pass

