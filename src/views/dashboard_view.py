"""
Dashboard principal: lista de partidos con filtros básicos.
"""
import flet as ft
from datetime import datetime
from src.utils import (
    t, PRIMARY, PRIMARY_LIGHT, SURFACE, SURFACE_2, ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY, STATUS_COLORS, MATCH_TYPE_COLORS,
    WARNING, SUCCESS, ERROR,
)
from src.services import get_all_matches, get_current_user


def _match_type_label(match_type: str) -> str:
    labels = {
        "futsal": t("futsal"),
        "football7": t("football7"),
        "football11": t("football11"),
    }
    return labels.get(match_type, match_type)


def _status_label(status: str) -> str:
    labels = {
        "pending": t("status_pending"),
        "in_progress": t("status_in_progress"),
        "finished": t("status_finished"),
    }
    return labels.get(status, status)


def build_match_card(match: dict, on_tap) -> ft.GestureDetector:
    type_color = MATCH_TYPE_COLORS.get(match["match_type"], PRIMARY_LIGHT)
    status_color = STATUS_COLORS.get(match["status"], TEXT_SECONDARY)
    date_str = match["match_date"].strftime("%d/%m/%Y %H:%M") if isinstance(
        match["match_date"], datetime) else str(match["match_date"])

    card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(
                                _match_type_label(match["match_type"]),
                                size=11, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=type_color,
                            border_radius=20,
                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        ),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Text(
                                _status_label(match["status"]),
                                size=11, color=TEXT_PRIMARY,
                            ),
                            bgcolor=status_color,
                            border_radius=20,
                            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(match["title"], size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=TEXT_SECONDARY),
                        ft.Text(date_str, size=13, color=TEXT_SECONDARY),
                    ],
                    spacing=4,
                ),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LOCATION_ON, size=14, color=TEXT_SECONDARY),
                        ft.Text(match["venue"] or "—", size=13, color=TEXT_SECONDARY),
                    ],
                    spacing=4,
                ),
                ft.Divider(color=SURFACE, height=1),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(t("players"), size=11, color=TEXT_SECONDARY),
                                ft.Text(
                                    f"{match['confirmed_count']}/{match['max_players']}",
                                    size=16, weight=ft.FontWeight.BOLD, color=ACCENT,
                                ),
                            ],
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.VerticalDivider(color=SURFACE, width=1),
                        ft.Column(
                            [
                                ft.Text(t("cost_per_player"), size=11, color=TEXT_SECONDARY),
                                ft.Text(
                                    f"${match['cost_per_player']:,.0f}",
                                    size=16, weight=ft.FontWeight.BOLD, color=SUCCESS,
                                ),
                            ],
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.VerticalDivider(color=SURFACE, width=1),
                        ft.Column(
                            [
                                ft.Text(t("spots_available"), size=11, color=TEXT_SECONDARY),
                                ft.Text(
                                    str(match["available_spots"]),
                                    size=16, weight=ft.FontWeight.BOLD,
                                    color=WARNING if match["available_spots"] < 3 else TEXT_PRIMARY,
                                ),
                            ],
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),
            ],
            spacing=8,
        ),
        bgcolor=SURFACE_2,
        border_radius=12,
        padding=16,
        margin=ft.Margin.only(bottom=10),
    )

    return ft.GestureDetector(
        content=card,
        on_tap=lambda e: on_tap(match["id"]),
        mouse_cursor=ft.MouseCursor.CLICK,
    )


def build_dashboard_view(page: ft.Page, on_create_match, on_view_match, on_logout):
    user = get_current_user()
    matches_list = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
    filter_value = [None]  # None = todos

    def refresh_matches():
        matches_list.controls.clear()
        matches = get_all_matches()
        filtered = matches if filter_value[0] is None else [
            m for m in matches if m["match_type"] == filter_value[0]
        ]
        if not filtered:
            matches_list.controls.append(
                ft.Container(
                    content=ft.Text(t("no_matches"), color=TEXT_SECONDARY, size=15),
                    alignment=ft.alignment.center,
                    padding=40,
                )
            )
        else:
            for m in filtered:
                matches_list.controls.append(
                    build_match_card(m, on_view_match)
                )
        page.update()

    def filter_tab_changed(e):
        idx = e.control.selected_index
        filter_value[0] = [None, "futsal", "football7", "football11"][idx]
        refresh_matches()

    # ─── Header ───────────────────────────────────────────────────────────────
    header = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(t("dashboard"), size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(
                            f"👋 {user.name if user else ''}",
                            size=14, color=TEXT_SECONDARY,
                        ),
                    ],
                    spacing=2,
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    icon_color=TEXT_SECONDARY,
                    tooltip=t("logout"),
                    on_click=lambda e: on_logout(),
                ),
            ],
        ),
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        bgcolor=SURFACE_2,
    )

    # ─── Tabs de filtro ───────────────────────────────────────────────────────
    tabs = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.SPORTS_SOCCER, label="Todos"),
            ft.NavigationBarDestination(icon=ft.Icons.SPORTS_SOCCER, label=t("futsal")),
            ft.NavigationBarDestination(icon=ft.Icons.SPORTS_SOCCER, label=t("football7")),
            ft.NavigationBarDestination(icon=ft.Icons.STADIUM, label=t("football11")),
        ],
        selected_index=0,
        bgcolor=SURFACE_2,
        indicator_color=PRIMARY,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        on_change=filter_tab_changed,
    )

    # ─── FAB ──────────────────────────────────────────────────────────────────
    fab = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=PRIMARY_LIGHT,
        foreground_color=TEXT_PRIMARY,
        tooltip=t("create_match"),
        on_click=lambda e: on_create_match(),
    )

    refresh_matches()

    # FAB nativo de página (no interfiere con los taps de las cards)
    page.floating_action_button = fab
    page.update()

    return ft.Column(
        [
            header,
            ft.Container(
                content=matches_list,
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                expand=True,
            ),
            tabs,
        ],
        expand=True,
        spacing=0,
    ), refresh_matches
