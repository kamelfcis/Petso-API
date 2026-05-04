#!/usr/bin/env python3
"""
VPS / upload checks without relying on Django command discovery.

Run from project root (same folder as manage.py):
    python petso_check_vps.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "petso_project.settings")
    import django

    django.setup()
    from petso_project.vps_upload_checks import run_petso_vps_checks

    run_petso_vps_checks(sys.stdout)


if __name__ == "__main__":
    main()
