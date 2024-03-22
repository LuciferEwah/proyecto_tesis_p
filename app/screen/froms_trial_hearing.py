import flet as ft
from widgets.dialog import ConfirmationDialog
from widgets.from_card_widget import FormCardWidget
from widgets.table_widget import TablaWidget
from models.audencia_juicio_antecedentes import AudienciaJuicioAntecedentes
import asyncio


class ScreenFormsJuicio(ft.UserControl):
    def __init__(self, db, page, data, id_causa, on_home_trial_hearing_selected_callback, on_home_trial_composicion_hogar_callback, on_home_trial_interim_measures_callback, update_tabla_juicio_callback, mostrar_mensaje_func=None):
        super().__init__()
        self.database = db
        self.page = page
        self.data = data if data else []
        self.id_causa = id_causa
        self.text_fields = {}
        self.on_home_trial_hearing_selected_callback = on_home_trial_hearing_selected_callback
        self.on_home_trial_composicion_hogar_callback = on_home_trial_composicion_hogar_callback
        self.on_home_trial_interim_measures_callback = on_home_trial_interim_measures_callback
        self.update_tabla_juicio_callback = update_tabla_juicio_callback
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
            "¿Estás seguro(a) que quieres actualizar los datos?",
            self.some_confirm_action
        )
        self.delete_dialog = ConfirmationDialog(
            self.page,
            "Eliminar",
            "¿Estás seguro(a) que quieres eliminar los datos?",
            self.some_delete_action
        )

        self.button_update = ft.OutlinedButton(
            "Guardar Audiencia de Juicio" if self.data else "Guardar Nueva Audiencia de Juicio",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_button_click
        )

        self.button_delete = ft.OutlinedButton(
            "Eliminar Audiencia de Juicio",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_button_click,
            disabled=False if self.data else True
        )

        form_section = FormCardWidget(
            title="Detalles de la Audiencia de Juicio",
            field_groups=self._juicio_fields(),
            buttons=[self.button_update, self.button_delete],
            text_fields=self.text_fields,
            page=self.page
        ).build()

        self.tabla_audencia_jucio_involucrados = TablaWidget(
            [], [], self.on_row_on_row_trial_hearing_involved, "Involucrados en audencia en el jucio","Agregar nueva audencia jucio", False if self.data else True,disabled= False if self.data else True, fixed_width=None)
        self.tabla_audencia_jucio_composicion_hogar = TablaWidget(
            [], [], self.on_row_on_row_trial_hearing_composicion, "Composición hogar de la victima - Antecedentes del jucio", "Agregar nueva composición hogar", False if self.data else True,disabled= False if self.data else True, fixed_width=None)
        self.tabla_trial_interim_measures = TablaWidget(
            [], [], self.on_row_on_row_trial_interim_measures, "Sentencia Medidas cutelares adoptadas en el jucio","Agregar nueva medida cautelar", False if self.data else True,disabled= False if self.data else True, fixed_width=None)

        asyncio.create_task(self.initialize_async_data())

        return ft.Container(
            expand=False,
            padding=20,
            content=ft.Column(controls=[form_section, self.tabla_audencia_jucio_involucrados, self.tabla_audencia_jucio_composicion_hogar, self.tabla_trial_interim_measures],
                              spacing=20)
        )

    def _juicio_fields(self):
        fields = [
            {"type": "text",
            "label": "Fecha Citación",
            "value": self._get_data_value(2)},
            {"type": "text",
            "label": "Fecha Realización",
            "value": self._get_data_value(3)},
            {"type": "dropdown",
            "label": "Cambio Composición Hogar",
            "options": ["Sí", "No", "No aplica", "Sin información"],
            "value": self._get_data_value(4)},
            {"type": "dropdown",
            "label": "Suspendido",
            "options": ["Sí", "No", "No aplica", "Sin información"],
            "value": self._get_data_value(5)},
            {"type": "dropdown",
            "label": "Resolución",
            "options": ["Salida Colaborativa", "Rechazo Acoger la Tramitación", "Tribunal se Declara Incompetente", "Citar Audiencia de Juicio", "Archivo del procedimiento", "Abandono del procedimiento", "Suspensión de la sentencia", "No aplica", "Sin información"],
            "value": self._get_data_value(6)},
            {"type": "text",
            "label": "Sentencia",
            "value": self._get_data_value(7)},
            {"type": "text",
            "label": "Salida Colaborativa",
            "value": self._get_data_value(8)},
            {"type": "dropdown",
            "label": "Carabineros Informa Cese Medidas",
            "options": ["Sí", "No", "No aplica", "Sin información"],
            "value": self._get_data_value(9)},
            {"type": "dropdown",
            "label": "Recurso Procesal",
            "options": ["Apelación", "Reposición", "Ninguno", "Otro", "No aplica", "Sin información"],
            "value": self._get_data_value(10)},
            {"type": "text",
            "label": "Recurso Procesal Otro",
            "value": self._get_data_value(11)},
            {"type": "dropdown",
            "label": "Abre Causa Cumplimiento",
            "options": ["Sí", "No", "No aplica", "Sin información"],
            "value": self._get_data_value(12)},
            {"type": "text",
            "label": "Causa Cumplimiento Rol RIT",
            "value": self._get_data_value(13)},
            {"type": "text",
            "label": "Solicitan Informes Oficios",
            "value": self._get_data_value(14)},
            {"type": "text",
            "label": "Informes Solicitados a quien",
            "value": self._get_data_value(15)},
            {"type": "text",
            "label": "Informes Entregados",
            "value": self._get_data_value(16)},
            {"type": "text",
            "label": "Informes Entregados Cuales",
            "value": self._get_data_value(17)},
            {"type": "text",
            "label": "Informes Pendientes",
            "value": self._get_data_value(18)},
            {"type": "text",
            "label": "Demora en Entrega de Informes",
            "value": self._get_data_value(19)},
            {"type": "text",
            "label": "Suspensión Condicional",
            "value": self._get_data_value(20)},
            {"type": "text",
            "label": "Otro Acuerdo Cual",
            "value": self._get_data_value(21)},
            {"type": "text",
            "label": "Pericia Solicitada",
            "value": self._get_data_value(22)},
            {"type": "text",
            "label": "Pericia Cual",
            "value": self._get_data_value(23)},
            {"type": "text",
            "label": "Pericia Solicitante",
            "value": self._get_data_value(24)},
            {"type": "text",
            "label": "Pericia Resultado",
            "value": self._get_data_value(25)},
            {"type": "text",
            "label": "Pericia Evaluado",
            "value": self._get_data_value(26)},
            {"type": "text",
            "label": "Medidas Cautelares",
            "value": self._get_data_value(27)},
            {"type": "text",
            "label": "Medidas Recurso",
            "value": self._get_data_value(28)},
        ]
        return fields

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def some_confirm_action(self):
        try:
            id_juicio = self._get_data_value(0)
            # Obtén los valores de los campos del formulario aquí
            fecha_citacion = self.text_fields["Fecha Citación"].value
            fecha_realizacion = self.text_fields["Fecha Realización"].value
            cambio_composicion_hogar = self.text_fields["Cambio Composición Hogar"].value
            suspendido = self.text_fields["Suspendido"].value
            resolucion = self.text_fields["Resolución"].value
            sentencia = self.text_fields["Sentencia"].value
            salida_colaborativa = self.text_fields["Salida Colaborativa"].value
            carabineros_informa_cese = self.text_fields["Carabineros Informa Cese Medidas"].value
            recurso_procesal = self.text_fields["Recurso Procesal"].value
            recurso_procesal_otro = self.text_fields["Recurso Procesal Otro"].value
            abre_causa_cumplimiento = self.text_fields["Abre Causa Cumplimiento"].value
            causa_cumplimiento_rol_rit = self.text_fields["Causa Cumplimiento Rol RIT"].value
            solicitan_informes_oficios = self.text_fields["Solicitan Informes Oficios"].value
            informes_solicitados_a_quien = self.text_fields["Informes Solicitados a quien"].value
            informes_entregados = self.text_fields["Informes Entregados"].value
            informes_entregados_cuales = self.text_fields["Informes Entregados Cuales"].value
            informes_pendientes = self.text_fields["Informes Pendientes"].value
            demora_informes = self.text_fields["Demora en Entrega de Informes"].value
            suspension_condicional = self.text_fields["Suspensión Condicional"].value
            otro_acuerdo_cual = self.text_fields["Otro Acuerdo Cual"].value
            pericia_solicitada = self.text_fields["Pericia Solicitada"].value
            pericia_cual = self.text_fields["Pericia Cual"].value
            pericia_solicitante = self.text_fields["Pericia Solicitante"].value
            pericia_resultado = self.text_fields["Pericia Resultado"].value
            pericia_evaluado = self.text_fields["Pericia Evaluado"].value
            medidas_cautelares = self.text_fields["Medidas Cautelares"].value
            medidas_recurso = self.text_fields["Medidas Recurso"].value
            audiencia_juicio = AudienciaJuicioAntecedentes(
                id_causa=self.id_causa,
                fecha_citacion=fecha_citacion,
                fecha_realizacion=fecha_realizacion,
                cambio_composicion_hogar=cambio_composicion_hogar,
                suspendido=suspendido,
                resolucion=resolucion,
                sentencia=sentencia,
                salida_colaborativa=salida_colaborativa,
                carabineros_informa_cese_medidas=carabineros_informa_cese,
                recurso_procesal=recurso_procesal,
                recurso_procesal_otro=recurso_procesal_otro,
                abre_causa_cumplimiento=abre_causa_cumplimiento,
                causa_cumplimiento_rol_rit=causa_cumplimiento_rol_rit,
                solicitan_informes_oficios= solicitan_informes_oficios,
                informes_solicitados_a_quien=informes_solicitados_a_quien,
                informes_entregados=informes_entregados,
                informes_entregados_cuales=informes_entregados_cuales,
                informes_pendientes=informes_pendientes,
                demora_informes=demora_informes,
                suspension_condicional=suspension_condicional,
                otro_acuerdo_cual=otro_acuerdo_cual,
                pericia_solicitada=pericia_solicitada,
                pericia_cual=pericia_cual,
                pericia_solicitante=pericia_solicitante,
                pericia_resultado=pericia_resultado,
                pericia_evaluado=pericia_evaluado,
                medidas_cautelares=medidas_cautelares,
                medidas_recurso=medidas_recurso
            )
            print(audiencia_juicio)
            print(id_juicio)
            if id_juicio is None or id_juicio == '':
                await self.database.add_audiencia_juicio(self.id_causa, audiencia_juicio)
                mensaje = "Nueva audiencia de juicio agregada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)

            else:
                await self.database.update_audiencia_juicio(id_juicio, audiencia_juicio)
                mensaje = "Audiencia de juicio actualizada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')

            if self.update_tabla_juicio_callback:
                await self.update_tabla_juicio_callback()

        except ValueError as ve:
            await self.mostrar_mensaje(self.page, f"Error de valor: {str(ve)}", severidad='error')
        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error inesperado: {str(e)}", severidad='error')

    async def _update_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_button_click(self, event):
        await self.delete_dialog.open()

    async def some_delete_action(self, event=None):
        try:
            id_juicio = self._get_data_value(0)
            await self.database.delete_audiencia_juicio(id_juicio)
            mensaje = "Audiencia de juicio eliminada correctamente"
            await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

            if self.update_tabla_juicio_callback:
                await self.update_tabla_juicio_callback()

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error al eliminar: {str(e)}", severidad='error')

    async def get_audencias_jucio_relaciones(self):
        composicion_columns = ["id_audenciaJuicio_relaciones",
                               "id_victima",  "victima_representante_legal", "id_denunciado", "denunciado_representante_legal", "tipo_relacion", "denunciante_representanteLegal"]
        audencia_jucio_id = self._get_data_value(0)
        if audencia_jucio_id is not None:  # Asegúrate de que el victima_id no es None
            result = await self.database.get_audiencia_juicio_relaciones_by_audiencia(composicion_columns, audencia_jucio_id)
            return result, composicion_columns
        else:
            print("No se ha podido obtener el ID.")

    async def get_audencias_jucio_composicion(self):
        composicion_columns = ["id_composicion_actual",
                               "id_victima", "tipo_relacion", "Respuesta", "cantidad"]
        audencia_jucio_id = self._get_data_value(0)
        if audencia_jucio_id is not None:  # Asegúrate de que el victima_id no es None
            result = await self.database.get_composicion_hogar_en_juicio_by_audiencia(composicion_columns, audencia_jucio_id)
            return result, composicion_columns
        else:
            print("No se ha podido obtener el ID.")

    async def get_medidas_provisorias_by_sentencia(self):
        composicion_columns = ["id_medida_sentencia",
                               "tipo_medida", "respuesta", "plazo"]
        audencia_jucio_id = self._get_data_value(0)
        if audencia_jucio_id is not None:  # Asegúrate de que el victima_id no es None
            result = await self.database.get_medidas_provisorias_by_sentencia(composicion_columns, audencia_jucio_id)
            return result, composicion_columns
        else:
            print("No se ha podido obtener el ID.")

    async def initialize_async_data(self):
        # Obtener datos de los involucrados en la audiencia preparatoria
        data_audiencia_involucrados, columns_audiencia_involucrados = await self.get_audencias_jucio_relaciones()
        data_juicio_composicion_hogar, columns_composicion_hogar = await self.get_audencias_jucio_composicion()
        data_juicio_medidas, columns_juicio_medidas = await self.get_medidas_provisorias_by_sentencia()
        if data_audiencia_involucrados is not None:
            await self.tabla_audencia_jucio_involucrados.update_table(data_audiencia_involucrados, columns_audiencia_involucrados)
        if data_juicio_composicion_hogar is not None:
            await self.tabla_audencia_jucio_composicion_hogar.update_table(data_juicio_composicion_hogar, columns_composicion_hogar)
        if data_juicio_composicion_hogar is not None:
            await self.tabla_trial_interim_measures.update_table(data_juicio_medidas, columns_juicio_medidas)

    async def on_row_on_row_trial_hearing_involved(self, selected_id):
        data_trial_hearing_involved = await self.database.get_audiencia_juicio_relacion_by_id(selected_id)
        data_trial_hearing_involved_info = selected_id, data_trial_hearing_involved
        await self.on_home_trial_hearing_selected_callback(data_trial_hearing_involved_info)
        await self.page.go_async('/AudienciaJuicioInvolucrados')

    async def on_row_on_row_trial_hearing_composicion(self, selected_id):
        data_juicio_composicion_hogar = await self.database.get_composicion_hogar_en_juicio_by_id(selected_id)
        data_trial_composicion_hogar_info = selected_id, data_juicio_composicion_hogar
        await self.on_home_trial_composicion_hogar_callback(data_trial_composicion_hogar_info)
        await self.page.go_async('/ComposicionHogarEnJuicio')

    async def on_row_on_row_trial_interim_measures(self, selected_id):
        data_trial_interim_measures = await self.database.get_medida_provisoria_by_id(selected_id)
        data_trial_interim_measures_info = selected_id, data_trial_interim_measures
        await self.on_home_trial_interim_measures_callback(data_trial_interim_measures_info)
        await self.page.go_async('/MedidasCautelaresJuicio')
