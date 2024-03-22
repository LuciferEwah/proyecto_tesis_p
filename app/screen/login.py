import flet as ft
from widgets.button_login import EnterButton
from widgets.form_login import FromLogin


class LoginScreen(ft.UserControl):
    def __init__(self, bd):
        super().__init__()
        self.database = bd

    async def on_login_button_click(self, e):
        username = self.username_field.text_field.value
        password = self.password_field.text_field.value

        if username == "liacdd" and password == "admin:derecho":
            await self.page.go_async('/admin')
            return  
        
        es_valido, mensaje = await self.database.user_verification(username, password)
        if es_valido:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(mensaje,
                                                              text_align=ft.TextAlign.CENTER,  # Centra el texto
                                                              size=26,
                                                              weight=ft.FontWeight.BOLD))
            self.page.snack_bar.open = True
            await self.page.go_async('/PaginaPrincipal')
        else:
            self.page.snack_bar = ft.SnackBar(content=ft.Text(mensaje,
                                                              text_align=ft.TextAlign.CENTER,  # Centra el texto
                                                              size=26,
                                                              weight=ft.FontWeight.BOLD))
            self.page.snack_bar.open = True
            await self.page.update_async()

    def build(self):
        self.username_field = FromLogin(
            ft.icons.PERSON_PIN_CIRCLE_OUTLINED, "Usuario", False, False)
        self.password_field = FromLogin(
            ft.icons.LOCK_OPEN_OUTLINED, "Contraseña", True, True)
        # Definimos la instancia de un botón con la funcion para validar el formulario
        login_button = EnterButton("Entrar", self.on_login_button_click)

        return ft.Card(
            width=408,
            height=612,
            elevation=15,
            content=ft.Container(
                bgcolor='#23262a',
                border_radius=6,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Divider(height=40, color='transparent'),
                        ft.Container(
                            content=ft.Image(
                                src=f"/images/logo-aniversario.png",
                                width=300,
                                height=100,
                                fit=ft.ImageFit.FIT_WIDTH
                            )
                        ),
                        ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5,
                            controls=[
                                ft.Text("Ingresa", size=32,
                                        weight="bold", color=ft.colors.WHITE),
                                ft.Text("Universidad Finis terrae",
                                        size=15, weight='bold', color=ft.colors.WHITE)
                            ]
                        ),
                        ft.Divider(height=20, color="transparent"),
                        self.username_field,
                        self.password_field,
                        ft.Divider(height=20, color="transparent"),
                        login_button,  # Este es el botóm
                    ]
                )
            )
        )
