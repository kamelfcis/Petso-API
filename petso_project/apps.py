from django.apps import AppConfig


class PetsoProjectConfig(AppConfig):
    """Registers project-level management commands (next to settings)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "petso_project"
    label = "petso_project"
    verbose_name = "Petso project"
