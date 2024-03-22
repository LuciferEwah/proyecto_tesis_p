import flet as ft


class DataCardWidget(ft.UserControl):
    def __init__(self, page, title, is_percentage=False):
        super().__init__()
        self.page = page
        self.title = title
        self.is_percentage = is_percentage
        self.color_title = ft.colors.AMBER_900
        self.weight_title = ft.FontWeight.BOLD
        self.data_text = ft.Text("", size=18)  # Inicializar data_text aquí

    def build(self):
        title_text = ft.Text(self.title, size=18)
        self.data_container = ft.Column(
            controls=[title_text, self.data_text],  # Agregar data_text a los controles
            spacing=10
        )
        return ft.Card(
            expand=False,
            elevation=15,
            content=ft.Container(
                padding=20,
                content=self.data_container
            )
        )
        
    async def update_data(self, new_data):
        if isinstance(new_data, dict):
            self.data_container.controls = [self.data_container.controls[0]]  # Mantener solo el título
            for key, value in new_data.items():
                is_percentage = isinstance(value, float) and "porcentaje" in key.lower()
                formatted_value = f"{value:.2f}%" if is_percentage else str(value)
                data_text = ft.Text(f"{key}: {formatted_value}", size=14)
                self.data_container.controls.append(data_text)
        else:
            formatted_data = f"{new_data:.2f}%" if self.is_percentage else str(new_data)
            self.data_text.value = formatted_data  # Actualizar data_text
            self.data_container.controls = [self.data_container.controls[0], self.data_text]  # Mantener el título y data_text
        await self.data_container.update_async()
