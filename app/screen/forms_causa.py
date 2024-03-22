import flet as ft
from models.causa import Causa
from widgets.dialog import ConfirmationDialog
import asyncio
from widgets.table_widget import TablaWidget
from widgets.from_card_widget import FormCardWidget


class ScreenFormsCausa(ft.UserControl):
    def __init__(self, db, data, page, handle_route_change, nav_rail_class_2, update_tabla_causa_callback, on_causa_selected_callback, on_victima_selected_callback, on_denunciado_selected_callback, on_denunciantes_selected_callback, mostrar_mensaje_func=None):
        super().__init__()  # Llamada al constructor de la clase base
        self.data = data if data else []
        self.database = db
        self.page = page
        self.handle_route_change = handle_route_change
        self.nav_rail_class_2 = nav_rail_class_2
        self.update_tabla_causa_callback = update_tabla_causa_callback
        self.text_fields = {}
        self.on_causa_selected_callback = on_causa_selected_callback
        self.on_victima_selected_callback = on_victima_selected_callback
        self.on_denunciado_selected_callback = on_denunciado_selected_callback
        self.on_denunciantes_selected_callback = on_denunciantes_selected_callback
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
        self.causa_button_update = ft.OutlinedButton(
            "Guardar Causa" if self.data else "Guardar Nueva Causa",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_causa_button_click
        )

        self.causa_button_delete = ft.OutlinedButton(
            "Eliminar Causa",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_causa_button_click,
            disabled=False if self.data else True
        )

        causa_section = FormCardWidget(
            title="Detalles de la Causa",
            field_groups=self._causa_fields(),
            buttons=[self.causa_button_update, self.causa_button_delete],
            text_fields=self.text_fields,
            page=self.page
        ).build()

        division = ft.Container(width=1280,
                                content=ft.Divider(height=1, color="white"))
        
        self.tabla_widget_victima = TablaWidget(
            [], [], self.on_row_selected_victima, "Resumen de Victimas de la causa", "Agregar nueva victima", False if self.data else True,disabled= False if self.data else True, fixed_width=None)

        self.tabla_widget_denunciado = TablaWidget(
            [], [], self.on_row_selected_denunciado, "Resumen de Denunciados de la causa","Agregar nuevo denunciado", False if self.data else True,disabled= False if self.data else True, fixed_width=None)

        self.tabla_widget_denunciantes = TablaWidget(
            [], [], self.on_row_selected_denunciantes, "Resumen de Denunciantes de la causa","Agregar nuevo denunciante", False if self.data else True,disabled= False if self.data else True, fixed_width=None)

        # Llama a initialize_async_data para cargar los datos asíncronos y actualizar la tabla
        asyncio.create_task(self.initialize_async_data())
        
        # Usar nav_rail_class para crear rail
        rail = self.nav_rail_class_2.create_rail()
       
        main = ft.Column(
                controls=[
                    causa_section,
                    self.tabla_widget_victima,
                    self.tabla_widget_denunciado,
                    self.tabla_widget_denunciantes
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                expand=True  # Asegúrate de que main se expanda
            )

        return ft.Container(
            padding=20,
            expand=True,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[rail, main],  
                expand=True
            )
)

    def _causa_fields(self):
        fields = [
            {"type": "text",
             "label": "Digitador",
             "value": self._get_data_value(1)},
            {"type": "text",
             "label": "Rol_rit",
             "value": self._get_data_value(2)},
            {"type": "text",
             "label": "Fecha_Ingreso",
             "value": self._get_data_value(3)},
            {"type": "text",
             "label": "Cartulado",
             "value": self._get_data_value(4)},
            {"type": "dropdown",
             "label": "Procedimiento",
             "options": ["Violencia Intrafamiliar (vif)", "No aplica", "Sin informacion"],
             "value": self._get_data_value(5)},
            {"type": "dropdown",
             "label": "Materia",
             "options": ["Violencia intrafamiliar (22100)", "No aplica", "Sin informacion"],
             "value": self._get_data_value(6)},
            {"type": "dropdown",
             "label": "Estado_Admin",
             "options": ["Sin archivar", "Archivada", "No aplica", "Sin información"],
             "value": self._get_data_value(7)},
            {"type": "dropdown",
             "label": "Ubicacion",
             "options": ["Letra", "No aplica", "Sin información"],
             "value": self._get_data_value(8)},
            {"type": "dropdown",
             "label": "Cuaderno",
             "options": ["Principal", "No aplica", "Sin información"],
             "value": self._get_data_value(9)},
            {"type": "dropdown",
             "label": "Etapa",
             "options": ["Ingreso", "Demanda", "Audiencia preparatoria", "Audiencia de juicio", "Sentencia", "Terminada", "Archivada", "Cumplimiento", "Suspendida por acumulación", "No aplica", "Sin información"],
             "value": self._get_data_value(10)},
            {"type": "dropdown",
             "label": "Estado_Procesal",
             "options": ["Tramitación", "Archivado", "Con sentencia", "Concluido", "Acumulado", "No aplica", "Sin información"],
             "value": self._get_data_value(11)},
            {"type": "dropdown",
             "label": "Etapa_Actual",
             "options": ["Presentación Denuncia/Demanda", "Audiencia Preparatoria", "Audiencia de Juicio ", "Otro"],
             "value": self._get_data_value(12)},
            {"type": "dropdown",
             "label": "Via_Ingreso",
             "options": ["Denuncia", "Demanda", "No aplica", "Sin información"],
             "value": self._get_data_value(13)},
            {"type": "dropdown",
             "label": "Causa_Proteccion_Abierta",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(14)},
            {"type": "dropdown",
             "label": "Causa_Penal_Abierta",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(15)}

        ]
        return fields

    async def some_confirm_action(self, e=None):
        try:
            causa_id = self._get_data_value(0)  # Obtene el id de la causa
            causa = Causa(
                digitador=self.text_fields["Digitador"].value,
                rol_rit=self.text_fields["Rol_rit"].value,
                fecha_ingreso=self.text_fields["Fecha_Ingreso"].value,
                cartulado=self.text_fields["Cartulado"].value,
                procedimiento=self.text_fields["Procedimiento"].value,
                materia=self.text_fields["Materia"].value,
                estado_admin=self.text_fields["Estado_Admin"].value,
                ubicacion=self.text_fields["Ubicacion"].value,
                cuaderno=self.text_fields["Cuaderno"].value,
                etapa=self.text_fields["Etapa"].value,
                estado_procesal=self.text_fields["Estado_Procesal"].value,
                etapa_actual=self.text_fields["Etapa_Actual"].value,
                via_ingreso=self.text_fields["Via_Ingreso"].value,
                causa_proteccion_abierta=self.text_fields["Causa_Proteccion_Abierta"].value,
                causa_penal_abierta=self.text_fields["Causa_Penal_Abierta"].value
            )
            if causa_id is None or causa_id == '':
                mensaje = await self.database.add_causa(causa)
                mensaje = 'Causa Agregada correctamente'
                severidad = 'exito'
                await self.mostrar_mensaje(self.page, mensaje, severidad)
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)
            else:
                mensaje = await self.database.update_causa(causa_id, causa)
                mensaje = 'Causa Actualizada correctamente'
                severidad = 'exito'
                await self.mostrar_mensaje(self.page, mensaje, severidad)
            if self.update_tabla_causa_callback:
                await self.update_tabla_causa_callback()
        except ValueError as ve:
            mensaje = f"Error de valor: {str(ve)}"
            severidad = 'error'
        except Exception as e:
            mensaje = f"Error inesperado: {str(e)}"
            severidad = 'error'

    async def some_delete_action(self, event=None):
        causa_id = self._get_data_value(0)
        await self.database.delete_causa(causa_id)
        await self.mostrar_mensaje(self.page, "Causa Eliminada correctamente", severidad='exito')
        self.page.views.pop()
        top_view = self.page.views[-1]
        await self.page.go_async(top_view.route)
        if self.update_tabla_causa_callback:
            await self.update_tabla_causa_callback()

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def _update_causa_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_causa_button_click(self, event):
        await self.delete_dialog.open()

    async def get_victimas_de_causa(self):
        victim_columns = ["id_victima", "Edad", "Sexo", "estudios", "nacionalidad", "parentesco_acusado",
                          "caracter_lesion", "estado_temperancia", "comuna", "parentesco_denunciante"]
        # Obtiene el ID de la causa desde los datos actuales
        causa_id = self._get_data_value(0)
        if causa_id is not None:  # Asegúrate de que el causa_id no es None
            data_victima = await self.database.get_victimas_by_causa(victim_columns, causa_id)
            return data_victima, victim_columns
        else:
            await self.mostrar_mensaje(self.page, "No se ha podido obtener el ID de la causa.", severidad='error')

    async def get_denunciado_de_causa(self):
        denunciado_columns = ["id_denunciado", "edad", "sexo", "nacionalidad", "profesion_oficio",
                              "temperancia_otro", "comuna", "nivel_riesgo", "vif_numero"]
        # Obtiene el ID de la causa desde los datos actuales
        causa_id = self._get_data_value(0)
        if causa_id is not None:  # Asegúrate de que el causa_id no es None
            data_denunciado = await self.database.get_denunciados_by_causa(denunciado_columns, causa_id)
            return data_denunciado, denunciado_columns
        else:
            await self.mostrar_mensaje(self.page, "No se ha podido obtener el ID de la causa.", severidad='error')

    async def get_denunciante(self):
        denunciante_columns = ["tipo_relacion", "es_denunciante_victima",
                               "es_denunciante_persona_juridica", "Edad_Denunciante",
                               "Sexo_Denunciante", "Nacionalidad_Denunciante", "edad_denunciante"]
        causa_id = self._get_data_value(0)
        data = await self.database.get_denunciantes_by_causa(denunciante_columns, causa_id)
        return (data, denunciante_columns)

    async def initialize_async_data(self):
        data_victima, columns_victima = await self.get_victimas_de_causa()
        data_denunciado, denunciado_columns = await self.get_denunciado_de_causa()
        data_denunciantes, denunciante_columns = await self.get_denunciante()

        await self.tabla_widget_victima.update_table(data_victima, columns_victima)
        await self.tabla_widget_denunciado.update_table(data_denunciado, denunciado_columns)
        await self.tabla_widget_denunciantes.update_table(data_denunciantes, denunciante_columns)

    # En ScreenFormsCausa o en la pantalla donde tengas la lista de víctimas

    async def on_row_selected_victima(self, selected_id):
        victima_data = await self.database.get_victima_by_id(selected_id)
        victima_info = (selected_id, victima_data)
        await self.on_victima_selected_callback(victima_info)
        await self.page.go_async('/formulario_victima')

    async def on_row_selected_denunciado(self, selected_id):
        denunciado_data = await self.database.get_denunciado_by_id(selected_id)
        denunciado_info = (selected_id, denunciado_data)
        await self.on_denunciado_selected_callback(denunciado_info)
        await self.page.go_async('/formulario_denunciado')

    async def on_row_selected_denunciantes(self, selected_id):
        denunciado_data = await self.database.get_denunciantes_by_id(selected_id)
        denunciantes_info = (selected_id, denunciado_data)
        await self.on_denunciantes_selected_callback(denunciantes_info)
        await self.page.go_async('/formulario_denunciante')
