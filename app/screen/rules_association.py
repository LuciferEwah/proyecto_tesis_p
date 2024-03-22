import flet as ft
import pandas as pd
from widgets.rules import ReglasAsociacion
import asyncio

class RulesAssociantionScreen(ft.UserControl):
    def __init__(self, db, page, route_change_handler, nav_rail_class):
        super().__init__()
        self.db = db
        self.page = page
        self.route_change_handler = route_change_handler
        self.nav_rail_class = nav_rail_class
        self

    def build(self):


        self.regla_asociacion = ReglasAsociacion(self.page)

        self.regla_asociacion_container = ft.Container(content=self.regla_asociacion, visible=True)



        scrollable_content = ft.Column(
            [self.regla_asociacion_container ],  
            alignment=ft.MainAxisAlignment.START,
            expand=True
        )
        asyncio.create_task(self.load_and_display_data())

        return ft.Row(
            [
                self.nav_rail_class.create_rail(),
                ft.VerticalDivider(width=3),
                scrollable_content
            ],
            vertical_alignment=ft.CrossAxisAlignment.START
        )



    async def load_and_display_data(self):
        
        df_victimas_combinado, _ = await self.combinado_victimas()
        df_victimas_combinado = df_victimas_combinado.add_prefix("vic_")
        df_victimas_combinado.rename(columns={'vic_id_causa': 'id_causa'}, inplace=True)
        df_victimas_combinado = df_victimas_combinado.groupby('id_causa').first().reset_index()
        df_para_combinar = await self.get_combined_dataframe()
        df_final = pd.merge(df_victimas_combinado, df_para_combinar, on='id_causa', how='outer')
        # Eliminar la columna 'id_causa' (ya que ya se utilizó para la fusión)
        df_final.drop('id_causa', axis=1, inplace=True)
        df_final['delito_fecha_delito'] = df_final['delito_fecha_delito'].astype(str)


        await self.regla_asociacion.load_data(df_final)
        self.regla_asociacion_container.visible = True
        await self.regla_asociacion_container.update_async()
        


   
    async def combinado_victimas(self):
        # Obtener datos y columnas de víctimas y denunciantes
        victimas_data, columnas_victimas = await self.db.get_all_victimas()
        denunciantes_data, columnas_denunciantes = await self.db.get_all_denunciantes()
        df_victimas = pd.DataFrame(victimas_data, columns=columnas_victimas)
        df_denunciantes = pd.DataFrame(denunciantes_data, columns=columnas_denunciantes)
    

        # Asegurar que df_denunciantes tenga las mismas columnas que df_victimas
        columnas_comunes = set(columnas_victimas).intersection(columnas_denunciantes)
        df_tabla_denunciante_es_victima = df_denunciantes[df_denunciantes['es_denunciante_victima'] == 'si']
        df_tabla_denunciante_es_victima = df_tabla_denunciante_es_victima[list(columnas_comunes)]

        # Concatenar DataFrames asegurando que tienen las mismas columnas
        df_combinado = pd.concat([df_victimas[list(columnas_comunes)], df_tabla_denunciante_es_victima], ignore_index=True)
        

        return df_combinado, columnas_comunes


    async def get_denunciados(self):
        mapeo_antecedentes_inverso = {
        "aborto": "antecedente_aborto",
        "abandono de niños y personas desvalidas": "antecedente_abandono",
        "violación": "antecedente_violacion",
        "estupro": "antecedente_estupro",
        "abuso sexual": "antecedente_abuso_sexual",
        "pornografia": "antecedente_pornografia",
        "prostitución de menores": "antecedente_prostitucion_menores",
        "incesto": "antecedente_incesto",
        "parricidio": "antecedente_parricidio",
        "femicidio": "antecedente_femicidio",
        "homicidio": "antecedente_homicidio",
        "infanticidio": "antecedente_infanticidio",
        "lesiones corporales": "antecedente_lesiones_corporales",
        "maltrato a menores de 18 años, adultos mayores o personas en situación de discapacidad": "antecedente_maltrato",
        "tráfico ilícito de migrantes": "antecedente_trafico_migrantes",
        "trata de personas": "antecedente_trata_personas",
        "robo": "antecedente_robo",
        "hurto": "antecedente_hurto",
        "estafa": "antecedente_estafa",
        "incendio": "antecedente_incendio",
        "trafico ilícito de estupefacientes y sustancias psicotrópicas": "antecedente_trafico_estupefacientes",
        "registro especial de condenas por vif": "antecedente_registro_vif"
        }
        mapeo_respuestas_vif_inverso = {
            "¿cual es su parentesco con el denunciado?": "vif_parentesco_denunciado",
            "¿cual es su parentesco con el denunciado - otro?": "vif_parentesco_denunciado_otro",
            "¿tiene hijos menores de 18 anos?": "vif_hijos_menores",
            "¿la persona que usted denuncio le golpeo o intento golpear en esta oportunidad?": "vif_hecho_golpes",
            "¿le provoco lesiones tales como, moretones, aranazos u otras?": "vif_hecho_lesiones",
            "hecho denunciado: ¿le amenazo de muerte?": "vif_hecho_amenaza_muerte",
            "hecho denunciado: ¿utilizo un arma contra usted? (armas de fuego, arma blanca u objeto contundente)": "vif_hecho_uso_arma",
            "hecho denunciado: ¿le violento o intento violentar sexualmente?": "vif_hecho_violencia_sexual",
            "persona denunciada: ¿tiene acceso a armas de fuego?": "vif_denunciado_acceso_armas",
            "persona denunciada: ¿consume el/ella alcohol y/o drogas?": "vif_denunciado_consumo_sustancias",
            "¿le golpea cuando consume alcohol y/o drogas?": "vif_denunciado_violencia_consumo",
            "persona denunciada: ¿se le ha diagnosticado algun trastorno psiquiatrico?": "vif_denunciado_trastorno_psiquiatrico",
            "¿el/ella le ha golpeado anteriormente?": "vif_historia_golpes_previos",
            "¿ha aumentado la frecuencia o gravedad de los golpes en los ultimos 3 meses?": "vif_historia_aumento_golpes",
            "¿le ha amenzado con arma de fuego, arma blanca(ej. cortaplumas, cuchillos), u otros objetos con anterioridad?": "vif_historia_amenaza_arma",
            "historia: ¿con anterioridad a esta denuncia, el/ella le ha amenazado de muerte?": "vif_historia_amenaza_muerte_previa",
            "¿ha golpeado a menores de edad de la familia, otros familiares o conocidos recientemente?": "vif_historia_violencia_menores",
            "¿esta persona presenta celos violentos?": "vif_historia_celos_violentos",
            "¿esta separada(o)/divorciada(o) de esta persona, o esta en proceso de separacion/divorcio?": "vif_historia_separacion",
            "historia: la persona denunciada ¿se niega a aceptar esta separacion/divorcio?": "vif_historia_rechazo_separacion",
            "respecto a usted: ¿tiene alguna discapacidad que le dificulte protegerse?": "vif_usted_discapacidad",
            "respecto a usted: ¿esta embarazada? (si es mujer a quien se entrevista y no es adulta mayor)": "vif_usted_embarazo",
            "respecto a usted: ¿vive con el denunciado(a)?": "vif_usted_convivencia_denunciado",
            "respecto a usted: ¿depende economicamente del denunciado(a)?": "vif_usted_dependencia_economica",
            "respecto a lo contado: ¿cree que el denunciado(a) le agredira si sabe de la denuncia?": "vif_reaccion_denuncia_agresion",
            "respecto de lo contado: ¿cree que pueda matarle a usted o a alguien de su familia?": "vif_reaccion_denuncia_riesgo_fatal",
            "¿tiene el imputado(a) otras denuncias por vif?": "vif_imputado_denuncias_vif",
            "¿tiene el imputado(a) condenas por vif?": "vif_imputado_condenas_vif",
            "¿registra el imputado(a) denuncias o condenas por desacato en vif?": "vif_imputado_desacato_vif",
            "¿tiene el imputado(a) condenas o procesos pendientes por: a) crimen o simple delito contra las personas; b) violacion, estupro, otros delitos sexuales de los parrafos 5 y 6 del titulo vii, libro ii cp; c) infracciones ley 17.798 sobre control de armas; d) amenazas; e) robo con violencia; f) aborto con violencia?": "vif_imputado_delitos_pendientes"
        }


        # Obtener datos de la base de datos
        denunciados_data, denunciados_columns = await self.db.get_all_denunciados()
        antecedentes_data, antecedentes_columns = await self.db.get_all_denunciado_antecedentes()
        riesgo_vif_data, riesgo_vif_columns = await self.db.get_all_denunciado_riesgo_vif()

        # Crear DataFrames con los datos y columnas correspondientes
        df_denunciados = pd.DataFrame(denunciados_data, columns=denunciados_columns)
        df_antecedentes = pd.DataFrame(antecedentes_data, columns=antecedentes_columns)
        df_riesgo_vif = pd.DataFrame(riesgo_vif_data, columns=riesgo_vif_columns)
   
        df_denunciados = df_denunciados.add_prefix('den_')

        # Cambia el nombre de la columna 'id_causa' a 'id_causa' sin el prefijo
        df_denunciados = df_denunciados.rename(columns={'den_id_causa': 'id_causa'})


        # Transformar los DataFrames
        df_antecedentes_transformado = await self.transformar_dataframe_completo(df_antecedentes, mapeo_antecedentes_inverso)
        df_vif_transformado = await self.transformar_dataframe_completo(df_riesgo_vif, mapeo_respuestas_vif_inverso)

        # Realizar la fusión de los DataFrames en base a la columna 'id_causa'    
        df_merged_1 = pd.merge(df_denunciados, df_antecedentes_transformado, on='id_causa', how='outer')
        df_final = pd.merge(df_merged_1, df_vif_transformado, on='id_causa', how='outer')
        df_final = df_final.drop_duplicates(subset='id_causa', keep='first')
        df_final = df_final.fillna('no aplica')

        return df_final
    
    async def get_medidas_preparatoria(self):
        mapeo_medidas_policiales_preguntas_inverso = {
        "rondas periódicas al domicilio de la víctima": "med_poli_rondas_domicilio",
        "acceso a teléfono prioritario del cuadrante": "med_poli_telefono_cuadrante",
        "prohibición de acercarse a la víctima": "med_poli_prohibicion_acercamiento",
        "prohibir o restringir la presencia del ofensor en el hogar común y domicilio": "med_poli_restriccion_presencia_ofensor",
        "asegurar la entrega material de los efectos personales de la víctima": "med_poli_entrega_efectos_personales",
        "fijar alimentos provisionales": "med_poli_fijacion_alimentos",
        "medidas cautelares: determinar un régimen provisorio de cuidado personal de nna": "med_poli_regimen_cuidado_nna",
        "medidas cautelares: decretar la prohibición de celebrar actos o contratos": "med_poli_prohibicion_actos_contratos",
        "medidas cautelares: prohibir el porte y tenencia de cualquier arma de fuego": "med_poli_prohibicion_armas",
        "decretar la reserva de la identidad del denunciante": "med_poli_reserva_identidad_denunciante",
        "establecer medidas de protección para adultos mayores o personas afectadas por alguna incapacidad": "med_poli_proteccion_adultos_mayores_discapacidad",
        "asistencia obligatoria a programas terapéuticos o de orientación familiar": "med_poli_asistencia_terapeutica",
        "obligación de presentarse regularmente a la unidad policial que determine el juez": "med_poli_presentacion_unidad_policial",
        "otra medida cautelar": "med_poli_otra_cautelar",
        }
        mapeo_medidas_preparatorias_preguntas_inverso = {
        "rondas periódicas al domicilio de la víctima": "med_pre_rondas_domicilio",
        "acceso a teléfono prioritario del cuadrante": "med_pre_telefono_cuadrante",
        "prohibición de acercarse a la víctima": "med_pre_prohibicion_acercamiento",
        "prohibir o restringir la presencia del ofensor en el hogar común y domicilio": "med_pre_restriccion_presencia_ofensor",
        "asegurar la entrega material de los efectos personales de la víctima": "med_pre_entrega_efectos_personales",
        "fijar alimentos provisionales": "med_pre_fijacion_alimentos",
        "medidas cautelares: determinar un régimen provisorio de cuidado personal de nna": "med_pre_regimen_cuidado_nna",
        "medidas cautelares: decretar la prohibición de celebrar actos o contratos": "med_pre_prohibicion_actos_contratos",
        "medidas cautelares: prohibir el porte y tenencia de cualquier arma de fuego": "med_pre_prohibicion_armas",
        "decretar la reserva de la identidad del denunciante": "med_pre_reserva_identidad_denunciante",
        "establecer medidas de protección para adultos mayores o personas afectadas por alguna incapacidad": "med_pre_proteccion_adultos_mayores_discapacidad",
        "asistencia obligatoria a programas terapéuticos o de orientación familiar": "med_pre_asistencia_terapeutica",
        "obligación de presentarse regularmente a la unidad policial que determine el juez": "med_pre_presentacion_unidad_policial",
        "otra medida cautelar": "med_pre_otra_cautelar",
        }
        mapeo_medidas_jucio_preguntas_inverso = {
            "rondas periódicas al domicilio de la víctima": "med_jui_rondas_domicilio",
            "acceso a teléfono prioritario del cuadrante": "med_jui_telefono_cuadrante",
            "prohibición de acercarse a la víctima": "med_jui_prohibicion_acercamiento",
            "prohibir o restringir la presencia del ofensor en el hogar común y domicilio": "med_jui_restriccion_presencia_ofensor",
            "asegurar la entrega material de los efectos personales de la víctima": "med_jui_entrega_efectos_personales",
            "fijar alimentos provisionales": "med_jui_fijacion_alimentos",
            "medidas cautelares: determinar un régimen provisorio de cuidado personal de nna": "med_jui_regimen_cuidado_nna",
            "medidas cautelares: decretar la prohibición de celebrar actos o contratos": "med_jui_prohibicion_actos_contratos",
            "medidas cautelares: prohibir el porte y tenencia de cualquier arma de fuego": "med_jui_prohibicion_armas",
            "decretar la reserva de la identidad del denunciante": "med_jui_reserva_identidad_denunciante",
            "establecer medidas de protección para adultos mayores o personas afectadas por alguna incapacidad": "med_jui_proteccion_adultos_mayores_discapacidad",
            "asistencia obligatoria a programas terapéuticos o de orientación familiar": "med_jui_asistencia_terapeutica",
            "obligación de presentarse regularmente a la unidad policial que determine el juez": "med_jui_presentacion_unidad_policial",
            "otra medida cautelar": "med_jui_otra_cautelar",
        }
 
        data_antecedente_delito, columnas_antecedentes_delito = await self.db.get_all_antecedentes_delito()
        medidas_policiales_data, medidas_policiales_columns = await self.db.get_all_medidas_policiales()
        medidas_cautelares_data, medidas_cautelares_columns = await self.db.get_all_medidas_cautelares_preparatorias()
        medidas_sentencia_data, medidas_sentencia_columns = await self.db.get_all_medidas_provisorias_juicio()
        
        antecedentes_delito = pd.DataFrame(data_antecedente_delito, columns=columnas_antecedentes_delito)
        antecedentes_delito.drop('id_antecedentes_delito', axis=1, inplace=True)
        antecedentes_delito.drop('hora_delito', axis=1, inplace=True)
        antecedentes_delito = antecedentes_delito.add_prefix('delito_')
        antecedentes_delito = antecedentes_delito.rename(columns={'delito_id_causa': 'id_causa'})

        medidas_policiales_preparatorias = pd.DataFrame(medidas_policiales_data, columns=medidas_policiales_columns)
        medidas_cautelares_preparatorias = pd.DataFrame(medidas_cautelares_data, columns=medidas_cautelares_columns)
        medidas_sentenciales_preparatorias = pd.DataFrame(medidas_sentencia_data, columns=medidas_sentencia_columns)
       
        df = await self.transformar_dataframe_completo(medidas_policiales_preparatorias, mapeo_medidas_policiales_preguntas_inverso)
        df_1 = await self.transformar_dataframe_completo(medidas_cautelares_preparatorias, mapeo_medidas_preparatorias_preguntas_inverso)
        df_2 = await self.transformar_dataframe_completo(medidas_sentenciales_preparatorias, mapeo_medidas_jucio_preguntas_inverso)

            
        df_merged_1 = pd.merge(antecedentes_delito, df, on='id_causa', how='outer')
        df_merged_2 = pd.merge(df_merged_1, df_1, on='id_causa', how='outer')
        df_final = pd.merge(df_merged_2, df_2, on='id_causa', how='outer')
        df_final = df_final.drop_duplicates(subset='id_causa', keep='first')
        df_final = df_final.fillna('no aplica')


        return df_final
        
    async def get_combined_dataframe(self):
        # Obtener los DataFrames individuales
        df_denunciados = await self.get_denunciados()
        df_medidas_preparatoria = await self.get_medidas_preparatoria()
      
        # Realizar la fusión de los DataFrames en base a la columna 'id_causa'
        df_combined = pd.merge(df_denunciados, df_medidas_preparatoria, on='id_causa', how='outer')
  
        df_combined = df_combined.fillna('no aplica')
        return df_combined


    async def transformar_dataframe_completo(self, df, mapeo_preguntas, id_column_name=None):
        # Crear listas para almacenar los datos transformados
        case_ids = []
        ids = [] if id_column_name else None
        tipos_medida = []
        respuestas = []

        # Rellenar las listas con los datos normalizados
        for index, row in df.iterrows():
            case_ids.append(row['id_causa'])
            if id_column_name:
                ids.append(row[id_column_name])

            for medida, pregunta in mapeo_preguntas.items():
                tipos_medida.append(pregunta)
                # Obtener la respuesta, dando prioridad a 'descripcion' y usando 'respuesta' en caso contrario
                respuesta = row.get('descripcion', row.get('respuesta', 'no aplica'))
                # Reemplazar NaN con 'no aplica'
                respuesta = 'no aplica' if pd.isna(respuesta) else respuesta
                respuestas.append(respuesta)

        # Asegurarse de que todas las listas tengan la misma longitud
        max_length = max(len(case_ids), len(tipos_medida), len(respuestas))
        case_ids += [None] * (max_length - len(case_ids))
        tipos_medida += [None] * (max_length - len(tipos_medida))
        respuestas += ['no aplica'] * (max_length - len(respuestas))

        # Crear un nuevo DataFrame con las listas
        df_mapeado = pd.DataFrame({
            'id_causa': case_ids,
            'Tipo': tipos_medida,
            'Respuesta': respuestas
        })
        
        if id_column_name:
            df_mapeado[id_column_name] = ids

        df_ancho = df_mapeado.pivot_table(index=['id_causa'], columns=['Tipo'], values='Respuesta', aggfunc='first').reset_index()
        df_ancho['id_causa'] = df_ancho['id_causa'].astype(int)
        return df_ancho