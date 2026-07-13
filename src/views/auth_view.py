"""
Vista de Login y Registro de usuarios.
"""
import flet as ft
from src.utils import (
    t, PRIMARY, PRIMARY_LIGHT, SURFACE, SURFACE_2,
    TEXT_PRIMARY, TEXT_SECONDARY, ERROR, ACCENT,
)
from src.services import login_user, register_user
from src.models import PlayerPosition


def build_auth_view(page: ft.Page, on_login_success):
    """
    Retorna el contenido de la pantalla de autenticación.
    on_login_success: callback llamado cuando el login es exitoso.
    """
    is_login_mode = [True]

    # ─── Campos ──────────────────────────────────────────────────────────────
    txt_name = ft.TextField(
        label=t("name"),
        prefix_icon=ft.Icons.PERSON,
        border_color=PRIMARY_LIGHT,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        visible=False,
    )
    txt_phone = ft.TextField(
        label=t("phone"),
        prefix_icon=ft.Icons.PHONE,
        border_color=PRIMARY_LIGHT,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        keyboard_type=ft.KeyboardType.PHONE,
        visible=False,
    )
    dd_position = ft.Dropdown(
        label=t("position"),
        options=[ft.dropdown.Option(p.value) for p in PlayerPosition],
        border_color=PRIMARY_LIGHT,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        value=PlayerPosition.ANY.value,
        visible=False,
    )
    txt_email = ft.TextField(
        label=t("email"),
        prefix_icon=ft.Icons.EMAIL,
        border_color=PRIMARY_LIGHT,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    txt_password = ft.TextField(
        label=t("password"),
        prefix_icon=ft.Icons.LOCK,
        border_color=PRIMARY_LIGHT,
        focused_border_color=ACCENT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        password=True,
        can_reveal_password=True,
    )
    lbl_error = ft.Text("", color=ERROR, size=13, visible=False)
    submit_label = ft.Text(t("login"), color=TEXT_PRIMARY)
    btn_submit = ft.ElevatedButton(
        content=submit_label,
        bgcolor=PRIMARY_LIGHT,
        color=TEXT_PRIMARY,
        width=320,
        height=48,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
    )
    lbl_toggle = ft.Text(t("no_account"), color=TEXT_SECONDARY, size=13)
    toggle_label = ft.Text(t("register"), color=ACCENT)
    btn_toggle = ft.TextButton(content=toggle_label, style=ft.ButtonStyle(color=ACCENT))

    def show_error(key: str):
        lbl_error.value = t(key)
        lbl_error.visible = True
        page.update()

    def clear_error():
        lbl_error.value = ""
        lbl_error.visible = False

    def toggle_mode(e):
        clear_error()
        is_login_mode[0] = not is_login_mode[0]
        login = is_login_mode[0]

        txt_name.visible = not login
        txt_phone.visible = not login
        dd_position.visible = not login

        submit_label.value = t("login") if login else t("register")
        lbl_toggle.value = t("no_account") if login else t("have_account")
        toggle_label.value = t("register") if login else t("login")
        page.update()

    def on_submit(e):
        clear_error()
        if is_login_mode[0]:
            ok, msg = login_user(txt_email.value, txt_password.value)
            if ok:
                on_login_success()
            else:
                show_error(msg)
        else:
            ok, msg = register_user(
                name=txt_name.value,
                email=txt_email.value,
                password=txt_password.value,
                phone=txt_phone.value,
                position=dd_position.value or PlayerPosition.ANY.value,
            )
            if ok:
                on_login_success()
            else:
                show_error(msg)

    btn_submit.on_click = on_submit
    btn_toggle.on_click = toggle_mode

    # ─── Layout ───────────────────────────────────────────────────────────────
    logo = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.SPORTS_SOCCER, size=64, color=ACCENT),
                ft.Text(
                    t("app_name"),
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        margin=ft.Margin.only(bottom=32),
    )

    form = ft.Container(
        content=ft.Column(
            [
                logo,
                txt_name,
                txt_phone,
                dd_position,
                txt_email,
                txt_password,
                lbl_error,
                btn_submit,
                ft.Row(
                    [lbl_toggle, btn_toggle],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=24, vertical=40),
        bgcolor=SURFACE_2,
        border_radius=16,
        width=380,
    )

    return ft.Column(
        [form],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )
