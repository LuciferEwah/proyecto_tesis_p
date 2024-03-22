import flet as ft
from widgets.button_login import EnterButton
from widgets.form_login import FromLogin
from widgets.utils import mostrar_mensaje

class Admin(ft.UserControl):
    def __init__(self, bd, mostrar_mensaje_func = None):
        super().__init__()
        self.database = bd
        self.mostrar_mensaje = mostrar_mensaje_func

    async def on_login_button_click(self, e):
        username = self.username_field.text_field.value
        password = self.password_field.text_field.value

        # Aquí agregas el usuario usando la función add_usuario
        await self.database.add_user(username, password)
        await self.mostrar_mensaje(self.page, "usuario agregado")
        # Código para regresar a la pantalla anterior
        if len(self.page.views) > 1:
            self.page.views.pop()
            top_view = self.page.views[-1]
            self.page.title = top_view.route
            await self.page.go_async(top_view.route)

    async def on_back_button_click(self, e):

        if len(self.page.views) > 1:
            self.page.views.pop()
            top_view = self.page.views[-1]
            self.page.title = top_view.route
            await self.page.go_async(top_view.route)

    def build(self):
        self.username_field = FromLogin(
            ft.icons.PERSON_PIN_CIRCLE_OUTLINED, "Usuario a agregar", False, False)
        self.password_field = FromLogin(
            ft.icons.LOCK_OPEN_OUTLINED, "Contraseña a agregar", True, True)
        # Definimos la instancia de un botón con la funcion para validar el formulario
        
        # Creas el botón para añadir usuario
        add_user_button = EnterButton("AÑADIR USUARIO", self.on_login_button_click)

        # Creas el botón para regresar
        back_button = EnterButton("REGRESAR", self.on_back_button_click)

        # Agrega los botones a tu interfaz, posiblemente en una fila
        buttons_row = ft.Column(
            controls=[
                add_user_button,
                back_button
            ],
            spacing=10  # Espaciado entre los botones
        )
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
                                ft.Text("ADMIN", size=32,
                                        weight="bold", color=ft.colors.WHITE),
                                ft.Text("ADMIN",
                                        size=15, weight='bold', color=ft.colors.WHITE)
                            ]
                        ),
                        ft.Divider(height=20, color="transparent"),
                        self.username_field,
                        self.password_field,
                        ft.Divider(height=20, color="transparent"),
                        buttons_row,  # Este es el botóm
                    ]
                )
            )
        )
