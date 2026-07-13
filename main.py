"""
Fútbol Manager — Aplicación de gestión de partidos amateur.
Stack: Flet (Python + Flutter rendering) + SQLite (SQLAlchemy)
Multiidioma: Español / Inglés (auto-detección del sistema)
"""
import flet as ft
from src.models import init_db
from src.services import logout_user, get_current_user
from src.utils import t, SURFACE, TEXT_PRIMARY, PRIMARY_LIGHT, SURFACE_2, TEXT_SECONDARY, ACCENT
from src.views import (
    build_auth_view,
    build_dashboard_view,
    build_create_match_view,
    build_match_detail_view,
    build_profile_view,
)

# ─── Rutas de navegación ──────────────────────────────────────────────────────
ROUTE_AUTH = "auth"
ROUTE_DASHBOARD = "dashboard"
ROUTE_CREATE_MATCH = "create_match"
ROUTE_MATCH_DETAIL = "match_detail"
ROUTE_PROFILE = "profile"


def main(page: ft.Page):
    # ── Configuración de la página ────────────────────────────────────────────
    page.title = t("app_name")
    page.bgcolor = SURFACE
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=PRIMARY_LIGHT,
        use_material3=True,
    )
    page.fonts = {}
    page.padding = 0
    page.window.width = 420
    page.window.height = 812
    page.window.min_width = 360

    # Inicializar base de datos
    init_db()

    # ── Estado de navegación ──────────────────────────────────────────────────
    nav_stack: list[dict] = []  # historial de rutas
    refresh_dashboard_fn = [None]
    current_tab = [0]  # 0=dashboard, 1=profile

    main_container = ft.Container(expand=True, padding=0)
    navbar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.SPORTS_SOCCER, label="Partidos"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON, label=t("profile")),
        ],
        selected_index=0,
        bgcolor=SURFACE_2,
        indicator_color=PRIMARY_LIGHT,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        visible=False,
    )

    def navigate(route: str, **kwargs):
        """Navegar a una ruta específica."""
        nav_stack.append({"route": route, **kwargs})
        _render_route(route, **kwargs)

    def go_back():
        if len(nav_stack) > 1:
            nav_stack.pop()
            prev = nav_stack[-1]
            _render_route(prev["route"], **{k: v for k, v in prev.items() if k != "route"})
        else:
            navigate(ROUTE_DASHBOARD)

    def _render_route(route: str, **kwargs):
        main_container.content = None

        if route == ROUTE_AUTH:
            navbar.visible = False
            main_container.content = build_auth_view(
                page,
                on_login_success=lambda: navigate(ROUTE_DASHBOARD),
            )

        elif route == ROUTE_DASHBOARD:
            navbar.visible = True
            navbar.selected_index = 0
            current_tab[0] = 0
            nav_stack.clear()
            nav_stack.append({"route": ROUTE_DASHBOARD})
            view, refresh_fn = build_dashboard_view(
                page,
                on_create_match=lambda: navigate(ROUTE_CREATE_MATCH),
                on_view_match=lambda mid: navigate(ROUTE_MATCH_DETAIL, match_id=mid),
                on_logout=_logout,
            )
            refresh_dashboard_fn[0] = refresh_fn
            main_container.content = view

        elif route == ROUTE_CREATE_MATCH:
            navbar.visible = False
            page.floating_action_button = None
            main_container.content = build_create_match_view(
                page,
                on_created=lambda mid: navigate(ROUTE_MATCH_DETAIL, match_id=mid),
                on_back=go_back,
            )

        elif route == ROUTE_MATCH_DETAIL:
            navbar.visible = False
            page.floating_action_button = None
            match_id = kwargs.get("match_id")
            main_container.content = build_match_detail_view(
                page,
                match_id=match_id,
                on_back=go_back,
                on_deleted=lambda: navigate(ROUTE_DASHBOARD),
            )

        elif route == ROUTE_PROFILE:
            navbar.visible = True
            navbar.selected_index = 1
            current_tab[0] = 1
            page.floating_action_button = None
            main_container.content = build_profile_view(
                page,
                on_logout=_logout,
                on_language_changed=lambda: _rebuild_app(),
            )

        page.update()

    def _logout():
        logout_user()
        nav_stack.clear()
        navigate(ROUTE_AUTH)

    def _rebuild_app():
        """Reconstruir la app completa al cambiar idioma."""
        page.title = t("app_name")
        route = nav_stack[-1]["route"] if nav_stack else ROUTE_AUTH
        _render_route(route)

    def on_navbar_change(e):
        idx = e.control.selected_index
        if idx == 0 and current_tab[0] != 0:
            navigate(ROUTE_DASHBOARD)
        elif idx == 1 and current_tab[0] != 1:
            navigate(ROUTE_PROFILE)

    navbar.on_change = on_navbar_change

    # ── Layout principal ──────────────────────────────────────────────────────
    page.add(
        ft.Column(
            [
                ft.Container(content=main_container, expand=True, padding=0),
                navbar,
            ],
            spacing=0,
            expand=True,
        )
    )

    # ── Pantalla inicial ──────────────────────────────────────────────────────
    if get_current_user():
        navigate(ROUTE_DASHBOARD)
    else:
        navigate(ROUTE_AUTH)


if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"\n{'='*45}")
    print(f"  Fútbol Manager — Servidor Web Local")
    print(f"  Abrí en este equipo:  http://localhost:8080")
    print(f"  Desde otros en el WiFi: http://{local_ip}:8080")
    print(f"{'='*45}\n")
    ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER, port=8080)
