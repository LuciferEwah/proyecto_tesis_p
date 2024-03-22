import flet as ft


class EnterButton(ft.UserControl):
    def __init__(self, btn_name, on_click_function):
        self.btn_name = btn_name
        self.on_click_function = on_click_function
        super().__init__()

    def build(self):
        return ft.ElevatedButton(
            content=ft.Text(
                self.btn_name,
                size=13,
                weight="bold"
            ),
            height=32,
            width=320,
            style=ft.ButtonStyle(
                shape={
                    "": ft.RoundedRectangleBorder(radius=8)
                },
                color={
                    "": "white",
                },
                bgcolor={"": "#00304E"}
            ),
            on_click=self.on_click_function
        )
