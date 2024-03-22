# screen_forms_victima.py
import flet as ft
from widgets.popbutton import PopButton
from models.victima import Victima
from widgets.dialog import ConfirmationDialog
from widgets.table_widget import TablaWidget
import asyncio
from widgets.from_card_widget import FormCardWidget


class ScreenFormsVictima(ft.UserControl):
    def __init__(self, db, page, data, on_home_composition_selected_callback, update_tabla_victima_callback, update_card_dashboard, id_causa=None, mostrar_mensaje_func=None):
        super().__init__()  # Llamada al constructor de la clase base
        self.database = db
        self.page = page
        self.data = data if data else []
        self.text_fields = {}
        self.id_causa = id_causa
        self.update_tabla_victima_callback = update_tabla_victima_callback
        self.update_card_dashboard = update_card_dashboard
        self.on_home_composition_selected_callback = on_home_composition_selected_callback
        self.mostrar_mensaje = mostrar_mensaje_func

        if not data:
            self.limpiar_formulario()

    def limpiar_formulario(self):
        # Recorre todos los campos de texto y establece sus valores a vacío
        for key in self.text_fields:
            self.text_fields[key].value = ""

    def build(self):
        self.confirm_dialog = ConfirmationDialog(
            self.page,
            "Esta acción necesita confirmación ",
            "¿Estás seguro(a) que quieres Actualizar los datos?",
            self.some_confirm_action
        )
        self.delete_dialog = ConfirmationDialog(
            self.page,
            "Esta acción necesita confirmación",
            "¿Estás seguro(a) que quieres Eliminar los datos?",
            self.some_delete_action
        )
        self.causa_button_update = ft.OutlinedButton(
            "Guardar Nueva Victima" if self.data else "Guardar Nueva Victima",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_causa_button_click
        )

        self.causa_button_delete = ft.OutlinedButton(
            "Eliminar Nueva Victima",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_causa_button_click,
            disabled=False if self.data else True
        )

        victima_section = FormCardWidget(
            title="Detalles de la Victima",
            field_groups=self._victima_fields(),
            buttons=[self.causa_button_update, self.causa_button_delete],
            text_fields=self.text_fields,
            page=self.page
        ).build()

        self.tabla_widget = TablaWidget(
            [], [], self.on_row_selected, "Resumen de Composición del Hogar de la Víctima", "Agregar nueva composición del hogar",False if self.data else True,disabled= False if self.data else True, fixed_width=None)
        asyncio.create_task(self.initialize_async_data())

        return ft.Container(
            expand=False,
            padding=20,
            content=ft.Column(controls=[victima_section, self.tabla_widget],
                              spacing=20)
        )

    def _victima_fields(self):
        fields = [
            {"type": "int",
             "label": "Edad",
             "value": self._get_data_value(2)},
            {"type": "dropdown",
             "label": "Sexo", "options": ["Femenino", "Masculino", "No aplica", "Sin información"],
             "value": self._get_data_value(3)},
            {"type": "dropdown",
             "label": "Nacionalidad", "options": ["Chilena", "Extranjera", "No aplica", "Sin información"],
             "value": self._get_data_value(4)},
            {"type": "text", "label": "Nacionalidad Extranjera",
             "value": self._get_data_value(5)},
            {"type": "dropdown", "label": "Profesión/Oficio",
             "options": ["Estudiante", "Dueña(o) de hogar", "Empleado(a)", "Desempleado(a)", "Otra ocupación", "Jubilado(a)/Pensionado(a)", "Sin ocupación/oficio", "No aplica", "Sin información"],
             "value": self._get_data_value(6)},
            {"type": "dropdown",
             "label": "Estudios",
             "options":  ["No aplica", "Sin info", "Nunca asistió", "Diferencial", "Sala Cuna", "Jardín Inf", "Prekínder/Kínder", "Básica Inc", "Básica Comp", "Media Inc", "Media Comp", "Técnico Profesional Inc", "Técnico Profesional Comp", "Profesional Inc", "Profesional Comp", "Posgrado Inc", "Posgrado Com"],
             "value": self._get_data_value(7)},
            {"type": "dropdown",
             "label": "Parentesco con el Acusado",
             "options": ["Cónyuge", "Ex Cónyuge", "Pareja", "Ex Pareja", "Conviviente (con AUC)", "Ex Conviviente (con AUC)", "Conviviente de hecho", "Ex conviviente de hecho", "Padre/Madre", "Padrastro/Madrasta", "Hijo/a", "Hermano/a", "Tío/a", "Suegro/a", "Abuelo/a", "Nieto/a", "Otro", "No aplica", "Sin información"],
             "value": self._get_data_value(8)},
            {"type": "text",
             "label": "Parentesco con el Acusado (Otro)",
             "value": self._get_data_value(9)},
            {"type": "dropdown",
             "label": "Caracter de Lesiones",
             "options": ["Sin lesiones", "Con lesiones", "No aplica", "Sin información"],
             "value": self._get_data_value(10)},
            {"type": "dropdown", "label": "Descripción de la Lesión",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(11)},
            {"type": "dropdown",
             "label": "Estado de Temperancia",
             "options": ["Estado Normal", "Otro", "No aplica", "Sin información"],
             "value": self._get_data_value(12)},
            {"type": "text",
             "label": "Estado de Temperancia (Otro)",
             "value": self._get_data_value(13)},
            {"type": "dropdown",
             "label": "Descripción de la Temperancia",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(14)},
            {"type": "dropdown",
             "label": "Comuna",
             "options": ["Alhué", "Buin", "Calera de Tango", "Cerrillos", "Cerro Navia", "Colina", "Conchalí", "Curacaví", "El Bosque", "El Monte", "Estación Central", "Huechuraba", "Independencia", "Isla de Maipo", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Lampa", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "María Pinto", "Melipilla", "Padre Hurtado", "Paine", "Pedro Aguirre Cerda", "Peñaflor", "Peñalolén", "Pirque", "Providencia", "Pudahuel", "Puente Alto", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Bernardo", "San Joaquín", "San José de Maipo", "San Miguel", "San Pedro", "San Ramón", "Santiago", "Talagante", "Tiltil", "Vitacura", "Ñuñoa"],
             "value": self._get_data_value(15)},
            {"type": "dropdown", "label": "Tiempo de Relación",
             "options": ["Menos de 1 año", "1 a 5 años", "6 a 10 años", "11 a 15 años", "16 a 20 años", "Más de 20 años", "No aplica", "Sin información"],
             "value": self._get_data_value(16)},
            {"type": "dropdown",
             "label": "Estado Civil",
             "options": ["Casado/a", "Conviviente/Pareja (Sin AUC)", "Conviviente/Pareja (Con AUC)", "Anulado/a", "Separado/a", "Divorciado/a", "Viudo/a", "Soltero/a", "No aplica", "Sin información"],
             "value": self._get_data_value(17)},
            {"type": "dropdown", 
             "label": "Parentesco con el Denunciante",
             "options": ["Cónyuge", "Ex Cónyuge", "Pareja", "Ex Pareja", "Conviviente (con AUC)", "Ex Conviviente (con AUC)", "Conviviente de hecho", "Ex conviviente de hecho", "Padre/Madre", "Padrastro/Madrasta", "Hijo/a", "Hermano/a", "Tío/a", "Suegro/a", "Abuelo/a", "Nieto/a", "Otro", "No aplica", "Sin información"],
             "value": self._get_data_value(18)},
            {"type": "text",
             "label": "Parentesco con el Denunciante (Otro)",
             "value": self._get_data_value(19)},
            {"type": "text",
             "label": "violencia patrimonial",
             "value": self._get_data_value(20)},
            {"type": "text",
             "label": "violencia economica",
             "value": self._get_data_value(21)},
             {"type": "text",
             "label": "ayuda tecnica",
             "value": self._get_data_value(22)},
             {"type": "text",
             "label": "ayuda tecnica tipo",
             "value": self._get_data_value(23)},
             {"type": "text",
             "label": "deterioro cognitivo",
             "value": self._get_data_value(24)},
             {"type": "text",
             "label": "informe medico",
             "value": self._get_data_value(25)},
             {"type": "text",
             "label": "num de enfermedades",
             "value": self._get_data_value(26)},
             {"type": "text",
             "label": "inasistencias de salud",
             "value": self._get_data_value(27)},
             {"type": "text",
             "label": "informes social",
             "value": self._get_data_value(28)},
             {"type": "text",
             "label": "comuna de ingreso",
             "value": self._get_data_value(29)},
             {"type": "text",
             "label": "listado de enfermedades",
             "value": self._get_data_value(30)},
        ]
        return fields

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def some_confirm_action(self):
        try:
            id_victima = self._get_data_value(0)
            victima = Victima(
                id_causa= self._get_data_value(1),
                edad=int(self.text_fields["Edad"].value),
                sexo=self.text_fields["Sexo"].value,
                nacionalidad=self.text_fields["Nacionalidad"].value,
                nacionalidad_extranjera=self.text_fields["Nacionalidad Extranjera"].value,
                profesion_oficio=self.text_fields["Profesión/Oficio"].value,
                estudios=self.text_fields["Estudios"].value,
                parentesco_acusado=self.text_fields["Parentesco con el Acusado"].value,
                parentesco_acusado_otro=self.text_fields["Parentesco con el Acusado (Otro)"].value,
                caracter_lesion=self.text_fields["Caracter de Lesiones"].value,
                descripcion_lesion=self.text_fields["Descripción de la Lesión"].value,
                estado_temperancia=self.text_fields["Estado de Temperancia"].value,
                estado_temperancia_otro=self.text_fields["Estado de Temperancia (Otro)"].value,
                descripcion_temperancia=self.text_fields["Descripción de la Temperancia"].value,
                comuna=self.text_fields["Comuna"].value,
                tiempo_relacion=self.text_fields["Tiempo de Relación"].value,
                estado_civil=self.text_fields["Estado Civil"].value,
                parentesco_denunciante=self.text_fields["Parentesco con el Denunciante"].value,
                parentesco_denunciante_otro=self.text_fields["Parentesco con el Denunciante (Otro)"].value,
                violencia_patrimonial = self.text_fields["violencia patrimonial"].value,
                vic_violencia_economica = self.text_fields["violencia economica"].value,
                vic_ayuda_tecnica = self.text_fields["ayuda tecnica"].value,
                vic_ayuda_tecnica_tipo = self.text_fields["ayuda tecnica tipo"].value,
                vic_deterioro_cognitivo = self.text_fields["deterioro cognitivo"].value,
                vic_informe_medico = self.text_fields["informe medico"].value,
                vic_num_enfermedades = self.text_fields["num de enfermedades"].value,
                vic_inasistencias_salud = self.text_fields["inasistencias de salud"].value,
                vic_informes_social = self.text_fields["informes social"].value,
                vic_comuna_ingreso = self.text_fields["comuna de ingreso"].value,
                listado_enfermedades = self.text_fields["listado de enfermedades"].value
                )

            if id_victima is None or id_victima == '':
                mensaje = await self.database.add_victima(self.id_causa, victima)
                mensaje = "Victima Agregada correctamente"
                severidad = 'exito'
                await self.mostrar_mensaje(self.page, mensaje, severidad)
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)
            else:
                mensaje = await self.database.update_victima(id_victima, victima)
                mensaje = "Victima Actualizada correctamente"
                severidad = 'exito'
                await self.mostrar_mensaje(self.page, mensaje, severidad)

            if self.update_tabla_victima_callback:
                await self.update_tabla_victima_callback()
            if self.update_card_dashboard:
                await self.update_card_dashboard()
        except ValueError as ve:
            # Captura errores de valor, como un valor entero inválido
            mensaje = f"Error de valor: {str(ve)}."
            severidad = 'error'
            await self.mostrar_mensaje(self.page, mensaje, severidad)
        except Exception as e:
            # Captura cualquier otro error
            mensaje = f"Error inesperado: {str(e)}"
            severidad = 'error'
            await self.mostrar_mensaje(self.page, mensaje, severidad)

    async def on_update_click(self, e):
        # Método que se llama cuando se hace clic en el botón de actualizar
        await self.update_victima_data()

    async def _update_causa_button_click(self, event):
        await self.confirm_dialog.open()
        # Obtienes el ID de la causa seleccionada'

    async def _delete_causa_button_click(self, event):
        await self.delete_dialog.open()

    async def get_composicion_familiar(self):
        # Define las columnas que deseas obtener de la composición familiar
        composicion_columns = [
            "id_composicion", "tipo_relacion", "Respuesta", "cantidad"]
        # Obtiene el ID de la víctima desde los datos actuales
        # Asegúrate de tener una forma de obtener este valor
        victima_id = self._get_data_value(0)
        if victima_id is not None:  # Asegúrate de que el victima_id no es None
            result = await self.database.get_composicion_familiar_por_victima(victima_id)
            # Maneja los datos como necesites, por ejemplo, mostrarlos en una tabla
            return result, composicion_columns
        else:
            print("No se ha podido obtener el ID de la víctima.")

    async def initialize_async_data(self):
        # Este método puede realizar operaciones asíncronas para obtener los datos.
        data, columns = await self.get_composicion_familiar()
        if data is not None:
            # Si obtienes datos, actualiza la tabla.
            await self.tabla_widget.update_table(data, columns)
            await self.page.update_async()

    async def on_row_selected(self, selected_id):
        data_home_composition = await self.database.get_family_composition_by_id(selected_id)
        await self.on_home_composition_selected_callback(data_home_composition)
        await self.page.go_async('/formulario_composicion_hogar')

    async def some_delete_action(self, event=None):
        try:
            id_victima = self._get_data_value(0)
            await self.database.delete_victima(id_victima)
            mensaje = "Víctima eliminada correctamente"

            await self.mostrar_mensaje(self.page, mensaje, severidad='exito')

            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

            if self.update_tabla_victima_callback:
                await self.update_tabla_victima_callback()
            if self.update_card_dashboard:
                await self.update_card_dashboard()

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error al eliminar: {str(e)}", severidad='error')
