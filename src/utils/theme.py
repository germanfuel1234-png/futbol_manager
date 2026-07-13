"""
Constantes de colores y estilos para toda la app.
Paleta: verde fútbol + oscuro.
"""
import flet as ft

# ─── Colores principales ──────────────────────────────────────────────────────
PRIMARY = "#1B5E20"        # Verde oscuro
PRIMARY_LIGHT = "#4CAF50"  # Verde medio
ACCENT = "#76FF03"         # Verde neón (accent)
SURFACE = "#1E1E2E"        # Fondo oscuro
SURFACE_2 = "#2A2A3E"      # Card fondo
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#B0BEC5"
ERROR = "#EF5350"
WARNING = "#FFA726"
SUCCESS = "#66BB6A"
PAID_COLOR = "#4CAF50"
PENDING_COLOR = "#FFA726"
CONFIRMED_COLOR = "#29B6F6"

# ─── Tipos de partido ────────────────────────────────────────────────────────
MATCH_TYPE_COLORS = {
    "futsal": "#7B1FA2",
    "football7": "#0288D1",
    "football11": "#1B5E20",
}

MATCH_TYPE_ICONS = {
    "futsal": ft.Icons.SPORTS_SOCCER,
    "football7": ft.Icons.SPORTS_SOCCER,
    "football11": ft.Icons.STADIUM,
}

STATUS_COLORS = {
    "pending": WARNING,
    "in_progress": PRIMARY_LIGHT,
    "finished": TEXT_SECONDARY,
}


def text_style(size: int = 14, color: str = TEXT_PRIMARY,
               weight=ft.FontWeight.NORMAL) -> ft.TextStyle:
    return ft.TextStyle(size=size, color=color, weight=weight)


def card_style(padding: int = 16) -> dict:
    return {
        "bgcolor": SURFACE_2,
        "border_radius": 12,
        "padding": padding,
    }
