import flet as ft
from models.denunciado import Denunciado
from widgets.dialog import ConfirmationDialog
import asyncio
from widgets.table_widget import TablaWidget
from widgets.from_card_widget import FormCardWidget
from models.antecedentes_denunciado import AntecedentesDenunciado
from models.denunciado_vif import DenunciadoIndicadoresRiesgoVIF
import numpy as np
import pandas as pd




class ScreenFormsDenunciado(ft.UserControl):
    def __init__(self, db, data, page, id_causa, update_tabla_causa_callback, update_card_dashboard, on_background_denounced_selected_callback, on_vif_denounced_selected_callback, mostrar_mensaje_func=None):
        super().__init__()
        self.data = data if data else []
        self.database = db
        self.page = page
        self.text_fields = {}
        self.id_causa = id_causa
        self.update_tabla_causa_callback = update_tabla_causa_callback
        self.update_card_dashboard = update_card_dashboard
        self.on_background_denounced_selected_callback = on_background_denounced_selected_callback
        self.on_vif_denounced_selected_callback = on_vif_denounced_selected_callback
        self.mostrar_mensaje = mostrar_mensaje_func
        if not data:
            self.limpiar_formulario()


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
        self.causa_button_update = ft.OutlinedButton(
            "Guardar denunciado" if self.data else "Guardar Nuevo Denunciado",
            icon=ft.icons.SAVE,
            icon_color="green400",
            on_click=self._update_causa_button_click
        )

        self.causa_button_delete = ft.OutlinedButton(
            "Eliminar denunciado",
            icon=ft.icons.DELETE,
            icon_color="red400",
            on_click=self._delete_causa_button_click,
            disabled=False if self.data else True
        )

        causa_section = FormCardWidget(
            title="Detalles del denunciado",
            field_groups=self._denunciado_fields(),
            buttons=[self.causa_button_update, self.causa_button_delete],
            text_fields=self.text_fields,
            page=self.page,
            width=1280
        ).build()

        self.tabla_widget_background_denounced = TablaWidget(
            [], [], self.on_row_selected_background_denounced, "Antecedentes del denunciado","Agregar nuevo antecedente", False if self.data else True, disabled= False if self.data else True, fixed_width=None)
        self.tabla_widget_vif_indicators = TablaWidget(
            [], [], self.on_row_selected_vif_indicators, "Riesgo VIF del denunciado", "Agregar nuevo riesgo VIF", False if self.data else True, disabled= False if self.data else True,fixed_width=None)
        # Llama a initialize_async_data para cargar los datos asíncronos y actualizar la tabla
        asyncio.create_task(self.initialize_async_data())

 
        fila_superior = ft.Row(
            controls=[causa_section],
            spacing=20,
            vertical_alignment= ft.CrossAxisAlignment.START
        )

        # Columna principal con la fila superior y la tabla debajo
        return ft.Column(
            controls=[
                fila_superior,
                self.tabla_widget_background_denounced, 
                self.tabla_widget_vif_indicators # Asegúrate de que este widget esté correctamente inicializado
            ],
            spacing=20  # Espacio entre los elementos de la columna
        )

    def _denunciado_fields(self):
        fields = [

            {"type": "int",
             "label": "Edad",
             "value": self._get_data_value(2)},
            {"type": "dropdown",
             "label": "Sexo",
             "options": ["Femenino", "Masculino", "No aplica", "Sin información"],
             "value": self._get_data_value(3)},
            {"type": "dropdown",
             "label": "Nacionalidad",
             "options": ["Chilena", "Extranjera", "Sin información", "No aplica"],
             "value": self._get_data_value(4)},
            {"type": "text",
             "label": "Nacionalidad Extranjera",
             "value": self._get_data_value(5)},
            {"type": "dropdown",
             "label": "Profesión/Oficio",
             "options": ["Estudiante", "Dueña(o) de hogar", "Empleado(a)", "Desempleado(a)", "Otra ocupación", "Jubilado(a)/Pensionado(a)", "Sin ocupación/oficio", "No aplica", "Sin información"],
             "value": self._get_data_value(6)},

            {"type": "dropdown",
             "label": "Estudios",
             "options":  ["No aplica", "Sin info", "Nunca asistió", "Diferencial", "Sala Cuna", "Jardín Inf", "Prekínder/Kínder", "Básica Inc", "Básica Comp", "Media Inc", "Media Comp", "Técnico Profesional Inc", "Técnico Profesional Comp", "Profesional Inc", "Profesional Comp", "Posgrado Inc", "Posgrado Com"],
             "value": self._get_data_value(7)},
            {"type": "dropdown",
             "label": "Presencia de Lesiones",
             "options": ["Sin lesiones", "Con lesiones", "No aplica", "Sin información"],
             "value": self._get_data_value(8)},
            {"type": "dropdown",
             "label": "Descripción de Lesiones",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(9)},
            {"type": "dropdown",
             "label": "Estado de Temperancia",
             "options": ["Estado Normal", "Otro", "No aplica", "Sin información"],
             "value": self._get_data_value(10)},
            {"type": "text",
             "label": "Temperancia Otro",
             "value": self._get_data_value(11)},
            {"type": "text",
             "label": "Descripción de Temperancia",
             "options": ["Sí", "No", "No aplica", "Sin información"],
             "value": self._get_data_value(12)},
            {"type": "text",
             "label": "Otros Antecedentes",
             "value": self._get_data_value(13)},
            {"type": "dropdown",
             "label": "Comuna",
             "options": ["Alhué", "Buin", "Calera de Tango", "Cerrillos", "Cerro Navia", "Colina", "Conchalí", "Curacaví", "El Bosque", "El Monte", "Estación Central", "Huechuraba", "Independencia", "Isla de Maipo", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Lampa", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú", "María Pinto", "Melipilla", "Padre Hurtado", "Paine", "Pedro Aguirre Cerda", "Peñaflor", "Peñalolén", "Pirque", "Providencia", "Pudahuel", "Puente Alto", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Bernardo", "San Joaquín", "San José de Maipo", "San Miguel", "San Pedro", "San Ramón", "Santiago", "Talagante", "Tiltil", "Vitacura", "Ñuñoa"],
             "value": self._get_data_value(14)},
            {"type": "dropdown",
             "label": "Estado Civil",
             "options": ["Casado/a", "Conviviente/Pareja (Sin AUC)", "Conviviente/Pareja (Con AUC)", "Anulado/a", "Separado/a", "Divorciado/a", "Viudo/a", "Soltero/a", "No aplica", "Sin información"],
             "value": self._get_data_value(15)},
            {"type": "dropdown",
             "label": "Nivel de Riesgo",
             "options": ["Alto", "Medio", "Bajo", "No aplica", "Sin información"],
             "value": self._get_data_value(16)},
            {"type": "float",
             "label": "Número VIF",
             "value": self._get_data_value(17)}

        ]
        return fields

    def _get_data_value(self, index):
        return self.data[index] if len(self.data) > index else ""

    async def _update_causa_button_click(self, event):
        await self.confirm_dialog.open()

    async def _delete_causa_button_click(self, event):
        await self.delete_dialog.open()

    async def get_background_denounced(self):
        # Define las columnas que deseas obtener de la composición familiar
        composicion_columns = [
            "id_antecedente", "tipo_antecedente", "descripcion"]
        denunciado_id = self._get_data_value(0)
        if denunciado_id is not None:  # Asegúrate de que el victima_id no es None
            result = await self.database.get_antecedentes_by_denunciado_id(composicion_columns, denunciado_id)
            return result, composicion_columns
        else:
            print("No se ha podido obtener el ID de la víctima.")

    async def get_vif_indicators(self):
        # Define las columnas que deseas obtener de la composición familiar
        composicion_columns = [
            "id_riesgo_vif", "descripcion_indicador", "respuesta"]
        denunciado_id = self._get_data_value(0)
        if denunciado_id is not None:  # Asegúrate de que el victima_id no es None
            result = await self.database.get_indicadores_riesgo_vif_by_denunciado_id(composicion_columns, denunciado_id)
            return result, composicion_columns
        else:
            print("No se ha podido obtener el ID de la víctima.")

    async def initialize_async_data(self):
        # Obtener y actualizar los antecedentes
        data_background, columns_background = await self.get_background_denounced()
        await self.tabla_widget_background_denounced.update_table(data_background, columns_background)

        # Obtener y actualizar los indicadores VIF
        data_vif, columns_vif = await self.get_vif_indicators()
        await self.tabla_widget_vif_indicators.update_table(data_vif, columns_vif)

        # Actualizar la página
        await self.page.update_async()


    async def on_row_selected_background_denounced(self, selected_id):
        background_denounced_data = await self.database.get_antecedente_by_id(selected_id)
        background_denounced_info = (selected_id, background_denounced_data)
        await self.on_background_denounced_selected_callback(background_denounced_info)
        await self.page.go_async('/formulario_antecedentes_denunciado')

    async def on_row_selected_vif_indicators(self, selected_id):
        vif_denounced_data = await self.database.get_indicador_riesgo_vif_by_id(selected_id)
        vif_denounced_info = (selected_id, vif_denounced_data)
        await self.on_vif_denounced_selected_callback(vif_denounced_info)
        await self.page.go_async('/formulario_indicadores_riesgo_vif')

    async def some_confirm_action(self):
        try:
            id_denunciado = self._get_data_value(0)
            denunciado = Denunciado(
                id_causa=self._get_data_value(1),
                edad=int(self.text_fields["Edad"].value),
                sexo=self.text_fields["Sexo"].value,
                nacionalidad=self.text_fields["Nacionalidad"].value,
                nacionalidad_extranjera=self.text_fields["Nacionalidad Extranjera"].value,
                profesion_oficio=self.text_fields["Profesión/Oficio"].value,
                estudios=self.text_fields["Estudios"].value,
                caracter_lesion=self.text_fields["Presencia de Lesiones"].value,
                lesiones_descripcion=self.text_fields["Descripción de Lesiones"].value,
                estado_temperancia=self.text_fields["Estado de Temperancia"].value,
                temperancia_otro=self.text_fields["Temperancia Otro"].value,
                temperancia_descripcion=self.text_fields["Descripción de Temperancia"].value,
                otros_antecedentes=self.text_fields["Otros Antecedentes"].value,
                comuna=self.text_fields["Comuna"].value,
                estado_civil=self.text_fields["Estado Civil"].value,
                nivel_riesgo=self.text_fields["Nivel de Riesgo"].value,
                vif_numero=float(self.text_fields["Número VIF"].value)
            )
            if id_denunciado is None or id_denunciado == '':
                id_nuevo_denunciado = await self.database.add_denunciado(self.id_causa, denunciado)
                mensaje = "Nuevo denunciado agregado correctamente"
                severidad = 'exito'
                await self.mostrar_mensaje(self.page, mensaje, severidad)
                if id_nuevo_denunciado:
                    await self.agregar_antecedentes_predeterminados(id_nuevo_denunciado)
                if id_nuevo_denunciado:
                    await self.agregar_indicadores_riesgo_vif_predeterminados(id_nuevo_denunciado)
                self.page.views.pop()
                top_view = self.page.views[-1]
                await self.page.go_async(top_view.route)
            else:
                mensaje = await self.database.update_denunciado(id_denunciado, denunciado)
                mensaje = "Denunciado actualizado correctamente"
                severidad = 'exito'
                await self.mostrar_mensaje(self.page, mensaje, severidad)
            if self.update_tabla_causa_callback:
                await self.update_tabla_causa_callback()
            if self.update_card_dashboard:
                await self.update_card_dashboard()

        except ValueError as ve:
            mensaje_error = str(ve)
            if "float" in mensaje_error:
                mensaje = "Error: Se esperaba un número decimal en Número VIF."
            elif "int" in mensaje_error:
                mensaje = "Error: Se esperaba un número entero en Edad."
            severidad = 'error'
            await self.mostrar_mensaje(self.page, mensaje, severidad)
        except Exception as e:
            mensaje = f"Error inesperado: {str(e)}"
            severidad = 'error'
            await self.mostrar_mensaje(self.page, mensaje, severidad)

    async def some_delete_action(self, event=None):
        try:
            id_denunciado = self._get_data_value(0)
            await self.database.delete_denunciado(id_denunciado)

            # Mostrar mensaje de confirmación
            mensaje = "Denunciado eliminado correctamente"
            severidad = 'exito'
            await self.mostrar_mensaje(self.page, mensaje, severidad)

            # Ejecutar callbacks
            if self.update_tabla_causa_callback:
                await self.update_tabla_causa_callback()
            if self.update_card_dashboard:
                await self.update_card_dashboard()

            # Redirigir a la vista anterior
            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.go_async(top_view.route)

        except Exception as e:
            # Mostrar mensaje de error si algo sale mal
            mensaje_error = f"Error al eliminar denunciado: {str(e)}"
            await self.mostrar_mensaje(self.page, mensaje_error, 'error')

    async def agregar_antecedentes_predeterminados(self, id_denunciado):
        antecedentes_predeterminados = [
            "Aborto",
            "Abandono de niños y personas desvalidas",
            "Violación",
            "Estupro",
            "Abuso sexual",
            "Pornografía",
            "Prostitución de menores",
            "Incesto",
            "Parricidio",
            "Femicidio",
            "Homicidio",
            "Infanticidio",
            "Lesiones corporales",
            "Maltrato a menores de 18 años, adultos mayores o personas en situación de discapacidad",
            "Tráfico ilícito de migrantes",
            "Trata de personas",
            "Robo",
            "Hurto",
            "Estafa",
            "Incendio",
            "Tráfico ilícito de estupefacientes y sustancias psicotrópicas",
            "Registro especial de condenas por VIF"
        ]
        for antecedente in antecedentes_predeterminados:
            antecedente_denunciado = AntecedentesDenunciado(
                id_denunciado=id_denunciado,
                tipo_antecedente=antecedente,
                descripcion=""  # Descripción vacía por ahora
            )
            await self.database.add_antecedentes_denunciado(id_denunciado, antecedente_denunciado)

    async def agregar_indicadores_riesgo_vif_predeterminados(self, id_denunciado):
        indicadores_riesgo_vif_predeterminados = [
            "¿Tiene hijos menores de 18 años?",
            "¿El denunciado le golpeó o intentó golpear en esta oportunidad?",
            "¿Le provocó lesiones tales como, moretones, arañazos u otras?",
            "Amenazas de muerte",
            "¿Utilizó un arma contra usted? (armas de fuego, arma blanca u objeto contundente)",
            "¿le violentó o intentó violentar sexualmente?",
            "¿Tiene acceso a armas de fuego?",
            "¿Consume él/ella alcohol y/o drogas?",
            "¿Le golpea cuando consume alcohol y/o drogas?",
            "¿Se le ha diagnosticado algún trastorno psiquiátrico?",
            " ¿Él/ella le ha golpeado anteriormente?",
            "¿Ha aumentado la freuencia o gravedad de los golpes en los últimos 3 meses?",
            "¿Le ha amenzado con arma de fuego, arma blanca u otros objetos con anterioridad?",
            "¿Con anterioridad a esta denuncia, él/ella le ha amenazado de muerte?",
            "¿Ha golpeado a menores de edad de la familia, otros familiares o conocidos recientemente?",
            "¿Esta persona presenta celos violentos?",
            "¿Está separada(o)/divorciada(o) de esta persona, o esta en proceso de separación/divorcio?",
            "La persona denunciada ¿Se niega a aceptar esta separación/divorcio?",
            "¿Tiene alguna discapacidad que le dificulte protegerse?",
            "¿Está embarazada?",
            "¿Vive con el denunciado(a)?",
            "¿Depende económicamente del denunciado(a)?",
            "Usted: ¿Depende económicamente del denunciado(a)?",
            "Respecto a lo contado: ¿Cree que el denunciado(a) le agredirá si sabe de la denuncia?",
            "¿Cree que pueda matarle a usted o a alguien de su familia?",
            "¿Tiene el imputado(a) otras denuncias por VIF?",
            "¿Tiene el imputado(a) condenas por VIF?",
            "¿Registra el imputado(a) denuncias o condenas por desacato en VIF?",
            "¿Tiene el imputado(a) condenas o procesos pendientes por a) Crimen o simple delito contra las personas?",
            "¿Tiene el imputado(a) condenas o procesos pendientes por b) Violación, estupro, u otros delitos sexuales de los párrafos 5 y 6 del título VII, libro II CP?",
            "¿Tiene el imputado(a) condenas o procesos pendientes por: c) Infracciones de la ley 17.798 sobre control de armas?",
            "¿Tiene el imputado(a) condenas o procesos pendientes por d) Amenazas?",
            "¿Tiene el imputado(a) condenas o procesos pendientes por: e) Robo con violencia?",
            "¿Tiene el imputado(a) condenas o procesos pendientes por: f) Aborto con violencia?"]
        for indicador in indicadores_riesgo_vif_predeterminados:
            indicador_riesgo_vif = DenunciadoIndicadoresRiesgoVIF(
                id_denunciado=id_denunciado,
                descripcion_indicador=indicador,
                respuesta=""
            )
            await self.database.add_indicador_riesgo_vif(id_denunciado, indicador_riesgo_vif)


    async def obtener_y_mapear_indicadores(self, denunciado_id):
        mapeo_indicadores = {
            "¿tiene hijos menores de 18 anio?": "vif_hijos_menores",
            "¿el denunciado le golpeo o intento golpear en esta oportunidad?": "vif_hecho_golpes",
            "¿le provoco lesiones tales como, moretones, aranazos u otras?": "vif_hecho_lesiones",
            "amenazas de muerte": "vif_hecho_amenaza_muerte",
            "¿utilizo un arma contra usted? (armas de fuego, arma blanca u objeto contundente)": "vif_hecho_uso_arma",
            "¿le violento o intento violentar sexualmente?": "vif_hecho_violencia_sexual",
            "¿tiene acceso a armas de fuego?": "vif_denunciado_acceso_armas",
            "¿consume el/ella alcohol y/o drogas?": "vif_denunciado_consumo_sustancias",
            "¿le golpea cuando consume alcohol y/o drogas?": "vif_denunciado_violencia_consumo",
            "¿se le ha diagnosticado algun trastorno psiquiatrico?": "vif_denunciado_trastorno_psiquiatrico",
            "¿el/ella le ha golpeado anteriormente?": "vif_historia_golpes_previos",
            "¿ha aumentado la frecuencia o gravedad de los golpes en los ultimos 3 meses?": "vif_historia_aumento_golpes",
            "¿le ha amenazado con arma de fuego, arma blanca u otros objetos con anterioridad?": "vif_historia_amenaza_arma",
            "¿con anterioridad a esta denuncia, el/ella le ha amenazado de muerte?": "vif_historia_amenaza_muerte_previa",
            "¿ha golpeado a menores de edad de la familia, otros familiares o conocidos recientemente?": "vif_historia_violencia_menores",
            "¿esta persona presenta celos violentos?": "vif_historia_celos_violentos",
            "¿esta separada(o)/divorciada(o) de esta persona, o esta en proceso de separacion/divorcio?": "vif_historia_separacion",
            "la persona denunciada ¿se niega a aceptar esta separacion/divorcio?": "vif_historia_rechazo_separacion",
            "¿tiene alguna discapacidad que le dificulte protegerse?": "vif_usted_discapacidad",
            "¿está embarazada?": "vif_usted_embarazo",
            "¿vive con el denunciado(a)?": "vif_usted_convivencia_denunciado",
            "¿depende economicamente del denunciado(a)?": "vif_usted_dependencia_economica",
            "respecto a lo contado: ¿cree que el denunciado(a) le agredira si sabe de la denuncia?": "vif_reaccion_denuncia_agresion",
            "¿cree que pueda matarle a usted o a alguien de su familia?": "vif_reaccion_denuncia_riesgo_fatal",
            "¿tiene el imputado(a) otras denuncias por VIF?": "vif_imputado_denuncias_vif",
            "¿tiene el imputado(a) condenas por VIF?": "vif_imputado_condenas_vif",
            "¿registra el imputado(a) denuncias o condenas por desacato en VIF?": "vif_imputado_desacato_vif"
        }

        condenas_o_procesos = [
            "¿tiene el imputado(a) condenas o procesos pendientes por a) crimen o simple delito contra las personas?",
            "¿tiene el imputado(a) condenas o procesos pendientes por b) violación, estupro, u otros delitos sexuales de los párrafos 5 y 6 del título VII, libro II CP?",
            "¿tiene el imputado(a) condenas o procesos pendientes por: c) infracciones de la ley 17.798 sobre control de armas?",
            "¿tiene el imputado(a) condenas o procesos pendientes por d) amenazas?",
            "¿tiene el imputado(a) condenas o procesos pendientes por: e) robo con violencia?",
            "¿tiene el imputado(a) condenas o procesos pendientes por: f) aborto con violencia?"
        ]

        # Obtener los datos de la base de datos
        composicion_columns = ["descripcion_indicador", "respuesta"]
        result = await self.database.get_indicadores_riesgo_vif_by_denunciado_id(composicion_columns, denunciado_id)
        columnas_df = list(mapeo_indicadores.values()) + ['vif_imputado_delitos_pendientes']
        df = pd.DataFrame(columns=columnas_df)
        df.loc[0] = [0] * len(columnas_df)  # Añadir una fila con valores predeterminados a 0

        for indicador, respuesta in result:
            nombre_columna = mapeo_indicadores.get(indicador)
            if nombre_columna in df.columns:
                respuesta_minuscula = respuesta.lower()  # Convertir la respuesta a minúscula
                if respuesta_minuscula == 'si' or respuesta_minuscula == 'sí':
                    df.loc[0, nombre_columna] = 1
                elif respuesta_minuscula == 'no aplica' or respuesta_minuscula == 'sin información':
                    df.loc[0, nombre_columna] = 0
                else:
                    df.loc[0, nombre_columna] = 0
            elif indicador in condenas_o_procesos and respuesta.lower() == 'si':
                df.loc[0, 'vif_imputado_delitos_pendientes'] = 1

            
        prediccion = self.modelo.predict(df)

        # Mapeo de índices a nombres de clases según el orden en 'y'
        clases = ['nivel_bajo', 'nivel_medio', 'nivel_alto']

        # Obtener el índice de la clase con la mayor probabilidad
        indice_clase_predicha = np.argmax(prediccion, axis=1)

        # Obtener el nombre de la clase predicha
        nombre_clase_predicha = clases[indice_clase_predicha[0]]
         
        return nombre_clase_predicha

