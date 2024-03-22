import flet as ft
from models.composicion_hogar import ComposicionHogar
from widgets.dialog import ConfirmationDialog
from widgets.from_card_widget import FormCardWidget
import asyncio
import unicodedata


class ScreenFormsHomeComposition(ft.UserControl):
    def __init__(self, db, page, data, id_victima=None, update_tabla_victim_callback=None, mostrar_mensaje_func=None):
        super().__init__()
        self.database = db
        self.data = data if data else []
        self.page = page
        self.text_fields = {}
        self.id_victima = id_victima
        self.update_tabla_victim_callback = update_tabla_victim_callback
        if not data:
            self.limpiar_formulario()
        self.opciones_filtradas = []
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
            "Guardar composición del hogar" if self.data else "Guardar Nueva composición del hogar",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_causa_button_click
        )

        self.home_composition_button_delete = ft.OutlinedButton(
            "Eliminar composición del hogar",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_causa_button_click,
            disabled=False if self.data else True
        )
        asyncio.create_task(self.inicializar_opciones_menu())

        self.composition_section = FormCardWidget(
            title="Detalles la composición del hogar de la Victima",
            field_groups=self._composicion_fields(self.opciones_filtradas),
            buttons=[self.home_composition_button_update,
                     self.home_composition_button_delete],
            text_fields=self.text_fields,
            page=self.page
        )

        return ft.Container(
            expand=False,
            padding=20,
            content=ft.Column(controls=[self.composition_section],
                              spacing=20)
        )

    def _composicion_fields(self, opciones_filtradas):
        fields = [
            {"type": "dropdown",
             "label": "Tipo Relación",
             "options": opciones_filtradas,
             "value": self._get_data_value(2), "col": {"md": 8}},
            {"type": "dropdown",
             "label": "Respuesta",
             "options": ['Sí', 'No', 'No Aplica', 'Sin información'],
             "value": self._get_data_value(3)},
            {"type": "text",
             "label": "cantidad",
             "value": self._get_data_value(4)},

        ]
        return fields

    async def actualizar_opciones_tipo_relacion(self, id_victima):
        # Obtener relaciones existentes de la base de datos
        relaciones_existentes_raw = await self.database.obtener_composicion_hogar_existentes(id_victima)
        # Lista completa de opciones, normalizada
        todas_las_opciones_raw = ["La víctima vive con Cónyuge", "La víctima vive con Ex-Cónyuge", "La víctima vive con Pareja", "La víctima vive con Ex-Pareja", "La víctima vive con Conviviente (con AUC)", "La víctima vive con Ex-Conviviente (con AUC)", "La víctima vive con Conviviente de hecho", "La víctima vive con Ex-Conviviente de hecho", "La víctima vive con Papá", "La víctima vive con Mamá", "La víctima vive con Padrastro", "La víctima vive con Madrastra", "La víctima vive con Hijo(s)", "La víctima vive con Hija(s)",
                                  "La víctima vive con Hijastro(s)", "La víctima vive con Hijastra(s)", "La víctima vive con Hermano(s)", "La víctima vive con Hermana(s)", "La víctima vive con Hermanastro(s)", "La víctima vive con Hermanastra(s)", "La víctima vive con Tío(s)", "La víctima vive con Tía(s)", "La víctima vive con Suegro", "La víctima vive con Suegra", "La víctima vive con Abuelo", "La víctima vive con Nieto(s)", "La víctima vive con Nieta(s)", " La víctima vive con Otro(a)"]
        todas_las_opciones = [self.normalizar_texto(
            opcion) for opcion in todas_las_opciones_raw]

        opciones_filtradas = [
            opcion for opcion in todas_las_opciones if opcion not in relaciones_existentes_raw]

        return opciones_filtradas, todas_las_opciones_raw

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

    async def inicializar_opciones_menu(self):
        opciones_filtradas, todas_las_opciones_raw = await self.actualizar_opciones_tipo_relacion(self.id_victima)
        opcion_seleted = self._get_data_value(2)
        await self.composition_section.actualizar_opciones_dropdown("Tipo Relación", opcion_seleted, opciones_filtradas, todas_las_opciones_raw)

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def some_confirm_action(self):
        try:
            id_home_composition = self._get_data_value(0)
            tipo_relacion = self.text_fields["Tipo Relación"].value
            respuesta = self.text_fields["Respuesta"].value
            cantidad = int(self.text_fields["cantidad"].value)

            home_composition = ComposicionHogar(
                id_victima=self._get_data_value(1),
                tipo_relacion=tipo_relacion,
                respuesta=respuesta,
                cantidad=cantidad
            )
            if id_home_composition is None or id_home_composition == '':
                await self.database.add_composition(self.id_victima, home_composition)
                mensaje = "Nueva composición del hogar agregada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)

            else:
                await self.database.update_composition(id_home_composition, home_composition)
                mensaje = "Composición del hogar actualizada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
            if self.update_tabla_victim_callback:
                await self.update_tabla_victim_callback()

        except ValueError as ve:
            mensaje = f"Error de valor: {str(ve)}"
            await self.mostrar_mensaje(self.page, mensaje, severidad='error')
        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error inesperado: {str(e)}", severidad='error')

    async def _update_causa_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_causa_button_click(self, event):
        await self.delete_dialog.open()

    async def some_delete_action(self, event=None):
        try:
            id_home_composition = self._get_data_value(0)

            if id_home_composition:
                await self.database.delete_composition(id_home_composition)
                mensaje = "Composición del hogar eliminada correctamente"
            else:
                raise ValueError(
                    "No se especificó un ID válido para la composición del hogar.")

            await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

            if self.update_tabla_victim_callback:
                await self.update_tabla_victim_callback()

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')
