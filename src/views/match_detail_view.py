"""
Vista de detalle de partido: jugadores, pagos y estadísticas.
"""
import flet as ft
from datetime import datetime
from src.utils import (
    t, PRIMARY, PRIMARY_LIGHT, SURFACE, SURFACE_2, ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY, ERROR, SUCCESS, WARNING,
    PAID_COLOR, PENDING_COLOR, CONFIRMED_COLOR, STATUS_COLORS,
    MATCH_TYPE_COLORS,
)
from src.services import (
    get_match_detail, add_player_to_match, update_payment_status,
    update_match_status, save_match_stats, delete_match, get_current_user,
)


def _payment_chip(status: str, on_change) -> ft.GestureDetector:
    colors = {
        "pending": PENDING_COLOR,
        "paid": PAID_COLOR,
        "confirmed": CONFIRMED_COLOR,
    }
    labels = {
        "pending": t("pending"),
        "paid": t("paid"),
        "confirmed": t("confirmed_by_org"),
    }
    color = colors.get(status, TEXT_SECONDARY)
    return ft.GestureDetector(
        content=ft.Container(
            content=ft.Text(labels.get(status, status), size=11, color=TEXT_PRIMARY),
            bgcolor=color,
            border_radius=20,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        ),
        on_tap=on_change,
        mouse_cursor=ft.MouseCursor.CLICK if on_change else ft.MouseCursor.BASIC,
    )


