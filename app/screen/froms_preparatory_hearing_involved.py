import flet as ft
from widgets.dialog import ConfirmationDialog
from widgets.from_card_widget import FormCardWidget
from models.audencia_relaciones import AudienciaRelaciones
import asyncio


class ScreenPreparatoryHearingInvolved(ft.UserControl):
    def __init__(self, db, page, data, id_audencia, id_causa, update_tabla_audiencia_involved_callback=None, mostrar_mensaje_func=None):
        super().__init__()
        self.database = db
        self.data = data if data else []
        self.page = page
        self.text_fields = {}
        self.id_audencia = id_audencia
        self.id_causa = id_causa
        self.update_tabla_audiencia_involved_callback = update_tabla_audiencia_involved_callback
        if not data:
            self.limpiar_formulario()
        self.opciones_victimas = []
        self.opciones_denunciado = []
        self.opciones_denunciante = []
        self.mostrar_mensaje = mostrar_mensaje_func

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

        self.home_composition_button_update = ft.OutlinedButton(
            "Guardar" if self.data else "Guardar Nueva Composición del Hogar",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_button_click
        )

        self.home_composition_button_delete = ft.OutlinedButton(
            "Eliminar",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_button_click,
            disabled=False if self.data else True
        )
        composition_section = FormCardWidget(
            title="Detalles los involucrados en la audencia preparatoria",
            field_groups=self._audiencia_preparatoria_involved_fields(
                self.opciones_victimas, self.opciones_denunciado, self.opciones_denunciante),
            buttons=[self.home_composition_button_update,
                     self.home_composition_button_delete],
            text_fields=self.text_fields,
            page=self.page
        )

        asyncio.create_task(self.actualizar_dropdown_victimas(self.id_causa))
        asyncio.create_task(
            self.actualizar_dropdown_denunciados(self.id_causa))
        asyncio.create_task(
            self.actualizar_dropdown_denunciantes(self.id_causa))
        return ft.Container(
            expand=False,
            padding=20,
            content=ft.Column(controls=[composition_section],
                              spacing=20)
        )

    def _audiencia_preparatoria_involved_fields(self, opciones_de_victimas, opciones_de_denunciado, opciones_de_denunciante):
        fields = [

            {"type": "dropdown",
             "label": "ID Víctima",
             "options": opciones_de_victimas,
             "value": self._get_data_value(2), "col": {"md": 3}},
            {"type": "dropdown",
             "label": "ID Denunciado",
             "options": opciones_de_denunciado,
             "value": self._get_data_value(3), "col": {"md": 3}},
            {"type": "dropdown",
             "label": "ID Denunciante",
             "options": opciones_de_denunciante,
             "value": self._get_data_value(4), "col": {"md": 4}},
            {"type": "dropdown",
             "label": "Representante Legal Víctima",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(5), "col": {"md": 3}},
            {"type": "dropdown",
             "label": "Representante Legal Denunciado",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(6), "col": {"md": 3}},
            {"type": "dropdown",
             "label": "Representante Legal Denunciante",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(7), "col": {"md": 4}},

        ]
        return fields

    async def actualizar_dropdown_victimas(self, id_causa):
        ids_victimas = await self.database.obtener_ids_victimas_por_causa(id_causa)
        opciones_dropdown = [str(id_victima) for id_victima in ids_victimas]

        self.text_fields["ID Víctima"].options = [
            ft.dropdown.Option(id_victima) for id_victima in opciones_dropdown]

        # Establecer el valor actual como defecto
        # Asegúrate de que este es el índice correcto
        valor_actual = str(self._get_data_value(2))
        if valor_actual in opciones_dropdown:
            self.text_fields["ID Víctima"].value = valor_actual

        await self.text_fields["ID Víctima"].update_async()

    async def actualizar_dropdown_denunciados(self, id_causa):
        ids_denunciados = await self.database.obtener_ids_denunciados_por_causa(id_causa)
        opciones_dropdown = [str(id_denunciado)
                             for id_denunciado in ids_denunciados]

        self.text_fields["ID Denunciado"].options = [
            ft.dropdown.Option(id_denunciado) for id_denunciado in opciones_dropdown]

        # Establecer el valor actual como defecto
        # Asegúrate de que este es el índice correcto
        valor_actual = str(self._get_data_value(3))
        if valor_actual in opciones_dropdown:
            self.text_fields["ID Denunciado"].value = valor_actual

        await self.text_fields["ID Denunciado"].update_async()

    async def actualizar_dropdown_denunciantes(self, id_causa):
        ids_denunciantes = await self.database.obtener_ids_denunciantes_por_causa(id_causa)
        opciones_dropdown = [str(tipo_relacion)
                             for tipo_relacion in ids_denunciantes]
        self.text_fields["ID Denunciante"].options = [
            ft.dropdown.Option(tipo_relacion) for tipo_relacion in opciones_dropdown]

        valor_actual = str(self._get_data_value(4))
        if valor_actual in opciones_dropdown:
            self.text_fields["ID Denunciante"].value = valor_actual

        await self.text_fields["ID Denunciante"].update_async()

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def _update_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_button_click(self, event):
        await self.delete_dialog.open()

    async def some_confirm_action(self):
        try:
            id_relacion = self._get_data_value(0)
            id_audencia = self._get_data_value(1)

            id_victima = int(self.text_fields["ID Víctima"].value)

            id_denunciado = int(self.text_fields["ID Denunciado"].value)
            tipo_relacion = int(self.text_fields["ID Denunciante"].value)
            victima_representante_legal = self.text_fields["Representante Legal Víctima"].value
            denunciado_representante_legal = self.text_fields["Representante Legal Denunciado"].value
            denunciante_representante_legal = self.text_fields["Representante Legal Denunciante"].value
            # Crear instancia de AudienciaRelaciones
            audiencia_preparatoria_relacion = AudienciaRelaciones(
                # Aquí debes pasar el ID de la audiencia preparatoria
                id_audiencia=id_audencia,
                id_victima=id_victima,
                id_denunciado=id_denunciado,
                tipo_relacion=tipo_relacion,
                victima_representante_legal=victima_representante_legal,
                denunciado_representante_legal=denunciado_representante_legal,
                denunciante_representante_legal=denunciante_representante_legal
            )

            if id_relacion is None or id_relacion == '':
                await self.database.add_audiencia_preparatoria_relacion(self.id_audencia, audiencia_preparatoria_relacion)
                mensaje = "Nueva relación de audiencia preparatoria agregada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)

            else:
                await self.database.update_audiencia_preparatoria_relacion(id_relacion, audiencia_preparatoria_relacion)
                mensaje = "Relación de audiencia preparatoria actualizada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')

            if self.update_tabla_audiencia_involved_callback:
                await self.update_tabla_audiencia_involved_callback()

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')

    async def some_delete_action(self, event=None):
        try:
            id_relacion = self._get_data_value(0)
            await self.database.delete_audiencia_preparatoria_relacion(id_relacion)
            mensaje = "Relación de audiencia preparatoria eliminada correctamente"

            await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

            if self.update_tabla_audiencia_involved_callback:
                await self.update_tabla_audiencia_involved_callback()

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')
