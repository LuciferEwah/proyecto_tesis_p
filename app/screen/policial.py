import flet as ft
from widgets.table_widget import TablaWidget
import asyncio


class ScreenInformacionPolicial(ft.UserControl):
    def __init__(self, route_change_handler, nav_rail_class, db, page, id_causa, on_policia_report_selected_callback=None, mostrar_mensaje_func=None):
        super().__init__()  # Llamada al constructor de la clase base
        self.route_change_handler = route_change_handler
        self.nav_rail_class = nav_rail_class
        self.database = db
        self.page = page
        self.id_causa = id_causa
        self.on_policia_report_selected_callback = on_policia_report_selected_callback
        self.mostrar_mensaje = mostrar_mensaje_func

    def build(self):
        rail = self.nav_rail_class.create_rail()
        
        self.tabla_policia_report = TablaWidget(
            [], [], self.on_row_policia_report, "Reportes de la Policía",
            "Agregar nuevo reporte policial", False if self.id_causa else True,
            disabled=False if self.id_causa else True, fixed_width=None
        )


        asyncio.create_task(self.initialize_async_data())

        return ft.Row(
            [
                rail,
                ft.Column(
                    [self.tabla_policia_report], alignment=ft.MainAxisAlignment.START),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    async def get_policia_reports(self):
        policia_report_columns = [
            "id_antecedentes_delito", "codigo_delito", "fecha_delito", "hora_delito", "comuna", "lugar_ocurrencia"]
        data = await self.database.get_antecedentes_delito_by_causa(policia_report_columns, self.id_causa)
        return (data, policia_report_columns)

    async def initialize_async_data(self):
        data_policia_report, columns_policia_report = await self.get_policia_reports()
        await self.tabla_policia_report.update_table(data_policia_report, columns_policia_report)

    async def on_row_policia_report(self, selected_id):
        policia_report_data = await self.database.get_antecedente_delito_by_id(selected_id)
        policia_report_info = (selected_id, policia_report_data)
        await self.on_policia_report_selected_callback(policia_report_info)
        await self.page.go_async('/AntecedentesPoliciales')
