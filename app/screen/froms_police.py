import flet as ft
from widgets.dialog import ConfirmationDialog
from widgets.from_card_widget import FormCardWidget
from models.antecedente_policial import AntecedentePolicial
from widgets.table_widget import TablaWidget
import asyncio


class ScreenFormsPolice(ft.UserControl):
    def __init__(self, db, page, data, id_causa, on_home_police_measures_callback, update_tabla_antecedentes_callback=None, mostrar_mensaje_func=None):
        super().__init__()
        self.database = db
        self.page = page
        self.data = data if data else []
        self.id_causa = id_causa
        self.text_fields = {}
        self.on_home_police_measures_callback = on_home_police_measures_callback
        self.update_tabla_antecedentes_callback = update_tabla_antecedentes_callback
        if not data:
            self.limpiar_formulario()
        self.mostrar_mensaje = mostrar_mensaje_func

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
            "Guardar antecedentes del delito" if self.data else "Guardar Nuevo antecedentes del delito",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_button_click
        )

        self.button_delete = ft.OutlinedButton(
            "Eliminar antecedentes del delito",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_button_click,
            disabled=False if self.data else True
        )

        antecedentes_section = FormCardWidget(
            title="Detalles de Antecedentes del Delito",
            field_groups=self._antecedentes_fields(),
            buttons=[self.button_update, self.button_delete],
            text_fields=self.text_fields,
            page=self.page
        ).build()

        self.tabla_police_measures = TablaWidget(
            [], [], self.on_row_on_row_police_measures_involved, "Medidas cutelares Carabineros","Agregar nueva medida cautelar", False if self.data else True,disabled= False if self.data else True, fixed_width=None)
        asyncio.create_task(self.initialize_async_data())

        return ft.Container(
            expand=False,
            padding=20,
            content=ft.Column(
                controls=[antecedentes_section, self.tabla_police_measures], spacing=20)
        )

    def _antecedentes_fields(self):
        fields = [
            {"type": "dropdown",
                "label": "Código del Delito",
                "options": ["VIF (Lesiones físicas)", "VIF (Lesiones psicológicas)", "VIF (Lesiones físicas y psicológicas)", "No aplica"],
                "value": self._get_data_value(2)},
            {"type": "text",
                "label": "Fecha del Delito",
                "value": self._get_data_value(3)},
            {"type": "text",
                "label": "Hora del Delito",
                "value": self._get_data_value(4)},
            {"type": "dropdown",
                "label": "Lugar de Ocurrencia",
                "options": ["Domicilio particular", "Via pública", "Otro", "No aplica", "Sin información"],
                "value": self._get_data_value(5)},
            {"type": "text",
                "label": "Lugar de Ocurrencia - Otro",
                "value": self._get_data_value(6)},
            {"type": "dropdown",
             "label": "Comuna",
             "options": ["Alhué", "Buin", "Calera de Tango", "Cerrillos", "Cerro Navia", "Colina", "Conchalí", "Curacaví", "El Bosque", "El Monte", "Estación Central", "Huechuraba", "Independencia", "Isla de Maipo", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Lampa", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "María Pinto", "Melipilla", "Padre Hurtado", "Paine", "Pedro Aguirre Cerda", "Peñaflor", "Peñalolén", "Pirque", "Providencia", "Pudahuel", "Puente Alto", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Bernardo", "San Joaquín", "San José de Maipo", "San Miguel", "San Pedro", "San Ramón", "Santiago", "Talagante", "Tiltil", "Vitacura", "Ñuñoa"],
             "value": self._get_data_value(7)},
            {"type": "text",
                "label": "Unidad",
                "value": self._get_data_value(8)},
            {"type": "text",
                "label": "Cuadrante",
                "value": self._get_data_value(9)},
        ]
        return fields

    async def _update_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_button_click(self, event):
        await self.delete_dialog.open()

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def some_confirm_action(self):
        try:
            id_antecedente = self._get_data_value(0)
            codigo_delito = self.text_fields["Código del Delito"].value
            fecha_delito = self.text_fields["Fecha del Delito"].value
            hora_delito = self.text_fields["Hora del Delito"].value
            lugar_ocurrencia = self.text_fields["Lugar de Ocurrencia"].value
            lugar_ocurrencia_otro = self.text_fields["Lugar de Ocurrencia - Otro"].value
            comuna = self.text_fields["Comuna"].value
            unidad = self.text_fields["Unidad"].value
            cuadrante = self.text_fields["Cuadrante"].value

            antecedente_policial = AntecedentePolicial(
                id_causa=self.id_causa,
                codigo_delito=codigo_delito,
                fecha_delito=fecha_delito,
                hora_delito=hora_delito,
                lugar_ocurrencia=lugar_ocurrencia,
                lugar_ocurrencia_otro=lugar_ocurrencia_otro,
                comuna=comuna,
                unidad=unidad,
                cuadrante=cuadrante
            )

            if id_antecedente is None or id_antecedente == '':
                await self.database.add_antecedente_policial(self.id_causa, antecedente_policial)
                mensaje = "Nuevo antecedente policial agregado correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)
            else:
                await self.database.update_antecedente_policial(id_antecedente, antecedente_policial)
                mensaje = "Antecedente policial actualizado correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
            if self.update_tabla_antecedentes_callback:
                await self.update_tabla_antecedentes_callback()
        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')

    async def some_delete_action(self, event=None):
        try:
            id_antecedente = self._get_data_value(0)
            await self.database.delete_antecedente_policial(id_antecedente)
            mensaje = "Antecedente policial eliminado correctamente"

            await self.mostrar_mensaje(self.page, mensaje, severidad='exito')

            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

            if self.update_tabla_antecedentes_callback:
                await self.update_tabla_antecedentes_callback()

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')

    async def get_medidas_policiales_by_antecedentes(self):
        composicion_columns = ["id_medida_policial", "tipo_medida", "respuesta", "plazo"]
        audencia_antecedentes_policiales = self._get_data_value(0)
        if audencia_antecedentes_policiales is not None:  # Asegúrate de que el victima_id no es None
            result = await self.database.get_medidas_policiales_by_antecedente_delito(composicion_columns, audencia_antecedentes_policiales)
            return result, composicion_columns
        else:
            print("No se ha podido obtener el ID.")

    async def initialize_async_data(self):
        # Obtener datos de los involucrados en la audiencia preparatoria
        data_police_measures, columns_police_measures = await self.get_medidas_policiales_by_antecedentes()
        if data_police_measures is not None:
            await self.tabla_police_measures.update_table(data_police_measures, columns_police_measures)

    async def on_row_on_row_police_measures_involved(self, selected_id):
        data_police_measures = await self.database.get_medida_policial_by_id(selected_id)
        data_police_measures_info = selected_id, data_police_measures
        await self.on_home_police_measures_callback(data_police_measures_info)
        await self.page.go_async('/MedidasPoliciales')
