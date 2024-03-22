import flet as ft
from widgets.dialog import ConfirmationDialog
from widgets.from_card_widget import FormCardWidget
from models.antecedentes_denunciado import AntecedentesDenunciado
import asyncio
import unicodedata


class ScreenFormsBackgroundDenounced(ft.UserControl):
    def __init__(self, db, page, data, id_denounced, update_tabla_denounced_callback, mostrar_mensaje_func=None):
        super().__init__()
        self.database = db
        self.data = data if data else []
        self.page = page
        self.id_denounced = id_denounced
        self.text_fields = {}
        self.update_tabla_denounced_callback = update_tabla_denounced_callback
        self.mostrar_mensaje = mostrar_mensaje_func
        if not data:
            self.limpiar_formulario()
        self.opciones_filtradas = []

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
            "Guardar antecedente" if self.data else "Guardar Nuevo antecedente",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_button_click
        )

        self.button_delete = ft.OutlinedButton(
            "Eliminar antecedente",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_button_click,
            disabled=False if self.data else True
        )

        asyncio.create_task(self.inicializar_opciones_menu())
        self.form_section = FormCardWidget(
            title="Detalles de los antecedentes del denunciado",
            field_groups=self._background_denounced_fields(
                self.opciones_filtradas),
            buttons=[self.button_update, self.button_delete],
            text_fields=self.text_fields,
            page=self.page
        )

        return ft.Container(
            expand=False,
            padding=20,
            content=ft.Column(controls=[self.form_section],
                              spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    def _background_denounced_fields(self, opciones_filtradas):
        fields = [
            {"type": "dropdown",
             "label": "Tipo Antecedente",
             "options": opciones_filtradas,
             "value": self._get_data_value(2), "col": {"md": 8}},
            {"type": "dropdown",
             "label": "Repuesta",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(3)}

        ]
        return fields

    async def actualizar_opciones_tipo_antecedentes(self, id_denounced):
        # Obtener relaciones existentes de la base de datos
        relaciones_existentes_raw = await self.database.obtener_antecedentes_denunciado(id_denounced)
        todas_las_opciones_raw = ["Aborto", "Abandono de niños y personas desvalidas", "Violación", "Estupro", "Abuso sexual", " Pornografía", "Prostitución de menores", "Incesto", "Parricidio", "Femicidio", "Homicidio", "Infanticidio", "Lesiones corporales",
                                  "Maltrato a menores de 18 años, adultos mayores o personas en situación de discapacidad", "Tráfico ilícito de migrantes", "Trata de personas", "Robo", "Hurto", "Estafa", "Incendio", "Tráfico ilícito de estupefacientes y sustancias psicotrópicas", "Registro especial de condenas por VIF"]
        todas_las_opciones = [self.normalizar_texto(
            opcion) for opcion in todas_las_opciones_raw]

        opciones_filtradas = [
            opcion for opcion in todas_las_opciones if opcion not in relaciones_existentes_raw]

        return opciones_filtradas, todas_las_opciones_raw

    async def inicializar_opciones_menu(self):
        opciones_filtradas, todas_las_opciones_raw = await self.actualizar_opciones_tipo_antecedentes(self.id_denounced)
        opcion_seleted = self._get_data_value(2)
        await self.form_section.actualizar_opciones_dropdown("Tipo Antecedente", opcion_seleted, opciones_filtradas, todas_las_opciones_raw)

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def some_confirm_action(self):
        try:
            id_antecedentes = self._get_data_value(0)
            tipo_antecedente = self.text_fields["Tipo Antecedente"].value
            descripcion = self.text_fields["Repuesta"].value

            antecedentes_denunciado = AntecedentesDenunciado(
                id_denunciado=self._get_data_value(1),
                tipo_antecedente=tipo_antecedente,
                descripcion=descripcion
            )

            if id_antecedentes is None or id_antecedentes == '':
                mensaje = await self.database.add_antecedentes_denunciado(self.id_denounced, antecedentes_denunciado)
                mensaje = "Nuevo antecedente del denunciado agregados correctamente"
                severidad = 'exito'
                await self.mostrar_mensaje(self.page, mensaje, severidad)
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)
            else:
                mensaje = await self.database.update_antecedentes_denunciado(id_antecedentes, antecedentes_denunciado)
                mensaje = "Antecedente del denunciado actualizado correctamente"
                severidad = 'exito'
                await self.mostrar_mensaje(self.page, mensaje, severidad)
            if self.update_tabla_denounced_callback:
                await self.update_tabla_denounced_callback()
        except ValueError as ve:
            mensaje = f"Error de valor: {str(ve)}"
            severidad = 'error'
        except Exception as e:
            mensaje = f"Error inesperado: {str(e)}"
            severidad = 'error'

    async def _update_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_button_click(self, event):
        await self.delete_dialog.open()

    async def some_delete_action(self, event=None):
        try:
            id_antecedentes = self._get_data_value(0)
            await self.database.delete_antecedentes_denunciado(id_antecedentes)

            # Mostrar mensaje de confirmación
            mensaje = "Antecedentes del denunciado eliminados correctamente"
            severidad = 'exito'
            await self.mostrar_mensaje(self.page, mensaje, severidad)

            # Ejecutar callbacks
            if self.update_tabla_denounced_callback:
                await self.update_tabla_denounced_callback()

            # Redirigir a la vista anterior
            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

        except Exception as e:
            # Mostrar mensaje de error si algo sale mal
            mensaje_error = f"Error al eliminar antecedentes del denunciado: {str(e)}"
            await self.mostrar_mensaje(self.page, mensaje_error, 'error')

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
