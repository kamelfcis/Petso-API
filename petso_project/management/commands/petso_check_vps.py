from django.core.management.base import BaseCommand

from petso_project.vps_upload_checks import run_petso_vps_checks


class Command(BaseCommand):
    help = "Check media directory and env when file uploads fail on VPS but work locally."

    def handle(self, *args, **options):
        run_petso_vps_checks(self.stdout)
