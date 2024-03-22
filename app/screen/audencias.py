import flet as ft
from widgets.table_widget import TablaWidget
import asyncio


class ScreenFormsAudencias(ft.UserControl):
    def __init__(self, route_change_handler, nav_rail_class, db, page, id_causa, on_preparatory_hearin_selected_callback, on_trial_hearing_selected_callback):
        super().__init__()  # Llamada al constructor de la clase base
        self.route_change_handler = route_change_handler
        self.nav_rail_class = nav_rail_class
        self.database = db
        self.page = page
        self.id_causa = id_causa
        self.on_preparatory_hearin_selected_callback = on_preparatory_hearin_selected_callback
        self.on_trial_hearing_selected_callback = on_trial_hearing_selected_callback

    def build(self):
        rail = self.nav_rail_class.create_rail()
        division = ft.Container(width=1280,
                                content=ft.Divider(height=1, color="white"))

        self.tabla_preparatory_hearing = TablaWidget(
            [], [], self.on_row_preparatory_hearing, "Resumen de la audencia preparatoria",
            "Agregar nueva audencia prepratoria", False if self.id_causa else True,
            disabled=False if self.id_causa else True, fixed_width=None
        )

        self.tabla_trial_hearing = TablaWidget(
            [], [], self.on_row_trial_hearing, "Resumen de la audencia del juicio",
            "Agregar nueva audencia de jucio", False if self.id_causa else True,
            disabled=False if self.id_causa else True, fixed_width=None
)
        asyncio.create_task(self.initialize_async_data())

        return ft.Row(
            [
                rail,

                ft.Column(
                    [self.tabla_preparatory_hearing, division, self.tabla_trial_hearing], alignment=ft.MainAxisAlignment.START),
            ],

            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    async def get_preparatory_hearing(self):
        preparatory_hearing_columns = ["id_audiencia_preparatoria", "fecha_citacion",
                                       "fecha_realizacion", "suspension_anterior",
                                       "resolucion", "salida_colaborativa"]
        data = await self.database.get_audiencia_preparatoria_by_causa(preparatory_hearing_columns,  self.id_causa)
        return (data, preparatory_hearing_columns)

    async def get_trial_hearing(self):
        trial_hearing_columns = ["id_audiencia_juicio", "fecha_citacion", "fecha_realizacion",
                                 "cambio_composicion_hogar", "suspendido",
                                 "resolucion", "sentencia", "abre_causa_cumplimiento"]
        data = await self.database.get_audiencia_juicio_by_causa(trial_hearing_columns,  self.id_causa)
        return (data, trial_hearing_columns)

    async def initialize_async_data(self):
        data_preparatory_hearing, columns_preparatory_hearing = await self.get_preparatory_hearing()
        data_trial_hearing, columns_trial_hearing = await self.get_trial_hearing()

        await self.tabla_preparatory_hearing.update_table(data_preparatory_hearing, columns_preparatory_hearing)
        await self.tabla_trial_hearing.update_table(data_trial_hearing, columns_trial_hearing)

    async def on_row_preparatory_hearing(self, selected_id):
        preparatory_hearing_data = await self.database.get_audiencia_preparatoria_by_id(selected_id)
        preparatory_hearing_info = (selected_id, preparatory_hearing_data)
        await self.on_preparatory_hearin_selected_callback(preparatory_hearing_info)
        await self.page.go_async('/AudenciaPreparatoria')

    async def on_row_trial_hearing(self, selected_id):
        trial_hearing_data = await self.database.get_audiencia_juicio_by_id(selected_id)
        trial_hearing_info = (selected_id, trial_hearing_data)
        await self.on_trial_hearing_selected_callback(trial_hearing_info)
        await self.page.go_async('/AudienciaJuicioAntecedentes')
