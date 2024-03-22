import flet as ft
from models.denunciantes import Denunciante
from widgets.dialog import ConfirmationDialog
from widgets.from_card_widget import FormCardWidget


class ScreenFormsDenunciante(ft.UserControl):
    def __init__(self, db, page, data, update_table_causa, id_causa=None, mostrar_mensaje_func=None):
        super().__init__()
        self.database = db
        self.page = page
        self.data = data if data else []
        self.text_fields = {}
        self.update_table_causa = update_table_causa
        self.id_causa = id_causa
        if not data:
            self.limpiar_formulario()
        self.mostrar_mensaje = mostrar_mensaje_func

    def limpiar_formulario(self):
        # Recorre todos los campos de texto y establece sus valores a vacío
        for key in self.text_fields:
            self.text_fields[key].value = ""

    def build(self):
        self.confirm_dialog = ConfirmationDialog(
            self.page,
            "Esta acción necesita confirmación",
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
            "Guardar Denunciante" if self.data else "Guardar Nuevo Denunciante",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_causa_button_click
        )

        self.causa_button_delete = ft.OutlinedButton(
            "Eliminar Denunciante",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_causa_button_click,
            disabled=False if self.data else True
        )
        denunciante_section = FormCardWidget(
            title="Detalles de la Denunciantes",
            field_groups=self._denunciante_fields(),
            buttons=[self.causa_button_update, self.causa_button_delete],
            text_fields=self.text_fields,
            page=self.page
        ).build()

        return ft.Container(
            expand=False,
            padding=20,
            content=ft.Column(controls=[denunciante_section],
                              spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    def _denunciante_fields(self):
        fields = [
            {"type": "dropdown",
             "label": "Es Denunciante Víctima",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(2)},
            {"type": "text", "label": "Es Denunciante Persona Jurídica",
             "value": self._get_data_value(3)},
            {"type": "text", "label": "Nombre Persona Jurídica",
             "value": self._get_data_value(4)},
            {"type": "int", "label": "Edad Denunciante",
             "value": self._get_data_value(5)},
            {"type": "dropdown",
             "label": "Sexo Denunciante",
             "options": ["Femenino", "Masculino", "No aplica", "Sin información"],
             "value": self._get_data_value(6)},
            {"type": "dropdown",
             "label": "Nacionalidad Denunciante",
             "options": ["Chilena", "Extranjera", "Sin información", "No aplica"],
             "value": self._get_data_value(7)},
            {"type": "text",
             "label": "Nacionalidad Extranjera Denunciante",
             "value": self._get_data_value(8)},
            {"type": "dropdown", "label": "Profesión/Oficio Denunciante",
             "options": ["Estudiante", "Dueña(o) de hogar", "Empleado(a)", "Desempleado(a)", "Otra ocupación", "Jubilado(a)/Pensionado(a)", "Sin ocupación/oficio", "No aplica", "Sin información"],
             "value": self._get_data_value(9)},
            {"type": "dropdown",
             "label": "Estudios Denunciante",
             "options":  ["No aplica", "Sin info", "Nunca asistió", "Diferencial", "Sala Cuna", "Jardín Inf", "Prekínder/Kínder", "Básica Inc", "Básica Comp", "Media Inc", "Media Comp", "Técnico Profesional Inc", "Técnico Profesional Comp", "Profesional Inc", "Profesional Comp", "Posgrado Inc", "Posgrado Com"],
             "value": self._get_data_value(10)},
            {"type": "dropdown", "label": "Parentesco con el Acusado",
             "options": ["Cónyuge", "Ex Cónyuge", "Pareja", "Ex Pareja", "Conviviente (con AUC)", "Ex Conviviente (con AUC)", "Conviviente de hecho", "Ex conviviente de hecho", "Padre/Madre", "Padrastro/Madrasta", "Hijo/a", "Hermano/a", "Tío/a", "Suegro/a", "Abuelo/a", "Nieto/a", "Otro", "No aplica", "Sin información"],
             "value": self._get_data_value(11)},
            {"type": "text",
             "label": "Parentesco con el Acusado (Otro)",
             "value": self._get_data_value(12)},
            {"type": "dropdown",
             "label": "Presencia de Lesiones Denunciante",
             "options": ["Sin lesiones", "Con lesiones", "No aplica", "Sin información"],
             "value": self._get_data_value(13)},
            {"type": "dropdown",
             "label": "Descripción de la Lesión Denunciante",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(14)},
            {"type": "dropdown",
             "label": "Estado de Temperancia Denunciante",
             "options": ["Estado Normal", "Otro", "No aplica", "Sin información"],
             "value": self._get_data_value(15)},
            {"type": "text", "label": "Estado de Temperancia Denunciante (Otro)", "value": self._get_data_value(
                16)},
            {"type": "text",
             "label": "Descripción de la Temperancia Denunciante",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(17)},
            {"type": "dropdown",
             "label": "Comuna",
             "options": ["Alhué", "Buin", "Calera de Tango", "Cerrillos", "Cerro Navia", "Colina", "Conchalí", "Curacaví", "El Bosque", "El Monte", "Estación Central", "Huechuraba", "Independencia", "Isla de Maipo", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Lampa", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "María Pinto", "Melipilla", "Padre Hurtado", "Paine", "Pedro Aguirre Cerda", "Peñaflor", "Peñalolén", "Pirque", "Providencia", "Pudahuel", "Puente Alto", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Bernardo", "San Joaquín", "San José de Maipo", "San Miguel", "San Pedro", "San Ramón", "Santiago", "Talagante", "Tiltil", "Vitacura", "Ñuñoa"],
             "value": self._get_data_value(18)},
            {"type": "dropdown", 
             "label": "Estado Civil",
             "options": ["Casado/a", "Conviviente/Pareja (Sin AUC)", "Conviviente/Pareja (Con AUC)", "Anulado/a", "Separado/a", "Divorciado/a", "Viudo/a", "Soltero/a", "No aplica", "Sin información"],
             "value": self._get_data_value(19)}

        ]

        return fields

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def _update_causa_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_causa_button_click(self, event):
        await self.delete_dialog.open()

    async def some_confirm_action(self):
        try:

            tipo_relacion = self._get_data_value(0)
            denunciante = Denunciante(
                id_causa=self._get_data_value(1),
                es_denunciante_victima=self.text_fields["Es Denunciante Víctima"].value,
                es_denunciante_persona_juridica=self.text_fields["Es Denunciante Persona Jurídica"].value,
                nombre_persona_juridica=self.text_fields["Nombre Persona Jurídica"].value,
                edad_denunciante=int(
                    self.text_fields["Edad Denunciante"].value),
                sexo_denunciante=self.text_fields["Sexo Denunciante"].value,
                nacionalidad_denunciante=self.text_fields["Nacionalidad Denunciante"].value,
                nacionalidad_extranjera_denunciante=self.text_fields[
                    "Nacionalidad Extranjera Denunciante"].value,
                profesion_oficio_denunciante=self.text_fields["Profesión/Oficio Denunciante"].value,
                estudios_denunciante=self.text_fields["Estudios Denunciante"].value,
                parentesco_acusado=self.text_fields["Parentesco con el Acusado"].value,
                parentesco_acusado_otro=self.text_fields[
                    "Parentesco con el Acusado (Otro)"].value,
                caracter_lesion_denunciante=self.text_fields[
                    "Presencia de Lesiones Denunciante"].value,
                descripcion_lesion_denunciante=self.text_fields[
                    "Descripción de la Lesión Denunciante"].value,
                estado_temperancia_denunciante=self.text_fields[
                    "Estado de Temperancia Denunciante"].value,
                estado_temperancia_denunciante_otro=self.text_fields[
                    "Estado de Temperancia Denunciante (Otro)"].value,
                descripcion_temperancia_denunciante=self.text_fields[
                    "Descripción de la Temperancia Denunciante"].value,
                comuna=self.text_fields["Comuna"].value,
                estado_civil=self.text_fields["Estado Civil"].value
            )

            if tipo_relacion is None or tipo_relacion == '':
                await self.database.add_denunciante(self.id_causa, denunciante)
                mensaje = "Nuevo denunciante agregado correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)

            else:
                await self.database.update_denunciante(tipo_relacion, denunciante)
                mensaje = "Denunciante actualizado correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
            if self.update_table_causa:
                await self.update_table_causa()
        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')

    async def some_delete_action(self, event=None):
        try:
            tipo_relacion = self._get_data_value(0)
            await self.database.delete_denunciante(tipo_relacion)
            mensaje = "Denunciante eliminado correctamente"
            await self.mostrar_mensaje(self.page, mensaje, severidad='exito')

            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

            if self.update_table_causa:
                await self.update_table_causa()

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')
