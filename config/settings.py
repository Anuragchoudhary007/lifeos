"""
LifeOS Configuration Settings

Central configuration file for the application.
All global settings should be defined here.
"""

from __future__ import annotations

from pathlib import Path


class Settings:
    """Application configuration."""

    # --------------------------------------------------
    # Project
    # --------------------------------------------------

    APP_NAME = "LifeOS"
    VERSION = "0.1.0"
    DEBUG = True

    # --------------------------------------------------
    # Paths
    # --------------------------------------------------

    ROOT_DIR = Path(__file__).resolve().parent.parent

    STORAGE_DIR = ROOT_DIR / "storage"

    DATABASE_DIR = STORAGE_DIR / "database"

    EXPORT_DIR = STORAGE_DIR / "exports"

    IMPORT_DIR = STORAGE_DIR / "imports"

    BACKUP_DIR = STORAGE_DIR / "backups"

    CACHE_DIR = STORAGE_DIR / "cache"

    LOG_DIR = STORAGE_DIR / "logs"

    # --------------------------------------------------
    # Database
    # --------------------------------------------------

    DATABASE_NAME = "lifeos.db"

    DATABASE_URL = f"sqlite:///{DATABASE_DIR / DATABASE_NAME}"


settings = Settings()