def build_match_detail_view(page: ft.Page, match_id: int, on_back, on_deleted=None):
    current_user = get_current_user()
    detail = [get_match_detail(match_id)]  # mutable container

    content_area = ft.Column(spacing=0, expand=True)
    snackbar = ft.SnackBar(content=ft.Text(""), bgcolor=SUCCESS)
    page.overlay.append(snackbar)

    def show_snack(msg: str, color=SUCCESS):
        snackbar.content = ft.Text(msg, color=TEXT_PRIMARY)
        snackbar.bgcolor = color
        snackbar.open = True
        page.update()

    def refresh():
        detail[0] = get_match_detail(match_id)
        render()

    def cycle_payment(mp_id: int, current_status: str):
        """Cicla: pending → paid → confirmed → pending"""
        cycle = {"pending": "paid", "paid": "confirmed", "confirmed": "pending"}
        new_status = cycle.get(current_status, "pending")
        update_payment_status(mp_id, new_status)
        refresh()

    def on_add_player(e):
        def confirm(dialog_e):
            email = txt_player_email.value.strip()
            if email:
                ok, result = add_player_to_match(match_id, email)
                if ok:
                    show_snack(f"✅ {result} agregado")
                    refresh()
                else:
                    show_snack(t(result) if result in [
                        "user_not_found", "already_in_match", "match_full"
                    ] else result, ERROR)
            page.close(dialog)

        txt_player_email = ft.TextField(
            label=t("email"),
            prefix_icon=ft.Icons.EMAIL,
            border_color=PRIMARY_LIGHT,
            color=TEXT_PRIMARY,
        )
        dialog = ft.AlertDialog(
            title=ft.Text(t("add_player"), color=TEXT_PRIMARY),
            bgcolor=SURFACE_2,
            content=txt_player_email,
            actions=[
                ft.TextButton(content=ft.Text(t("cancel")), on_click=lambda e: page.close(dialog)),
                ft.ElevatedButton(content=ft.Text(t("save"), color=TEXT_PRIMARY), bgcolor=PRIMARY_LIGHT,
                                  color=TEXT_PRIMARY, on_click=confirm),
            ],
        )
        page.open(dialog)

    def on_change_status(e):
        d = detail[0]
        cycle = {"pending": "in_progress", "in_progress": "finished", "finished": "pending"}
        new_s = cycle.get(d["status"], "pending")
        update_match_status(match_id, new_s)
        refresh()

    def on_delete(e):
        def confirm_delete(de):
            page.close(confirm_dialog)
            delete_match(match_id)
            if on_deleted:
                on_deleted()
            else:
                on_back()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text(t("confirm_delete"), color=ERROR),
            bgcolor=SURFACE_2,
            actions=[
                ft.TextButton(content=ft.Text(t("cancel")), on_click=lambda e: page.close(confirm_dialog)),
                ft.ElevatedButton(content=ft.Text(t("delete"), color=TEXT_PRIMARY), bgcolor=ERROR,
                                  color=TEXT_PRIMARY, on_click=confirm_delete),
            ],
        )
        page.open(confirm_dialog)

    def on_edit_stats(e):
        d = detail[0]
        players = d["players"]
        if not players:
            show_snack("No hay jugadores en este partido", WARNING)
            return

        # Construir formulario de estadísticas
        stat_rows = []
        for p in players:
            goals_field = ft.TextField(
                value=str(p["goals"]), width=55, keyboard_type=ft.KeyboardType.NUMBER,
                text_align=ft.TextAlign.CENTER, color=TEXT_PRIMARY,
                border_color=PRIMARY_LIGHT,
            )
            assists_field = ft.TextField(
                value=str(p["assists"]), width=55, keyboard_type=ft.KeyboardType.NUMBER,
                text_align=ft.TextAlign.CENTER, color=TEXT_PRIMARY,
                border_color=PRIMARY_LIGHT,
            )
            yc_field = ft.TextField(
                value=str(p["yellow_cards"]), width=55, keyboard_type=ft.KeyboardType.NUMBER,
                text_align=ft.TextAlign.CENTER, color=TEXT_PRIMARY,
                border_color=PRIMARY_LIGHT,
            )
            mvp_check = ft.Checkbox(value=p["is_mvp"], fill_color=ACCENT)
            stat_rows.append({
                "mp_id": p["mp_id"],
                "name": p["player_name"],
                "goals": goals_field,
                "assists": assists_field,
                "yellow_cards": yc_field,
                "is_mvp": mvp_check,
            })

        def save_stats(e):
            stats_data = [{
                "mp_id": r["mp_id"],
                "goals": r["goals"].value or 0,
                "assists": r["assists"].value or 0,
                "yellow_cards": r["yellow_cards"].value or 0,
                "red_cards": 0,
                "is_mvp": r["is_mvp"].value,
            } for r in stat_rows]
            save_match_stats(match_id, stats_data)
            page.close(stats_dialog)
            show_snack("Estadísticas guardadas ✅")
            refresh()

        stats_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Jugador", size=12, color=TEXT_SECONDARY, width=120),
                        ft.Text("⚽", size=12, color=TEXT_SECONDARY, width=55),
                        ft.Text("🅰️", size=12, color=TEXT_SECONDARY, width=55),
                        ft.Text("🟨", size=12, color=TEXT_SECONDARY, width=55),
                        ft.Text("MVP", size=12, color=TEXT_SECONDARY, width=40),
                    ],
                    spacing=4,
                ),
                *[
                    ft.Row(
                        [
                            ft.Text(r["name"], size=13, color=TEXT_PRIMARY, width=120,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            r["goals"],
                            r["assists"],
                            r["yellow_cards"],
                            r["is_mvp"],
                        ],
                        spacing=4,
                    )
                    for r in stat_rows
                ],
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=8,
        )

        stats_dialog = ft.AlertDialog(
            title=ft.Text(t("stats"), color=TEXT_PRIMARY),
            bgcolor=SURFACE_2,
            content=ft.Container(content=stats_content, height=320, width=360),
            actions=[
                ft.TextButton(content=ft.Text(t("cancel")), on_click=lambda e: page.close(stats_dialog)),
                ft.ElevatedButton(content=ft.Text(t("save"), color=TEXT_PRIMARY), bgcolor=PRIMARY_LIGHT,
                                  color=TEXT_PRIMARY, on_click=save_stats),
            ],
        )
        page.open(stats_dialog)

    def render():
        d = detail[0]
        if not d:
            return
        content_area.controls.clear()

        is_organizer = current_user and current_user.id == d["organizer_id"]
        type_color = MATCH_TYPE_COLORS.get(d["match_type"], PRIMARY_LIGHT)
        status_color = STATUS_COLORS.get(d["status"], TEXT_SECONDARY)
        date_str = (
            d["match_date"].strftime("%d/%m/%Y %H:%M")
            if isinstance(d["match_date"], datetime) else str(d["match_date"])
        )
        type_labels = {"futsal": t("futsal"), "football7": t("football7"), "football11": t("football11")}
        status_labels = {"pending": t("status_pending"), "in_progress": t("status_in_progress"), "finished": t("status_finished")}

        # ── Info header ──────────────────────────────────────────────────────
        info_card = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(type_labels.get(d["match_type"], ""), size=12,
                                               color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                                bgcolor=type_color, border_radius=20,
                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                            ),
                            ft.Container(expand=True),
                            ft.GestureDetector(
                                content=ft.Container(
                                    content=ft.Text(status_labels.get(d["status"], ""), size=12,
                                                   color=TEXT_PRIMARY),
                                    bgcolor=status_color, border_radius=20,
                                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                ),
                                on_tap=on_change_status if is_organizer else None,
                                mouse_cursor=ft.MouseCursor.CLICK if is_organizer else ft.MouseCursor.BASIC,
                            ),
                        ],
                    ),
                    ft.Text(d["title"], size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ft.Row([
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=TEXT_SECONDARY),
                        ft.Text(date_str, size=13, color=TEXT_SECONDARY),
                    ], spacing=4),
                    ft.Row([
                        ft.Icon(ft.Icons.LOCATION_ON, size=14, color=TEXT_SECONDARY),
                        ft.Text(d["venue"] or "—", size=13, color=TEXT_SECONDARY),
                    ], spacing=4),
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, size=14, color=TEXT_SECONDARY),
                        ft.Text(f"{t('organizer')}: {d['organizer_name']}", size=13, color=TEXT_SECONDARY),
                    ], spacing=4),
                    ft.Divider(color=SURFACE, height=1),
                    ft.Row(
                        [
                            ft.Column([
                                ft.Text(t("players"), size=11, color=TEXT_SECONDARY),
                                ft.Text(f"{d['confirmed_count']}/{d['max_players']}",
                                        size=18, weight=ft.FontWeight.BOLD, color=ACCENT),
                            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.VerticalDivider(color=SURFACE, width=1),
                            ft.Column([
                                ft.Text(t("total_cost"), size=11, color=TEXT_SECONDARY),
                                ft.Text(f"${d['total_cost']:,.0f}",
                                        size=18, weight=ft.FontWeight.BOLD, color=SUCCESS),
                            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ft.VerticalDivider(color=SURFACE, width=1),
                            ft.Column([
                                ft.Text(t("cost_per_player"), size=11, color=TEXT_SECONDARY),
                                ft.Text(f"${d['cost_per_player']:,.0f}",
                                        size=18, weight=ft.FontWeight.BOLD, color=WARNING),
                            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=SURFACE_2, border_radius=12, padding=16,
            margin=ft.Margin.only(bottom=12),
        )

        # ── Lista de jugadores / pagos ─────────────────────────────────────
        players_section = ft.Column(spacing=6)
        for p in d["players"]:
            mp_id = p["mp_id"]
            cur_status = p["payment_status"]
            players_section.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.CircleAvatar(
                                content=ft.Text(p["player_name"][0].upper(), color=TEXT_PRIMARY, size=14),
                                bgcolor=PRIMARY,
                                radius=18,
                            ),
                            ft.Column(
                                [
                                    ft.Text(p["player_name"], size=14, color=TEXT_PRIMARY,
                                            weight=ft.FontWeight.W_500),
                                    ft.Text(p["player_position"], size=11, color=TEXT_SECONDARY),
                                ],
                                spacing=2, expand=True,
                            ),
                            ft.Column(
                                [
                                    ft.Text(f"⚽{p['goals']} 🅰️{p['assists']}", size=11, color=TEXT_SECONDARY),
                                    ft.Text("⭐ MVP" if p["is_mvp"] else "", size=11, color=ACCENT),
                                ],
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                            _payment_chip(
                                cur_status,
                                on_change=(lambda mid=mp_id, cs=cur_status: lambda e: cycle_payment(mid, cs))()
                                if is_organizer else None,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10,
                    ),
                    bgcolor=SURFACE_2, border_radius=10, padding=12,
                )
            )

        players_card = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(t("players"), size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.PERSON_ADD,
                                icon_color=ACCENT,
                                tooltip=t("add_player"),
                                on_click=on_add_player,
                                visible=is_organizer,
                            ) if is_organizer else ft.Container(),
                        ],
                    ),
                    players_section,
                ],
                spacing=8,
            ),
            bgcolor=SURFACE, border_radius=12, padding=12,
            margin=ft.Margin.only(bottom=12),
        )

        # ── Acciones del organizador ──────────────────────────────────────
        organizer_actions = ft.Row(
            [
                ft.ElevatedButton(
                    content=ft.Text(t("stats"), color=TEXT_PRIMARY),
                    icon=ft.Icons.BAR_CHART,
                    bgcolor=PRIMARY,
                    color=TEXT_PRIMARY,
                    on_click=on_edit_stats,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                ),
                ft.OutlinedButton(
                    content=ft.Text(t("delete"), color=ERROR),
                    icon=ft.Icons.DELETE,
                    style=ft.ButtonStyle(
                        color=ERROR,
                        side=ft.BorderSide(1, ERROR),
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=on_delete,
                ),
            ],
            spacing=12,
            visible=is_organizer,
        )

        content_area.controls.extend([
            info_card,
            players_card,
            organizer_actions,
        ])
        page.update()

    render()

    return ft.Column(
        [
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=TEXT_PRIMARY,
                            on_click=lambda e: on_back(),
                        ),
                        ft.Text(t("match_detail"), size=20,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                    spacing=8,
                ),
                bgcolor=SURFACE_2,
                padding=ft.Padding.symmetric(horizontal=8, vertical=8),
            ),
            ft.Container(
                content=content_area,
                padding=ft.Padding.all(12),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
