"""
Ejecutar en modo escritorio para pruebas locales.
Uso: python run_desktop.py
"""
import flet as ft
from main import main

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
