import flet as ft
import asyncio


class PopButton(ft.UserControl):
    def __init__(self, page, special_route=None):
        super().__init__()
        self.page = page
        self.special_route = special_route  # Ruta especial opcional

    def build(self):
        return ft.IconButton(
            icon=ft.icons.ARROW_BACK_IOS_NEW,
            on_click=self.view_pop
        )

    async def view_pop(self, event):

        if len(self.page.views) > 1:
            self.page.views.pop()
            top_view = self.page.views[-1]
            self.page.title = top_view.route
            await self.page.go_async(top_view.route)

        else:

            print("No hay más vistas en la pila para volver.")
