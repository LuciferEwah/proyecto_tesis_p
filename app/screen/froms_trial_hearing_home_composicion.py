import flet as ft
from widgets.dialog import ConfirmationDialog
from widgets.from_card_widget import FormCardWidget
from models.composicion_hogar import ComposicionHogarEnJuicio
import asyncio
import unicodedata


class ScreenCompositionHogarEnJuicio(ft.UserControl):
    def __init__(self, db, page, data, id_juicio, id_causa, update_tabla_trial_hearing_callback=None, mostrar_mensaje_func=None):
        super().__init__()
        self.database = db
        self.data = data if data else []
        self.page = page
        self.text_fields = {}
        self.id_juicio = id_juicio
        self.id_causa = id_causa
        self.update_tabla_trial_hearing_callback = update_tabla_trial_hearing_callback
        if not data:
            self.limpiar_formulario()
        self.opciones_filtradas = []
        self.opciones_victimas = []
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

        self.button_update = ft.OutlinedButton(
            "Guardar composición hogar actual" if self.data else "Guardar Nueva composición hogar actual",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_button_click
        )

        self.button_delete = ft.OutlinedButton(
            "Eliminar composición hogar actual",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_button_click,
            disabled=False if self.data else True
        )

        self.juicio_involved_section = FormCardWidget(
            title="Detalles de la composición del hogar actual en la Audiencia de Juicio",
            field_groups=self._composicion_hogar_fields(
                self.opciones_filtradas, self.opciones_victimas),
            buttons=[self.button_update, self.button_delete],
            text_fields=self.text_fields,
            page=self.page
        )
        asyncio.create_task(self.actualizar_dropdown_victimas(self.id_causa))
        return ft.Container(
            expand=False,
            padding=20,
            content=ft.Column(
                controls=[self.juicio_involved_section], spacing=20)
        )

    async def on_id_victima_change(self, event):
        id_victima = event.control.value
        if id_victima.isdigit():
            opciones_filtradas, todas_las_opciones_raw = await self.actualizar_tipo_relacion(int(id_victima), self.id_juicio)

            opcion_seleted = self._get_data_value(3)
            await self.juicio_involved_section.actualizar_opciones_dropdown("Tipo de Relación", opcion_seleted, opciones_filtradas, todas_las_opciones_raw)

    async def _update_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_button_click(self, event):
        await self.delete_dialog.open()

    def _composicion_hogar_fields(self, opciones_filtradas, opciones_de_victimas):
        fields = [
            {
                "type": "dropdown",
                "label": "ID Víctima",
                "options": opciones_de_victimas,
                "value": self._get_data_value(2),
                "on_change": self.on_id_victima_change
            },
            {
                "type": "dropdown",
                "label": "Tipo de Relación",
                "options": opciones_filtradas,
                "value": self._get_data_value(3),
                "col": {"md": 8}
            },
            {
                "type": "dropdown",
                "label": "Respuesta",
                "options": ['Sí', 'No', 'No Aplica', 'Sin información'],
                "value": self._get_data_value(4)},
            {
                "type": "int",
                "label": "cantidad",
                "value": self._get_data_value(5)
            },
        ]
        return fields

    async def actualizar_dropdown_victimas(self, id_causa):
        ids_victimas = await self.database.obtener_ids_victimas_por_causa(id_causa)
        opciones_dropdown = [str(id_victima) for id_victima in ids_victimas]

        self.text_fields["ID Víctima"].options = [
            ft.dropdown.Option(id_victima) for id_victima in opciones_dropdown]

        valor_actual = str(self._get_data_value(2))
        if valor_actual in opciones_dropdown:
            self.text_fields["ID Víctima"].value = valor_actual
            # Aquí añades la lógica para actualizar automáticamente el tipo de relación
            opciones_filtradas, todas_las_opciones_raw = await self.actualizar_tipo_relacion(int(valor_actual), self.id_juicio)
            opcion_selected = self._get_data_value(3)
            await self.juicio_involved_section.actualizar_opciones_dropdown("Tipo de Relación", opcion_selected, opciones_filtradas, todas_las_opciones_raw)

        await self.text_fields["ID Víctima"].update_async()

    async def actualizar_tipo_relacion(self, id_victima, id_juicio):
        # Obtener relaciones existentes de la base de datos
        relaciones_existentes_raw = await self.database.obtener_tipos_relacion_composicion_hogar_por_juicio(id_victima, id_juicio)
        # Lista completa de opciones, normalizada
        todas_las_opciones_raw = ["La víctima vive con Cónyuge", "La víctima vive con Ex-Cónyuge", "La víctima vive con Pareja", "La víctima vive con Ex-Pareja", "La víctima vive con Conviviente (con AUC)", "La víctima vive con Ex-Conviviente (con AUC)", "La víctima vive con Conviviente de hecho", "La víctima vive con Ex-Conviviente de hecho", "La víctima vive con Papá", "La víctima vive con Mamá", "La víctima vive con Padrastro", "La víctima vive con Madrastra", "La víctima vive con Hijo(s)", "La víctima vive con Hija(s)",
                                  "La víctima vive con Hijastro(s)", "La víctima vive con Hijastra(s)", "La víctima vive con Hermano(s)", "La víctima vive con Hermana(s)", "La víctima vive con Hermanastro(s)", "La víctima vive con Hermanastra(s)", "La víctima vive con Tío(s)", "La víctima vive con Tía(s)", "La víctima vive con Suegro", "La víctima vive con Suegra", "La víctima vive con Abuelo", "La víctima vive con Nieto(s)", "La víctima vive con Nieta(s)", " La víctima vive con Otro(a)"]

        todas_las_opciones = [self.normalizar_texto(
            opcion) for opcion in todas_las_opciones_raw]

        opciones_filtradas = [
            opcion for opcion in todas_las_opciones if opcion not in relaciones_existentes_raw]

        return opciones_filtradas, todas_las_opciones_raw

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def some_confirm_action(self):
        try:
            id_composicion = self._get_data_value(0)
            id_victima = int(self.text_fields["ID Víctima"].value)
            tipo_relacion = self.text_fields["Tipo de Relación"].value
            respuesta = self.text_fields["Respuesta"].value
            cantidad = int(self.text_fields["cantidad"].value)

            composicion_hogar_en_juicio = ComposicionHogarEnJuicio(
                id_audiencia_juicio=self.id_juicio,
                id_victima=id_victima,
                tipo_relacion=tipo_relacion,
                respuesta=respuesta,
                cantidad=cantidad
            )

            if id_composicion is None or id_composicion == '':
                await self.database.add_composicion_hogar_en_juicio(self.id_juicio, composicion_hogar_en_juicio)
                mensaje = "Nueva composición de hogar en juicio agregada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)

            else:
                await self.database.update_composicion_hogar_en_juicio(id_composicion, composicion_hogar_en_juicio)
                mensaje = "Composición de hogar en juicio actualizada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
            if self.update_tabla_trial_hearing_callback:
                await self.update_tabla_trial_hearing_callback()

        except ValueError as ve:
            mensaje = f"Error de valor: {str(ve)}"
            await self.mostrar_mensaje(self.page, mensaje, severidad='error')
        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error inesperado: {str(e)}", severidad='error')

    async def some_delete_action(self, event=None):
        try:
            id_relacion = self._get_data_value(0)
            await self.database.delete_composicion_hogar_en_juicio(id_relacion)
            mensaje = "Composición de hogar en juicio eliminada correctamente"

            await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

            if self.update_tabla_trial_hearing_callback:
                await self.update_tabla_trial_hearing_callback()

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error al eliminar: {str(e)}", severidad='error')

    def normalizar_texto(self, texto):
        if texto is None:
            return ""
        texto = texto.strip()
        texto = texto.replace('años', 'anio')
        texto_normalizado = unicodedata.normalize('NFD', texto)
        texto_sin_tildes = ''.join(
            c for c in texto_normalizado if unicodedata.category(c) != 'Mn').lower()
        texto_sin_tildes = texto_sin_tildes.replace('ñ', 'n')

        return texto_sin_tildes
