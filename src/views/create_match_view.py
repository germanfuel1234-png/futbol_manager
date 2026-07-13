"""
Vista de creación de partido.
"""
import flet as ft
from datetime import datetime
from src.utils import (
    t, PRIMARY, PRIMARY_LIGHT, SURFACE_2, ACCENT,
    TEXT_PRIMARY, TEXT_SECONDARY, ERROR, SUCCESS,
)
from src.services import create_match


def build_create_match_view(page: ft.Page, on_created, on_back):
    lbl_error = ft.Text("", color=ERROR, size=13, visible=False)
    lbl_success = ft.Text("", color=SUCCESS, size=13, visible=False)

    txt_title = ft.TextField(
        label=t("match_type") + " / " + t("title") if True else "",
        hint_text="Ej: Partido del domingo",
        prefix_icon=ft.Icons.SPORTS_SOCCER,
        border_color=PRIMARY_LIGHT,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
    )
    txt_title.label = "Título del partido"

    dd_type = ft.Dropdown(
        label=t("match_type"),
        options=[
            ft.dropdown.Option("futsal", t("futsal")),
            ft.dropdown.Option("football7", t("football7")),
            ft.dropdown.Option("football11", t("football11")),
        ],
        value="futsal",
        border_color=PRIMARY_LIGHT,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
    )

    # Fecha y hora con DatePicker y TimePicker
    selected_date = [datetime.now()]
    selected_time = [datetime.now()]

    lbl_date = ft.Text(
        selected_date[0].strftime("%d/%m/%Y"),
        color=TEXT_PRIMARY, size=14,
    )
    lbl_time = ft.Text(
        selected_date[0].strftime("%H:%M"),
        color=TEXT_PRIMARY, size=14,
    )

    def handle_date_change(e):
        if e.control.value:
            selected_date[0] = e.control.value
            lbl_date.value = selected_date[0].strftime("%d/%m/%Y")
            page.update()

    def handle_time_change(e):
        if e.control.value:
            t_val = e.control.value
            selected_time[0] = datetime.now().replace(hour=t_val.hour, minute=t_val.minute)
            lbl_time.value = f"{t_val.hour:02d}:{t_val.minute:02d}"
            page.update()

    date_picker = ft.DatePicker(on_change=handle_date_change)
    time_picker = ft.TimePicker(on_change=handle_time_change)

    btn_date = ft.OutlinedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ACCENT),
            lbl_date,
        ], spacing=8),
        style=ft.ButtonStyle(side=ft.BorderSide(1, PRIMARY_LIGHT)),
        on_click=lambda e: page.open(date_picker),
    )
    btn_time = ft.OutlinedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.ACCESS_TIME, size=16, color=ACCENT),
            lbl_time,
        ], spacing=8),
        style=ft.ButtonStyle(side=ft.BorderSide(1, PRIMARY_LIGHT)),
        on_click=lambda e: page.open(time_picker),
    )

    txt_venue = ft.TextField(
        label=t("venue"),
        prefix_icon=ft.Icons.LOCATION_ON,
        border_color=PRIMARY_LIGHT,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
    )
    txt_cost = ft.TextField(
        label=t("total_cost"),
        prefix_icon=ft.Icons.ATTACH_MONEY,
        border_color=PRIMARY_LIGHT,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        keyboard_type=ft.KeyboardType.NUMBER,
        value="0",
    )
    txt_notes = ft.TextField(
        label="Notas / Observaciones",
        prefix_icon=ft.Icons.NOTES,
        border_color=PRIMARY_LIGHT,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        multiline=True,
        min_lines=2,
        max_lines=4,
    )

    def on_submit(e):
        lbl_error.visible = False
        lbl_success.visible = False

        if not txt_title.value:
            lbl_error.value = t("field_required")
            lbl_error.visible = True
            page.update()
            return

        match_datetime = selected_date[0].replace(
            hour=selected_time[0].hour,
            minute=selected_time[0].minute,
        )

        try:
            cost = float(txt_cost.value or 0)
        except ValueError:
            lbl_error.value = "Costo inválido"
            lbl_error.visible = True
            page.update()
            return

        ok, result = create_match(
            title=txt_title.value,
            match_type=dd_type.value,
            match_date=match_datetime,
            venue=txt_venue.value,
            total_cost=cost,
            notes=txt_notes.value,
        )
        if ok:
            lbl_success.value = t("match_created")
            lbl_success.visible = True
            page.update()
            # Pequeño delay visual y redirigir al detalle
            import threading
            def redirect():
                import time; time.sleep(0.8)
                on_created(result)
            threading.Thread(target=redirect, daemon=True).start()
        else:
            lbl_error.value = str(result)
            lbl_error.visible = True
            page.update()

    return ft.Column(
        [
            # Header
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=TEXT_PRIMARY,
                            on_click=lambda e: on_back(),
                        ),
                        ft.Text(t("create_match"), size=20,
                                weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                    spacing=8,
                ),
                bgcolor=SURFACE_2,
                padding=ft.Padding.symmetric(horizontal=8, vertical=8),
            ),
            # Formulario
            ft.Container(
                content=ft.Column(
                    [
                        txt_title,
                        dd_type,
                        ft.Text(t("date"), color=TEXT_SECONDARY, size=13),
                        ft.Row([btn_date, btn_time], spacing=12),
                        txt_venue,
                        txt_cost,
                        txt_notes,
                        lbl_error,
                        lbl_success,
                        ft.ElevatedButton(
                            content=ft.Text(t("save"), color=TEXT_PRIMARY),
                            bgcolor=PRIMARY_LIGHT,
                            color=TEXT_PRIMARY,
                            width=320,
                            height=48,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                            on_click=on_submit,
                        ),
                    ],
                    spacing=14,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.Padding.all(16),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
