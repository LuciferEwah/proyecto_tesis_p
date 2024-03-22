import flet as ft

class NavigationRailClass:
    def __init__(self, route_change_handler, destinations, page, selected_index=0, show_trailing=False):
        self.route_change_handler = route_change_handler
        self.destinations = destinations
        self.page = page
        self.selected_index = selected_index
        self.show_trailing = show_trailing

    async def on_change(self, event):
        index = event.control.selected_index
        if 0 <= index < len(self.destinations):
            selected_route = self.destinations[index]["route"]
            current_route = self.page.views[-1].route if self.page.views else None

            if selected_route != current_route:
                if len(self.page.views) > 1:
                    self.page.views.pop()
                else:
                    pass
                    #print(f"No se elimina ninguna vista. Manteniendo {selected_route}.")
                await self.route_change_handler(selected_route)
            else:
                pass
                #print("La ruta seleccionada es la misma que la ruta actual. No se realiza ninguna acción.")
        else:
            pass
            #print(f"Índice fuera de rango: {index}")

    def set_selected_index(self, index):
        self.selected_index = index

    async def on_trailing_click(self, event):
        self.page.views.clear()
        await self.page.go_async('/PaginaPrincipal')
    


    def create_rail(self):
        rail_destinations = []
        for i, destination in enumerate(self.destinations):
            rail_destinations.append(
                ft.NavigationRailDestination(
                    icon=destination["icon"],
                    selected_icon=destination.get("selected_icon", destination["icon"]),
                    label=destination.get("label", ""),
                )
            )
        
        trailing_button = None
        if self.show_trailing:
            trailing_button = ft.FloatingActionButton(icon=ft.icons.HOME, tooltip="Regresar a la pagina principal", bgcolor=ft.colors.DEEP_PURPLE_500, on_click=self.on_trailing_click)

        rail = ft.NavigationRail(
            width=180,
            selected_index=self.selected_index,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            height=380,
            destinations=rail_destinations,
            on_change=self.on_change,
            trailing=trailing_button,
        )
        return rail
