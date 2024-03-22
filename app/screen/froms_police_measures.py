import flet as ft
from models.medida_cautelar import MedidaCautelarEspecial
from widgets.dialog import ConfirmationDialog
from widgets.from_card_widget import FormCardWidget
import asyncio
import unicodedata


class ScreenMedidasPoliciales(ft.UserControl):
    def __init__(self, db, page, data, id_antecedentes_policial, update_tabla_antecedentes_policiales_callback, mostrar_mensaje_func=None):
        super().__init__()
        self.database = db
        self.page = page
        self.data = data if data else []
        self.id_antecedentes_policial = id_antecedentes_policial
        self.text_fields = {}
        self.update_tabla_antecedentes_policiales_callback = update_tabla_antecedentes_policiales_callback
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

        self.button_update = ft.OutlinedButton(
            "Guardar Medida Policial" if self.data else "Guardar Nueva Medida Policial",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_button_click
        )

        self.button_delete = ft.OutlinedButton(
            "Eliminar Medida Policial",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_button_click,
            disabled=False if self.data else True
        )
        asyncio.create_task(self.inicializar_opciones_menu())
        self.medida_policial_section = FormCardWidget(
            title="Detalles de la Medida Policial",
            field_groups=self._medida_policial_fields(self.opciones_filtradas),
            buttons=[self.button_update, self.button_delete],
            text_fields=self.text_fields,
            page=self.page,
            width=1900,

        )

        return ft.Container(
            expand=False,
            padding=20,
            content=ft.Column(
                controls=[self.medida_policial_section], spacing=20)
        )

    def _medida_policial_fields(self, opciones_filtradas):
        fields = [
            {"type": "dropdown",
             "label": "Tipo de Medida",
             "options": opciones_filtradas,
             "value": self._get_data_value(2), "col": {"md": 14}},
            {"type": "dropdown",
             "label": "Respuesta",
             "options": ['Sí', 'No', 'No Aplica', 'Sin información'],
             "value": self._get_data_value(3)},
            {"type": "dropdown",
             "label": "plazo",
             "options": ["Indefinido", "30 días", "60 días", "90 días", "180 días", "Más de 180 días", "No aplica", "Sin información"],
             "value": self._get_data_value(4)},      
             {"type": "text",
            "label": "Interpone Recurso",
            "value": self._get_data_value(5)},
            {"type": "text",
            "label": "Demanda Reconvencional",
            "value": self._get_data_value(6)}
        ]
        return fields

    async def actualizar_tipos_de_medidas(self, id_antecedentes_policial):
        # Obtener relaciones existentes de la base de datos
        relaciones_existentes_raw = await self.database.obtener_tipos_medidas_policiales_por_antecedente(id_antecedentes_policial)

        todas_las_opciones_raw = ["Rondas periódicas al domicilio de la Víctima", "Teléfono prioritario del plan cuadrante", "Prohibición de acercarse a la víctima", "Prohibir o restringir la presencia del ofensor en el hogar común y domicilio, lugar de estudios o trabajo de la víctima, así como cualquier otra lugar en que la víctima permanezca, concurra o visite habitualmente", "Asegurar la entrega material de los efectos personales de la víctima que optare por no regresar al hogar común", "Fijar alimentos provisorios", "Medidas Cautelares: Determinar un régimen provisorio de cuidado personal de NNA, en conformidad al artículo 225 del Código Civil, y establecer la forma en que se mantenrá una relación directa y regular entre los progenitores y sus hijos",
                                  "Medidas Cautelares: Decretar la prohibición de celebrar actos o contratos", "Medidas Cautelares: Prohibir el porte y tenencia de cualquier arma de fuego, municiones y cartuchos", "Decretar la reserva de la identidad del tercero denunciante", "Establecer medidas de protección para adultos mayores o personas afectadas por alguna incapacidad o discapacidad", "Asistencia obligatoria a programas terapeuticos o de orientación familiar", "Obligación de presentarse regularmente a la unidad policial que determine el juez", "Otra medida cautelar"]
        todas_las_opciones = [self.normalizar_texto(
            opcion) for opcion in todas_las_opciones_raw]

        opciones_filtradas = [
            opcion for opcion in todas_las_opciones if opcion not in relaciones_existentes_raw]

        return opciones_filtradas, todas_las_opciones_raw

    async def inicializar_opciones_menu(self):
        opciones_filtradas, todas_las_opciones_raw = await self.actualizar_tipos_de_medidas(self.id_antecedentes_policial)
        opcion_seleted = self._get_data_value(2)
        await self.medida_policial_section.actualizar_opciones_dropdown("Tipo de Medida", opcion_seleted, opciones_filtradas, todas_las_opciones_raw)

    async def some_confirm_action(self):
        try:
            id_medida_policial = self._get_data_value(0)
            id_antecedentes_policial = self._get_data_value(1)

            tipo_medida = self.text_fields["Tipo de Medida"].value
            respuesta = self.text_fields["Respuesta"].value
            plazo = self.text_fields["plazo"].value
            interpone_recurso = self.text_fields["Interpone Recurso"].value
            demanda_reconvencional = self.text_fields["Demanda Reconvencional"].value

            medida_policial = MedidaCautelarEspecial(
                id_evento=id_antecedentes_policial,
                tipo_medida=tipo_medida,
                respuesta=respuesta,
                plazo=plazo,
                interpone_recurso=interpone_recurso,
                demanda_reconvencional=demanda_reconvencional
            )

            if id_medida_policial is None or id_medida_policial == '':
                await self.database.add_medida_policial(self.id_antecedentes_policial, medida_policial)
                mensaje = "Nueva medida policial agregada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)

            else:
                await self.database.update_medida_policial(id_medida_policial, medida_policial)
                mensaje = "Medida policial actualizada correctamente"
                await self.mostrar_mensaje(self.page, mensaje, severidad='exito')

            if self.update_tabla_antecedentes_policiales_callback:
                await self.update_tabla_antecedentes_policiales_callback()

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')

    async def some_delete_action(self, event=None):
        try:
            id_medida_policial = self._get_data_value(0)
            await self.database.delete_medida_policial(id_medida_policial)
            mensaje = "Medida policial eliminada correctamente"

            await self.mostrar_mensaje(self.page, mensaje, severidad='exito')
            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

            if self.update_tabla_antecedentes_policiales_callback:
                await self.update_tabla_antecedentes_policiales_callback()

        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error: {str(e)}", severidad='error')

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def _update_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_button_click(self, event):
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
