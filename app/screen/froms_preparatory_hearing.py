import flet as ft
from models.audencia_preparatoria import AudienciaPreparatoria
from widgets.dialog import ConfirmationDialog
from widgets.from_card_widget import FormCardWidget
from widgets.table_widget import TablaWidget
import asyncio


class ScreenFormsAudienciaPreparatoria(ft.UserControl):
    def __init__(self, db, page, data, on_home_preparatory_hearing_involved_selected_callback, on_medida_cautelar_selected_callback, id_causa=None, update_tabla_audiencia_callback=None, mostrar_mensaje_func=None):
        super().__init__()
        self.database = db
        self.data = data if data else []
        self.page = page
        self.text_fields = {}
        self.id_causa = id_causa
        self.on_medida_cautelar_selected_callback = on_medida_cautelar_selected_callback
        self.on_home_preparatory_hearing_involved_selected_callback = on_home_preparatory_hearing_involved_selected_callback
        self.update_tabla_audiencia_callback = update_tabla_audiencia_callback
        self.mostrar_mensaje = mostrar_mensaje_func
        if not data:
            self.limpiar_formulario()

    def limpiar_formulario(self):
        for key in self.text_fields:
            self.text_fields[key].value = ""

    def build(self):
        self.confirm_dialog = ConfirmationDialog(
            self.page,
            "Actualizar",
            "¿Estás seguro(a) que quieres Actualizar los datos?",
            self.some_confirm_action
        )
        self.delete_dialog = ConfirmationDialog(
            self.page,
            "Eliminar",
            "¿Estás seguro(a) que quieres Eliminar los datos?",
            self.some_delete_action
        )

        self.audiencia_button_update = ft.OutlinedButton(
            "Guardar Audiencia" if self.data else "Guardar Nueva Audiencia",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_causa_button_click
        )

        self.audiencia_button_delete = ft.OutlinedButton(
            "Eliminar Audiencia",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_causa_button_click,
            disabled=False if self.data else True
        )

        self.tabla_audencia_preparatoria_involucrados = TablaWidget(
            [], [], self.on_row_on_row_preparatory_hearing_involved, "Resumen involucrados en audencia preparatoria", "Agregar nuevos involucrados", False if self.data else True,disabled= False if self.data else True, fixed_width=None)
        self.tabla_medidas_cautelares = TablaWidget(
            [], [], self.on_row_selected_medida_cautelar, "Resumen de medidas cautelares en audiencia preparatoria", "Agregar nueva medida cautelar", False if self.data else True,disabled= False if self.data else True, fixed_width=None)
        asyncio.create_task(self.initialize_async_data())

        audiencia_section = FormCardWidget(
            title="Detalles de la Audiencia Preparatoria",
            field_groups=self._audiencia_fields(),
            buttons=[self.audiencia_button_update,
                     self.audiencia_button_delete],
            text_fields=self.text_fields,
            page=self.page
        ).build()

        division = ft.Container(width=1280,
                                content=ft.Divider(height=1, color="white"))

        return ft.Container(
            expand=False,
            padding=20,
            content=ft.Column(controls=[audiencia_section, division,
                                        self.tabla_audencia_preparatoria_involucrados, division,
                                        self.tabla_medidas_cautelares],
                              spacing=20)
        )

    def _audiencia_fields(self):
        fields = [
            {"type": "text",
            "label": "Fecha Citación",
            "value": self._get_data_value(2)},
            {"type": "text",
            "label": "Fecha Realización",
            "value": self._get_data_value(3)},
            {"type": "dropdown",
            "label": "Suspensión Anterior",
            "options": ["Sí", "No", "No aplica", "Sin información"],
            "value": self._get_data_value(4)},
            {"type": "dropdown",
            "label": "Solicita Informes/Oficios",
            "options": ["Sí", "No", "No aplica", "Sin información"],
            "value": self._get_data_value(5)},
            {"type": "dropdown",
            "label": "Resolución",
            "options": ["Salida Colaborativa", "Rechazo Acoger la Tramitación", "Tribunal se Declara Incompetente", "Citar Audiencia de Juicio", "Archivo del procedimiento", "Abandono del procedimiento", "Suspensión de la sentencia", "No aplica", "Sin información"],
            "value": self._get_data_value(6)},
            {"type": "text",
            "label": "Salida Colaborativa",
            "value": self._get_data_value(7)},
            {"type": "text",
            "label": "Otras Observaciones",
            "value": self._get_data_value(8)},
            {"type": "text",
            "label": "Informes solicitados a quien",
            "value": self._get_data_value(9)},
            {"type": "text",
            "label": "Informes entregados",
            "value": self._get_data_value(10)},
            {"type": "text",
            "label": "Informes entregados cuales",
            "value": self._get_data_value(11)},
            {"type": "text",
            "label": "Informes pendientes",
            "value": self._get_data_value(12)},
            {"type": "text",
            "label": "Demora entrega informes",
            "value": self._get_data_value(13)},
            {"type": "text",
            "label": "Pericia solicitada",
            "value": self._get_data_value(14)},
            {"type": "text",
            "label": "Pericia cual",
            "value": self._get_data_value(15)},
            {"type": "text",
            "label": "Pericia solicitante",
            "value": self._get_data_value(16)},
        ]
        return fields

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def some_confirm_action(self):
        try:
            id_audiencia = self._get_data_value(0)
            id_causa = self.id_causa
            fecha_citacion = self.text_fields["Fecha Citación"].value
            fecha_realizacion = self.text_fields["Fecha Realización"].value
            suspension_anterior = self.text_fields["Suspensión Anterior"].value
            solicita_informes = self.text_fields["Solicita Informes/Oficios"].value
            resolucion = self.text_fields["Resolución"].value
            salida_colaborativa = self.text_fields["Salida Colaborativa"].value
            otras_observaciones = self.text_fields["Otras Observaciones"].value
            informes_solicitados_a_quien = self.text_fields["Informes solicitados a quien"].value
            informes_entregados = self.text_fields["Informes entregados"].value
            informes_entregados_cuales = self.text_fields["Informes entregados cuales"].value
            informes_pendientes = self.text_fields["Informes pendientes"].value 
            demora_entrega_informes = self.text_fields["Demora entrega informes"].value
            pericia_solicitada = self.text_fields["Pericia solicitada"].value
            pericia_cual = self.text_fields["Pericia cual"].value
            pericia_solicitante = self.text_fields["Pericia solicitante"].value
            audienciaPreparatoria = AudienciaPreparatoria(
                id_causa=id_causa,
                fecha_citacion=fecha_citacion,
                fecha_realizacion=fecha_realizacion,
                suspension_anterior=suspension_anterior,
                solicita_informes_oficios=solicita_informes,
                resolucion=resolucion,
                salida_colaborativa=salida_colaborativa,
                otras_observaciones=otras_observaciones,
                informes_solicitados_a_quien=informes_solicitados_a_quien,
                informes_entregados=informes_entregados,
                informes_entregados_cuales=informes_entregados_cuales,
                informes_pendientes = informes_pendientes,
                demora_entrega_informes=demora_entrega_informes,
                pericia_solicitada=pericia_solicitada,
                pericia_cual=pericia_cual,
                pericia_solicitante=pericia_solicitante
            )
            if id_audiencia is None or id_audiencia == '':
                await self.database.add_audiencia_preparatoria(self.id_causa, audienciaPreparatoria)
                mensaje = "Nueva audiencia preparatoria agregada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)
            else:
                await self.database.update_audiencia_preparatoria(id_audiencia, audienciaPreparatoria)
                mensaje = "Audiencia preparatoria actualizada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
            if self.update_tabla_audiencia_callback:
                await self.update_tabla_audiencia_callback()
        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')

    async def _update_causa_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_causa_button_click(self, event):
        await self.delete_dialog.open()

    async def some_delete_action(self, event=None):
        try:
            id_audiencia = self._get_data_value(0)

            if id_audiencia:
                await self.database.delete_audiencia_preparatoria(id_audiencia)
                mensaje = "Audiencia preparatoria eliminada correctamente"
            else:
                raise ValueError(
                    "No se especificó un ID válido para la audiencia preparatoria.")

            await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

            if self.update_tabla_audiencia_callback:
                await self.update_tabla_audiencia_callback()
        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')

    async def get_audencias_preparatorias_relaciones(self):
        # Define las columnas que deseas obtener de la composición familiar
        composicion_columns = ["id_audencia_preparatoria_relaciones",
                               "id_victima", "victima_representante_legal", "id_denunciado", "denunciado_representante_legal", "tipo_relacion", "denunciante_representanteLegal"]

        audencia_preparatoria_id = self._get_data_value(0)
        if audencia_preparatoria_id is not None:  # Asegúrate de que el victima_id no es None
            result = await self.database.get_audiencia_preparatoria_relaciones_by_audiencia(composicion_columns, audencia_preparatoria_id)
            # Maneja los datos como necesites, por ejemplo, mostrarlos en una tabla
            return result, composicion_columns
        else:
            print("No se ha podido obtener el ID de la víctima.")

    async def get_medidas_cautelares_de_audiencia(self):
        # Define las columnas que deseas obtener de las medidas cautelares
        medidas_columns = ["id_medida_cautelar",
                           "tipo_medida", "respuesta", "plazo"]

        audiencia_preparatoria_id = self._get_data_value(0)
        if audiencia_preparatoria_id is not None:  # Asegúrate de que el audiencia_preparatoria_id no es None
            result = await self.database.get_medidas_cautelares_by_audiencia_preparatoria(medidas_columns, audiencia_preparatoria_id)
            return result, medidas_columns
        else:
            print("No se ha podido obtener el ID de la audiencia preparatoria.")

    async def initialize_async_data(self):
        # Obtener datos de los involucrados en la audiencia preparatoria
        data_audiencia_involucrados, columns_audiencia_involucrados = await self.get_audencias_preparatorias_relaciones()
        if data_audiencia_involucrados is not None:
            await self.tabla_audencia_preparatoria_involucrados.update_table(data_audiencia_involucrados, columns_audiencia_involucrados)
        data_medidas_cautelares, columns_medidas_cautelares = await self.get_medidas_cautelares_de_audiencia()
        if data_medidas_cautelares is not None:
            await self.tabla_medidas_cautelares.update_table(data_medidas_cautelares, columns_medidas_cautelares)

        await self.page.update_async()

    async def on_row_on_row_preparatory_hearing_involved(self, selected_id):
        data_preparatory_hearing_involved = await self.database.get_audiencia_preparatoria_relacion_by_id(selected_id)
        data_preparatory_hearing_involved_info = selected_id, data_preparatory_hearing_involved
        await self.on_home_preparatory_hearing_involved_selected_callback(data_preparatory_hearing_involved_info)
        await self.page.go_async('/AudenciaPreparatoriaInvolucrados')

    async def on_row_selected_medida_cautelar(self, selected_id):
        data_medida_cautelar = await self.database.get_medida_cautelar_preparatoria_by_id(selected_id)
        data_medida_cautelar_info = (selected_id, data_medida_cautelar)
        await self.on_medida_cautelar_selected_callback(data_medida_cautelar_info)
        await self.page.go_async('/AudenciaPreparatoriaMedidasCautelares')
