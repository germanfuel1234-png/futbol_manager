"""
Vista de perfil y estadísticas del jugador.
"""
import flet as ft
from src.utils import (
    t, PRIMARY, PRIMARY_LIGHT, SURFACE, SURFACE_2, ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY, load_language, available_languages,
    get_current_lang,
)
from src.services import get_current_user, get_user_stats, logout_user


def build_profile_view(page: ft.Page, on_logout, on_language_changed):
    user = get_current_user()

    def _stat_card(label: str, value: str, icon: str, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=28, color=color),
                    ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Text(label, size=12, color=TEXT_SECONDARY),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            bgcolor=SURFACE_2,
            border_radius=12,
            padding=16,
            expand=True,
        )

    stats = get_user_stats(user.id) if user else {}

    # ─── Cambio de idioma ────────────────────────────────────────────────────
    def on_lang_change(e):
        lang = e.control.value
        load_language(lang)
        on_language_changed()

    lang_dropdown = ft.Dropdown(
        label=t("change_language"),
        options=[ft.dropdown.Option(code, label) for code, label in available_languages()],
        value=get_current_lang(),
        border_color=PRIMARY_LIGHT,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        on_change=on_lang_change,
        width=200,
    )

    return ft.Column(
        [
            # Header
            ft.Container(
                content=ft.Column(
                    [
                        ft.CircleAvatar(
                            content=ft.Text(
                                user.name[0].upper() if user else "?",
                                size=32, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=PRIMARY_LIGHT,
                            radius=40,
                        ),
                        ft.Text(user.name if user else "", size=20,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(user.email if user else "", size=13, color=TEXT_SECONDARY),
                        ft.Text(user.position if user else "", size=13, color=ACCENT),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                ),
                bgcolor=SURFACE_2,
                padding=ft.Padding.symmetric(vertical=24),
                width=float("inf"),
            ),
            # Estadísticas
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(t("my_stats"), size=16,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Row(
                            [
                                _stat_card(t("total_matches"), stats.get("total_matches", 0),
                                           ft.Icons.SPORTS_SOCCER, ACCENT),
                                _stat_card(t("total_goals"), stats.get("total_goals", 0),
                                           ft.Icons.SPORTS_SOCCER, "#FF5722"),
                            ],
                            spacing=12,
                        ),
                        ft.Row(
                            [
                                _stat_card(t("total_assists"), stats.get("total_assists", 0),
                                           ft.Icons.ASSISTANT, PRIMARY_LIGHT),
                                _stat_card("MVP", stats.get("mvp_count", 0),
                                           ft.Icons.STAR, "#FFD700"),
                            ],
                            spacing=12,
                        ),
                    ],
                    spacing=12,
                ),
                padding=ft.Padding.all(16),
            ),
            # Configuración
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(t("settings"), size=16,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        lang_dropdown,
                        ft.ElevatedButton(
                            content=ft.Text(t("logout"), color=TEXT_SECONDARY),
                            icon=ft.Icons.LOGOUT,
                            bgcolor=SURFACE_2,
                            color=TEXT_SECONDARY,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=lambda e: (logout_user(), on_logout()),
                        ),
                    ],
                    spacing=14,
                ),
                padding=ft.Padding.all(16),
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=0,
    )
