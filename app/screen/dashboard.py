# Importaciones
import flet as ft
from widgets.table_widget import TablaWidget
import asyncio
from widgets.kpi import DataCardWidget


class DashboardScreen(ft.UserControl):
    def __init__(self, db, route_change_handler, nav_rail_class, on_causa_selected_callback, page):
        super().__init__()
        self.database = db
        self.route_change_handler = route_change_handler
        self.nav_rail_class = nav_rail_class
        self.selected_id = None
        self.on_causa_selected_callback = on_causa_selected_callback
        self.page = page
        self.pagina_actual_de_tabla_causa = 1

    async def on_row_selected(self, selected_id):
        causa_data = await self.database.get_causa_by_id(selected_id)
        causa_info = (selected_id, causa_data)
        self.on_causa_selected_callback(causa_info)
        await self.page.go_async('/formulario_causa')

    def build(self):
        rail = self.nav_rail_class.create_rail()

        
        next_page_button = ft.IconButton(tooltip="Pagina Siguiente", on_click=lambda _: self.next_page(),icon_color=ft.colors.DEEP_PURPLE_500, icon=ft.icons.KEYBOARD_ARROW_RIGHT,icon_size=40)
        prev_page_button = ft.IconButton(tooltip="Pagina Anterior", on_click=lambda _: self.previous_page(),icon_color=ft.colors.DEEP_PURPLE_500, icon=ft.icons.KEYBOARD_ARROW_LEFT_OUTLINED,icon_size=40)
        inicio_page_button = ft.IconButton(tooltip="Ir al inicio", on_click=lambda _: self.go_to_first_page(), icon_color=ft.colors.DEEP_PURPLE_500, icon=ft.icons.KEYBOARD_DOUBLE_ARROW_LEFT,icon_size=40)
        final_page_button = ft.IconButton(tooltip="Ir al final", on_click=lambda _: self.go_to_last_page(), icon_color=ft.colors.DEEP_PURPLE_500, icon=ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT_OUTLINED,icon_size=40)


        contenedor_paginacion = ft.Card(content=ft.Row(controls=[inicio_page_button,prev_page_button, next_page_button,final_page_button],spacing=30,alignment = ft.MainAxisAlignment.SPACE_AROUND),width=250,height=70,elevation=15)
        self.tabla_widget = TablaWidget(
            [], [], self.on_row_selected, "Resumen de las Causa","Agregar nueva causa",self.database, boton_extra= contenedor_paginacion)
        
        self.data_card = DataCardWidget(
            self.page, "Total de Causas")
        self.total_victimas_data_card = DataCardWidget(
            self.page, "Total de Víctimas")
        self.total_adult_seniors_data_card = DataCardWidget(
            self.page, "Porcentaje de Adultos Mayores Víctimas", is_percentage=True)

        self.average_age_data_card = DataCardWidget(
            self.page, "Estadísticas de Denunciados")
        self.total_denounced_data_card = DataCardWidget(
            self.page, "Total de Denunciados")

        asyncio.create_task(self.initialize_async_data())

        return ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                rail,
                ft.VerticalDivider(width=2, visible=True),
                ft.Column(
                    controls=[self.tabla_widget],
                    alignment=ft.MainAxisAlignment.START,
                ), ft.Column(controls=[ft.Row(controls=[self.data_card, self.total_victimas_data_card]),
                                       self.total_adult_seniors_data_card, self.average_age_data_card, self.total_denounced_data_card])
            ],

        )


    async def get_total_causes(self):
        # Suponiendo que la función 'get_all_causas' devuelve todas las causas
        total_causes = await self.database.get_total_causas()
        return total_causes

    async def get_total_victims(self):
        total_victims = await self.database.get_total_victimas()
        return total_victims

    async def get_total_adult_seniors_victims(self):
        total_adults = await self.database.get_porcentaje_adultos_mayores_victimas()
        return total_adults

    async def get_age_stats_denounced(self):
        average_age = await self.database.get_promedio_edad_denunciados()
        total_denounced = await self.database.get_cantidad_denunciados()
        des = await self.database.get_desviacion_estandar_edad_denunciados()
        
        return {
            'Promedio de edad': average_age,
            'cantidad de denunciados validos': total_denounced,
            'Desviación Estándar de la Edad (años)': des
        }


    async def get_total_denunciados(self):
        total_denounced = await self.database.get_total_denunciados()
        return total_denounced

    async def initialize_async_data(self):
        # Obtener los datos de la tabla y actualizar la tabla
        data, columns = await self.get_cause()
        await self.tabla_widget.update_table(data, columns)
        # Obtener el total de causas y actualizar el DataCardWidget
        total_causes = await self.get_total_causes()  # Obtiene el total de causas
        await self.data_card.update_data(total_causes)

        total_victims = await self.get_total_victims()
        await self.total_victimas_data_card.update_data(total_victims)

        total_adults = await self.get_total_adult_seniors_victims()
        await self.total_adult_seniors_data_card.update_data(total_adults)

            # Para el widget de edad promedio que necesita múltiples valores
        average_age_stats = await self.get_age_stats_denounced()
        await self.average_age_data_card.update_data(average_age_stats)

        total_denounced = await self.get_total_denunciados()
        await self.total_denounced_data_card.update_data(total_denounced)

    #async def delayed_initialize(self):
        # Espera un segundo (o el tiempo que consideres necesario) esto es solo necesario si esta en web
        #await asyncio.sleep(3)
        #await self.initialize_async_data()


    def next_page(self):
        if self.pagina_actual_de_tabla_causa < self.tabla_widget.total_pages:
            self.pagina_actual_de_tabla_causa += 1
            asyncio.create_task(self.initialize_async_data())

    def previous_page(self):
        if self.pagina_actual_de_tabla_causa > 1:
            self.pagina_actual_de_tabla_causa -= 1
            asyncio.create_task(self.initialize_async_data())

    def go_to_first_page(self):
        self.pagina_actual_de_tabla_causa = 1
        asyncio.create_task(self.initialize_async_data())

    def go_to_last_page(self):
        self.pagina_actual_de_tabla_causa = self.tabla_widget.total_pages
        asyncio.create_task(self.initialize_async_data())

    async def get_cause(self):
        await self.tabla_widget.calcular_total_paginas()
        causa_columns = ["ID_Causa", "Rol_rit", "estado_admin", "etapa",
                         "via_ingreso", "causa_proteccion_abierta", "causa_penal_abierta"]
        data = await self.database.get_causas_by_columns_new(causa_columns, self.pagina_actual_de_tabla_causa)
        return (data, causa_columns)