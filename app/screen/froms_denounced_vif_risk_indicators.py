import flet as ft
from models.denunciado_vif import DenunciadoIndicadoresRiesgoVIF
from widgets.dialog import ConfirmationDialog
from widgets.from_card_widget import FormCardWidget
import asyncio
import unicodedata


class ScreenFormsVifRiskIndicators(ft.UserControl):
    def __init__(self, db, page, data, id_denunciado, update_tabla_denounced_callback, mostrar_mensaje_func=None):
        super().__init__()
        self.database = db
        self.page = page
        self.data = data if data else []
        self.id_denunciado = id_denunciado
        self.text_fields = {}
        self.update_tabla_denounced_callback = update_tabla_denounced_callback
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
            "Guardar" if self.data else "Guardar Nuevo Riesgo VIF",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_causa_button_click
        )

        self.home_composition_button_delete = ft.OutlinedButton(
            "Eliminar",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_causa_button_click,
            disabled=False if self.data else True
        )

        asyncio.create_task(self.inicializar_opciones_menu())
        self.composition_section = FormCardWidget(
            title="Detalles del indicador riesgo vif del denunciado",
            field_groups=self._indicadores_fields(self.opciones_filtradas),
            buttons=[self.home_composition_button_update,
                     self.home_composition_button_delete],
            text_fields=self.text_fields,
            page=self.page
        )

        return ft.Container(
            expand=False,
            padding=20,
            content=ft.Column(controls=[self.composition_section],
                              spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    def _indicadores_fields(self, opciones_filtradas):
        fields = [
            {"type": "dropdown",
             "label": "Descripción del Indicador",
             "options": opciones_filtradas,
             "value": self._get_data_value(2), "col": {"md": 14}},
            {"type": "dropdown",
             "label": "Respuesta",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(3)}
        ]
        return fields

    async def actualizar_opciones_indicadores_vif(self, id_denunciado):
        # Obtener relaciones existentes de la base de datos
        relaciones_existentes_raw = await self.database.obtener_descripciones_indicadores_riesgo(id_denunciado)
        # Lista completa de opciones, normalizada
        todas_las_opciones_raw = ["¿Tiene hijos menores de 18 años?", "¿El denunciado le golpeó o intentó golpear en esta oportunidad?", "¿Le provocó lesiones tales como, moretones, arañazos u otras?", "Amenazas de muerte", "¿Utilizó un arma contra usted? (armas de fuego, arma blanca u objeto contundente)", "¿le violentó o intentó violentar sexualmente?", "¿Tiene acceso a armas de fuego?", "¿Consume él/ella alcohol y/o drogas?", "¿Le golpea cuando consume alcohol y/o drogas?", "¿Se le ha diagnosticado algún trastorno psiquiátrico?", " ¿Él/ella le ha golpeado anteriormente?", "¿Ha aumentado la freuencia o gravedad de los golpes en los últimos 3 meses?", "¿Le ha amenzado con arma de fuego, arma blanca u otros objetos con anterioridad?", "¿Con anterioridad a esta denuncia, él/ella le ha amenazado de muerte?", "¿Ha golpeado a menores de edad de la familia, otros familiares o conocidos recientemente?", " ¿Esta persona presenta celos violentos?", " ¿Está separada(o)/divorciada(o) de esta persona, o esta en proceso de separación/divorcio?", "La persona denunciada ¿Se niega a aceptar esta separación/divorcio?", "¿Tiene alguna discapacidad que le dificulte protegerse?",
                                  "¿Está embarazada?", "¿Vive con el denunciado(a)?", "¿Depende económicamente del denunciado(a)?", "usted: ¿Depende económicamente del denunciado(a)?", "Respecto a lo contado: ¿Cree que el denunciado(a) le agredirá si sabe de la denuncia?", "¿Cree que pueda matarle a usted o a alguien de su familia?", "¿Tiene el imputado(a) otras denuncias por VIF?", "¿Tiene el imputado(a) condenas por VIF?", " ¿Registra el imputado(a) denuncias o condenas por desacato en VIF?", "¿Tiene el imputado(a) condenas o procesos pendientes por a) Crimen o simple delito contra las personas?", "¿Tiene el imputado(a) condenas o procesos pendientes por b) Violación, estupro, u otros delitos sexuales de los párrafos 5 y 6 del título VII, libro II CP?", "¿Tiene el imputado(a) condenas o procesos pendientes por: c) Infracciones de la ley 17.798 sobre control de armas?", "¿Tiene el imputado(a) condenas o procesos pendientes por d) Amenazas?", "¿Tiene el imputado(a) condenas o procesos pendientes por: e) Robo con violencia?", "¿Tiene el imputado(a) condenas o procesos pendientes por: f) Aborto con violencia?"]
        todas_las_opciones = [self.normalizar_texto(
            opcion) for opcion in todas_las_opciones_raw]

        opciones_filtradas = [
            opcion for opcion in todas_las_opciones if opcion not in relaciones_existentes_raw]

        return opciones_filtradas, todas_las_opciones_raw

    async def inicializar_opciones_menu(self):
        opciones_filtradas, todas_las_opciones_raw = await self.actualizar_opciones_indicadores_vif(self.id_denunciado)
        opcion_seleted = self._get_data_value(2)
        await self.composition_section.actualizar_opciones_dropdown("Descripción del Indicador", opcion_seleted, opciones_filtradas, todas_las_opciones_raw)

    async def some_confirm_action(self):
        try:
            id_riesgo_vif = self._get_data_value(0)
            descripcion_indicador = self.text_fields["Descripción del Indicador"].value
            respuesta = self.text_fields["Respuesta"].value

            indicador_riesgo_vif = DenunciadoIndicadoresRiesgoVIF(
                id_denunciado=self._get_data_value(1),
                descripcion_indicador=descripcion_indicador,
                respuesta=respuesta
            )
            if id_riesgo_vif is None or id_riesgo_vif == '':
                await self.database.add_indicador_riesgo_vif(self.id_denunciado, indicador_riesgo_vif)
                mensaje = "Nuevo indicador de riesgo VIF agregado correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')

                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)

            else:
                await self.database.update_indicador_riesgo_vif(id_riesgo_vif, indicador_riesgo_vif)
                mensaje = "Indicador de riesgo VIF actualizado correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')

            if self.update_tabla_denounced_callback:
                await self.update_tabla_denounced_callback()

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')

    async def some_delete_action(self, event=None):
        try:
            id_riesgo_vif = self._get_data_value(0)
            await self.database.delete_indicador_riesgo_vif(id_riesgo_vif)
            mensaje = "Indicador de riesgo VIF eliminado correctamente"

            await self.mostrar_mensaje(self.page, mensaje, severidad='exito')

            if self.update_tabla_denounced_callback:
                await self.update_tabla_denounced_callback()

            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def _update_causa_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_causa_button_click(self, event):
        await self.delete_dialog.open()

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
