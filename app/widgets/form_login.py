import flet as ft


class FromLogin(ft.UserControl):
    def __init__(self, icon_name, text_hint, hide,reveal):
        self.icon_name = icon_name
        self.text_hint = text_hint
        self.hide = hide
        self.reveal = reveal
        super().__init__()

    def build(self):
        self.text_field = ft.TextField(
            border_color='transparent',
            bgcolor='transparent',
            height=20,
            width=200,
            text_size=12,
            content_padding=3,
            cursor_color='white',
            hint_text=self.text_hint,
            hint_style=ft.TextStyle(size=11, color=ft.colors.WHITE),
            password=self.hide,
            on_change=None,
            on_blur=None,
            can_reveal_password= self.reveal
        )
        return ft.Container(
            width=320,
            height=40,
            border=ft.border.only(bottom=ft.border.BorderSide(0.5, "white54")),
            content=ft.Row(
                spacing=20,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        name=self.icon_name,
                        size=20,
                        opacity=0.85,
                        color= ft.colors.WHITE
                    ),
                    self.text_field
                ]
            )
        )
