import flet as ft
import pandas as pd
import unicodedata
import re
import numpy as np
import os
from models.causa import Causa
import asyncio
from widgets.dialog import ConfirmationDialog
from models.victima import Victima
from models.composicion_hogar import ComposicionHogar, ComposicionHogarEnJuicio
from models.denunciado import Denunciado
from models.antecedentes_denunciado import AntecedentesDenunciado
from models.denunciado_vif import DenunciadoIndicadoresRiesgoVIF
from models.denunciantes import Denunciante
from models.audencia_preparatoria import AudienciaPreparatoria
from models.audencia_relaciones import AudienciaRelaciones
from models.medida_cautelar import MedidaCautelar, MedidaCautelarEspecial
from models.audencia_juicio_antecedentes import AudienciaJuicioAntecedentes
from models.antecedente_policial import AntecedentePolicial


class ConfigurationScreen(ft.UserControl):
    def __init__(self, db, page, route_change_handler, nav_rail_class, mostrar_mensaje_func=None):
        super().__init__()
        self.db = db
        self.page = page
        self.route_change_handler = route_change_handler
        self.nav_rail_class = nav_rail_class
        self.mostrar_mensaje = mostrar_mensaje_func
        self.file_picker = ft.FilePicker(on_result=self.pick_files_result)
        self.file_path = None
        self.file_picker_save = ft.FilePicker(on_result=self.pick_files_save_result)
        self.file_path_save = None
        self.directory_selected_event = asyncio.Event()
        self.df_tabla_causa = None
        self.df_tabla_victima = None
        self.df_tabla_composicion_hogar = None
        self.df_tabla_denunciado = None
        self.df_tabla_denunciado_vif = None
        self.df_tabla_denunciado_antecedentes = None
        self.df_tabla_antecetendes_delito = None
        self.df_tabla_medida_policial = None
        self.df_tabla_audiencia_preparatoria = None
        self.df_tabla_medida_preparatoria = None
        self.df_tabla_audencia_jucio = None
        self.df_tabla_medida_juicio = None
        self.df_tabla_composicion_hogar_cambio = None
        self.df_tabla_denunciantes = None

        self.mapeo_preguntas_medidas = {
            "rondas_domicilio": "rondas periódicas al domicilio de la víctima",
            "telefono_cuadrante": "acceso a teléfono prioritario del cuadrante",
            "prohibicion_acercamiento": "prohibición de acercarse a la víctima",
            "restriccion_presencia_ofensor": "prohibir o restringir la presencia del ofensor en el hogar común y domicilio",
            "entrega_efectos_personales": "asegurar la entrega material de los efectos personales de la víctima",
            "fijacion_alimentos": "fijar alimentos provisionales",
            "regimen_cuidado_nna": "medidas cautelares: determinar un régimen provisorio de cuidado personal de nna",
            "prohibicion_actos_contratos": "medidas cautelares: decretar la prohibición de celebrar actos o contratos",
            "prohibicion_armas": "medidas cautelares: prohibir el porte y tenencia de cualquier arma de fuego",
            "reserva_identidad_denunciante": "decretar la reserva de la identidad del denunciante",
            "proteccion_adultos_mayores_discapacidad": "establecer medidas de protección para adultos mayores o personas afectadas por alguna incapacidad",
            "asistencia_terapeutica": "asistencia obligatoria a programas terapéuticos o de orientación familiar",
            "presentacion_unidad_policial": "obligación de presentarse regularmente a la unidad policial que determine el juez",
            "otra_cautelar": "otra medida cautelar",
        }
        self.mapeo_preguntas_vif = {
            "vif_parentesco_denunciado": "¿Cuál es su parentesco con el Denunciado?",
            "vif_parentesco_denunciado_otro": "¿Cuál es su parentesco con el Denunciado - Otro?",
            "vif_hijos_menores": "¿Tiene hijos menores de 18 años?",
            "vif_hecho_golpes": "¿La persona que usted denunció le golpeó o intentó golpear en esta oportunidad?",
            "vif_hecho_lesiones": "¿Le provocó lesiones tales como, moretones, arañazos u otras?",
            "vif_hecho_amenaza_muerte": "Hecho Denunciado: ¿Le amenazó de muerte?",
            "vif_hecho_uso_arma": "Hecho Denunciado: ¿Utilizó un arma contra usted? (armas de fuego, arma blanca u objeto contundente)",
            "vif_hecho_violencia_sexual": "Hecho Denunciado: ¿le violentó o intentó violentar sexualmente?",
            "vif_denunciado_acceso_armas": "Persona Denunciada: ¿Tiene acceso a armas de fuego?",
            "vif_denunciado_consumo_sustancias": "Persona Denunciada: ¿Consume él/ella alcohol y/o drogas?",
            "vif_denunciado_violencia_consumo": "¿Le golpea cuando consume alcohol y/o drogas?",
            "vif_denunciado_trastorno_psiquiatrico": "Persona Denunciada: ¿Se le ha diagnosticado algún trastorno psiquiátrico?",
            "vif_historia_golpes_previos": "¿Él/ella le ha golpeado anteriormente?",
            "vif_historia_aumento_golpes": "¿Ha aumentado la frecuencia o gravedad de los golpes en los últimos 3 meses?",
            "vif_historia_amenaza_arma": "¿Le ha amenzado con arma de fuego, arma blanca(ej. Cortaplumas, cuchillos), u otros objetos con anterioridad?",
            "vif_historia_amenaza_muerte_previa": "Historia: ¿Con anterioridad a esta denuncia, él/ella le ha amenazado de muerte?",
            "vif_historia_violencia_menores": "¿Ha golpeado a menores de edad de la familia, otros familiares o conocidos recientemente?",
            "vif_historia_celos_violentos": "¿Esta persona presenta celos violentos?",
            "vif_historia_separacion": "¿Está separada(o)/divorciada(o) de esta persona, o esta en proceso de separación/divorcio?",
            "vif_historia_rechazo_separacion": "Historia: La persona denunciada ¿Se niega a aceptar esta separación/divorcio?",
            "vif_usted_discapacidad": "Respecto a usted: ¿Tiene alguna discapacidad que le dificulte protegerse?",
            "vif_usted_embarazo": "Respecto a usted: ¿Está embarazada? (Si es mujer a quien se entrevista y no es adulta mayor)",
            "vif_usted_convivencia_denunciado": "Respecto a usted: ¿Vive con el denunciado(a)?",
            "vif_usted_dependencia_economica": "Respecto a usted: ¿Depende económicamente del denunciado(a)?",
            "vif_reaccion_denuncia_agresion": "Respecto a lo contado: ¿Cree que el denunciado(a) le agredirá si sabe de la denuncia?",
            "vif_reaccion_denuncia_riesgo_fatal": "Respecto de lo contado: ¿Cree que pueda matarle a usted o a alguien de su familia?",
            "vif_imputado_denuncias_vif": "¿Tiene el imputado(a) otras denuncias por VIF?",
            "vif_imputado_condenas_vif": "¿Tiene el imputado(a) condenas por VIF?",
            "vif_imputado_desacato_vif": "¿Registra el imputado(a) denuncias o condenas por desacato en VIF?",
            "vif_imputado_delitos_pendientes": "¿Tiene el imputado(a) condenas o procesos pendientes por: a) crimen o simple delito contra las personas; b) violación, estupro, otros delitos sexuales de los párrafos 5 y 6 del título VII, libro II CP; c) infracciones ley 17.798 sobre control de armas; d) amenazas; e) robo con violencia; f) aborto con violencia?"
        }
        self.mapeo_antecedentes = {
            "antecedente_aborto": "Aborto",
            "antecedente_abandono": "Abandono de niños y personas desvalidas",
            "antecedente_violacion": "Violación",
            "antecedente_estupro": "Estupro",
            "antecedente_abuso_sexual": "Abuso sexual",
            "antecedente_pornografia": "Pornografía",
            "antecedente_prostitucion_menores": "Prostitución de menores",
            "antecedente_incesto": "Incesto",
            "antecedente_parricidio": "Parricidio",
            "antecedente_femicidio": "Femicidio",
            "antecedente_homicidio": "Homicidio",
            "antecedente_infanticidio": "Infanticidio",
            "antecedente_lesiones_corporales": "Lesiones corporales",
            "antecedente_maltrato": "Maltrato a menores de 18 años, adultos mayores o personas en situación de discapacidad",
            "antecedente_trafico_migrantes": "Tráfico ilícito de migrantes",
            "antecedente_trata_personas": "Trata de personas",
            "antecedente_robo": "Robo",
            "antecedente_hurto": "Hurto",
            "antecedente_estafa": "Estafa",
            "antecedente_incendio": "Incendio",
            "antecedente_trafico_estupefacientes": "Tráfico ilícito de estupefacientes y sustancias psicotrópicas",
            "antecedente_registro_vif": "Registro especial de condenas por VIF"
        }
        self.mapeo_composicion_hogar = {
            'vic_vive_con_conyuge': "La víctima vive con Cónyuge",
            'vic_vive_con_exconyuge': "La víctima vive con Ex-Cónyuge",
            'vic_vive_con_pareja': "La víctima vive con Pareja",
            'vic_vive_con_expareja': "La víctima vive con Ex-Pareja",
            'vic_vive_con_conviviente_auc': "La víctima vive con Conviviente (con AUC)",
            'vic_vive_con_exconviviente_auc': "La víctima vive con Ex-Conviviente (con AUC)",
            'vic_vive_con_conviviente_hecho': "La víctima vive con Conviviente de hecho",
            'vic_vive_con_exconviviente_hecho': "La víctima vive con Ex-Conviviente de hecho",
            'vic_vive_con_papa': "La víctima vive con Papá",
            'vic_vive_con_mama': "La víctima vive con Mamá",
            'vic_vive_con_padrastro': "La víctima vive con Padrastro",
            'vic_vive_con_madrastra': "La víctima vive con Madrastra",
            'vic_vive_con_1_hijo': "La víctima vive con 1 Hijo",
            'vic_vive_con_hijos': "La víctima vive con Hijo(s)",
            'vic_vive_con_1_hija': "La víctima vive con 1 Hija",
            'vic_vive_con_hijas': "La víctima vive con Hija(s)",
            'vic_vive_con_hijastro': "La víctima vive con Hijastro(s)",
            'vic_vive_con_hijastra': "La víctima vive con Hijastra(s)",
            'vic_vive_con_1_hermano': "La víctima vive con 1 Hermano",
            'vic_vive_con_hermanos': "La víctima vive con Hermano(s)",
            'vic_vive_con_1_hermana': "La víctima vive con 1 Hermana",
            'vic_vive_con_hermanas': "La víctima vive con Hermana(s)",
            'vic_vive_con_hermanastro': "La víctima vive con Hermanastro(s)",
            'vic_vive_con_hermanastra': "La víctima vive con Hermanastra(s)",
            'vic_vive_con_tio': "La víctima vive con Tío(s)",
            'vic_vive_con_tia': "La víctima vive con Tía(s)",
            'vic_vive_con_suegro': "La víctima vive con Suegro",
            'vic_vive_con_suegra': "La víctima vive con Suegra",
            'vic_vive_con_abuelo': "La víctima vive con Abuelo",
            'vic_vive_con_abuela': "La víctima vive con Abuela",
            'vic_vive_con_nieto': "La víctima vive con Nieto(s)",
            'vic_vive_con_nieta': "La víctima vive con Nieta(s)",
            'vic_vive_con_otro': "La víctima vive con Otro(a)",
        }
        # Mapeo de campos de cambio en la composición del hogar de la víctima
        self.mapeo_cambio_composicion_hogar = {
            'cambio_vic_vive_con_conyuge': "La víctima vive con Cónyuge",
            'cambio_vic_vive_con_exconyuge': "La víctima vive con Ex-Cónyuge",
            'cambio_vic_vive_con_pareja': "La víctima vive con Pareja",
            'cambio_vic_vive_con_expareja': "La víctima vive con Ex-Pareja",
            'cambio_vic_vive_con_conviviente_auc': "La víctima vive con Conviviente AUC",
            'cambio_vic_vive_con_exconviviente_auc': "La víctima vive con Ex-Conviviente AUC",
            'cambio_vic_vive_con_conviviente_hecho': "La víctima vive con Conviviente Hecho",
            'cambio_vic_vive_con_exconviviente_hecho': "La víctima vive con Ex-Conviviente Hecho",
            'cambio_vic_vive_con_papa': "La víctima vive con Papá",
            'cambio_vic_vive_con_mama': "La víctima vive con Mamá",
            'cambio_vic_vive_con_padrastro': "La víctima vive con Padrastro",
            'cambio_vic_vive_con_madrastra': "La víctima vive con Madrastra",
            'cambio_vic_vive_con_1_hijo': "La víctima vive con 1 Hijo",
            'cambio_vic_vive_con_hijos': "La víctima vive con Hijos",
            'cambio_vic_vive_con_1_hija': "La víctima vive con 1 Hija",
            'cambio_vic_vive_con_hijas': "La víctima vive con Hijas",
            'cambio_vic_vive_con_hijastro': "La víctima vive con Hijastro",
            'cambio_vic_vive_con_hijastra': "La víctima vive con Hijastra",
            'cambio_vic_vive_con_1_hermano': "La víctima vive con 1 Hermano",
            'cambio_vic_vive_con_hermanos': "La víctima vive con Hermanos",
            'cambio_vic_vive_con_1_hermana': "La víctima vive con 1 Hermana",
            'cambio_vic_vive_con_hermanas': "La víctima vive con Hermanas",
            'cambio_vic_vive_con_hermanastro': "La víctima vive con Hermanastro",
            'cambio_vic_vive_con_hermanastra': "La víctima vive con Hermanastra",
            'cambio_vic_vive_con_tio': "La víctima vive con Tío",
            'cambio_vic_vive_con_tia': "La víctima vive con Tía",
            'cambio_vic_vive_con_suegro': "La víctima vive con Suegro",
            'cambio_vic_vive_con_suegra': "La víctima vive con Suegra",
            'cambio_vic_vive_con_abuelo': "La víctima vive con Abuelo",
            'cambio_vic_vive_con_abuela': "La víctima vive con Abuela",
            'cambio_vic_vive_con_nieto': "La víctima vive con Nieto",
            'cambio_vic_vive_con_nieta': "La víctima vive con Nieta",
            'cambio_vic_vive_con_otro': "La víctima vive con Otro"
        }
        
        self.select_files_button = ft.ElevatedButton(
            "Seleccionar base de datos (Excel.xlsx/CSV_uft-8)", on_click=self.open_file_picker
        )

        # Botón para procesar los datos
        self.process_data_button = ft.OutlinedButton(
            "Cargar Base de datos", on_click=self.process_data, disabled=True, key="process_data_button"
        )
        # Botón para procesar los datos
        self.data_unstructure = ft.OutlinedButton(
            "Extraer datos para informes o investigación de víctimas, denunciantes jurídicos y acusados", on_click=self.process_data, disabled=True,  key="data_button"
        )

        self.delete_bd = ft.ElevatedButton(
            "Eliminar base de datos", on_click=self.prompt_delete_database,icon="auto_delete",
            icon_color="red400"
        )

    async def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.file_path = e.files[0].path  # Almacenar la ruta del archivo
            self.process_data_button.disabled = False  # Habilitar el botón de procesamiento
            self.data_unstructure.disabled = False
            await self.process_data_button.update_async()  # Actualizar el estado del botón
            await self.data_unstructure.update_async()
        else:
            await self.mostrar_mensaje(self.page, 'No se seleccionaron archivos.', 'error')

    async def pick_files_save_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.file_path_save = e.path  # Configurar la ruta de guardado
            self.directory_selected_event.set()  # Indicar que se ha seleccionado un directorio
        else:
            await self.mostrar_mensaje(self.page, 'No se seleccionaron archivos.', 'error')

    async def read_excel_file(self, file_path):
        try:
            pd.read_excel(file_path, header=0, skiprows=[1])
        except Exception as e:
            await self.mostrar_mensaje(self.page, f"Error al leer el archivo Excel: {e}",'error')

    async def read_csv_file(self, file_path):
        try:
            pd.read_csv(file_path, header=0, skiprows=[1], delimiter=',', encoding='latin-1',errors='ignore')
        except Exception as e:
            await self.mostrar_mensaje(self.page, f'Error al leer el archivo CSV: {e}','error')
            



    async def process_data(self, e):
        if self.file_path:
            try:
                df = None
                if self.file_path.endswith('.xlsx'):
                    df = pd.read_excel(self.file_path, header=0, skiprows=[1])

                elif self.file_path.endswith('.csv'):
                    # Lee el archivo CSV y trata todas las columnas como texto
                    df = pd.read_csv(self.file_path, header=0, skiprows=[1], delimiter=';')

                if df is not None:
                    for col in df.columns:
                        if col != 'fecha_ingreso':  # Saltar la columna fecha_ingreso
                            df[col] = df[col].astype(str)

                    df = df.apply(lambda x: x.str.lower() if x.dtype == "object" else x)

                    # Procesamiento de columnas de tipo objeto
                    for col in df.columns:
                        if df[col].dtype == 'object':
                            df[col] = df[col].map(lambda x: ''.join(c for c in unicodedata.normalize('NFD', x.replace('años', 'anyo').replace('año', 'anyo')) if unicodedata.category(c) != 'Mn') if isinstance(x, str) else x)

                    await self.process_and_normalize_data(df, e)
                else:
                    await self.mostrar_mensaje(self.page, 'Formato de archivo no soportado.')

            except Exception as e:
                print(f'Error al procesar el archivo: {e}', 'error')
                await self.mostrar_mensaje(self.page, f'Error al procesar el archivo: {e}', 'error')
        
        else:
            await self.mostrar_mensaje(self.page, 'Por favor, seleccione un archivo primero.')


            

    async def open_file_picker(self, e):
        await self.file_picker.pick_files_async()

    async def open_get_file(self, e):
        await self.file_picker_save.get_directory_path_async()


    def build(self):
        # Título de la Card
        self.page.overlay.append(self.file_picker)
        self.page.overlay.append(self.file_picker_save)
        title = ft.Text('Carga de Base de Datos', size=24,
                        weight=ft.FontWeight.BOLD)

        # Controles y elementos de la interfaz
        select_files_button_ui = self.select_files_button
        process_data_button_ui = self.process_data_button
        unstructure_data_button = self.data_unstructure
        self.progress_bar = ft.ProgressBar(
            visible=False, width=500, height=30)

        progress_bar_ui = self.progress_bar

        card_content = ft.Column(
            [title, select_files_button_ui, process_data_button_ui, unstructure_data_button,progress_bar_ui,self.delete_bd],
            spacing=20,  
            alignment=ft.MainAxisAlignment.START
        )

        # Crear la Card
        card = ft.Card(elevation=15,
                       width=600,
                       height=400,
                       content=ft.Container(
                           content=card_content,
                           padding=30,
                       ))

        # Barra de navegación lateral (si es parte de tu diseño)
        rail = self.nav_rail_class.create_rail()

        # Diseño final de la página
        return ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                card  #
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    async def process_and_normalize_data(self, df, e):

        if e.control.key == "process_data_button":
            await self.mostrar_mensaje(self.page, 'Comienza el proceso de carga, por favor esperar hasta que la barra cargue completamente')
            await asyncio.sleep(2) 
        elif e.control.key == "data_button":
            await self.mostrar_mensaje(self.page, 'Proceso de destructuración en curso')
            await asyncio.sleep(2) 
        self.progress_bar.visible = True
        self.progress_bar.value = 0
        await self.progress_bar.update_async()
        total_rows = len(df)
        processed_rows = 0

        normalized_victims_data = []
        normalized_denouncers_data = []
        normalized_datos_causa = []
        normalized_antedecentes_delito_data = []
        normalized_datos_audiencia_data = []
        normalized_datos_juicio_completo_data = []
        normalized_datos_denunciantes = []


        max_victims = 5
        max_denounceds = 5
        contador_victimas = 1
        contador_denunciado = 1
        for index, row in df.iterrows():
            row['id_causa'] = index + 1

            normalized_datos_causa.append(self.procesar_datos_causa(row))

            normalized_datos_denunciantes.append(self.procesar_datos_denunciantes(row))

            normalized_antedecentes_delito_data.append(self.procesar_antedecentes_delito(row))

            normalized_datos_audiencia_data.append(self.procesar_datos_audiencia_preparatoria(row))

            normalized_datos_juicio_completo_data.append(self.procesar_datos_juicio_completo(row))
            
            for i in range(1, max_victims + 1):
                # Obtenemos la edad y el sexo de la víctima actual
                vic_edad = row.get(f'vic{i}_edad')
                vic_sexo = row.get(f'vic{i}_sexo')
                # Verificamos si la fila debe ser procesada
                if (vic_edad not in ["no aplica", "sin informacion", 0,"0"]) or (vic_sexo in ["masculino", "femenino"]):
                    es_primer_victima = (i == 1)
                    victim_id = contador_victimas
                    victim_data = self.procesar_datos_victima(row, i, es_primer_victima, victim_id)
                    normalized_victims_data.append(victim_data)
                    contador_victimas += 1
                        
            for j in range(1, max_denounceds + 1):
                denounced_age = row.get(f'den{j}_edad')
                denounced_sex = row.get(f'den{j}_sexo')

                # Agregamos la condición para verificar la edad y el sexo
                if (denounced_age not in ["no aplica", "sin informacion", 0,"0"]) or (denounced_sex in ["masculino", "femenino"]):
                    es_primer_denunciante = (j == 1)
                    denounced_id = contador_denunciado
                    denounced_data = self.procesar_datos_denunciados(row, j, es_primer_denunciante, denounced_id)
                    normalized_denouncers_data.append(denounced_data)
                    contador_denunciado += 1


            processed_rows += 1
            if (processed_rows / total_rows) * 100 >= 0.3:
                self.progress_bar.value = 0.3
                await self.page.update_async()
        print("Realizando transformaciones adicionales.")

        df_normalized_datos_causa = pd.DataFrame(normalized_datos_causa)
        df_normalizado_victimas = pd.DataFrame(normalized_victims_data)
        df_normalizado_denunciados = pd.DataFrame(normalized_denouncers_data)
        df_normalized_datos_denunciantes = pd.DataFrame(normalized_datos_denunciantes)
        # self.df_medidas_juicio

        df_normalized_antedecentes_delito_data = pd.DataFrame(normalized_antedecentes_delito_data)
        df_normalized_antedecentes_delito_data['id_antedecentes_delito'] = range(1, len(df_normalized_antedecentes_delito_data) + 1)

        df_normalized_datos_audiencia_preparatoria = pd.DataFrame(normalized_datos_audiencia_data)
        df_normalized_datos_audiencia_preparatoria['id_audiencia_preparatoria'] = range(1, len(df_normalized_datos_audiencia_preparatoria) + 1)

        df_normalized_datos_juicio_completo_data = pd.DataFrame(normalized_datos_juicio_completo_data)
        df_normalized_datos_juicio_completo_data['id_audiencia_juicio'] = range(1, len(df_normalized_datos_juicio_completo_data) + 1)



        df_transformado_victima_composicion_hogar = self.transformar_dataframe(df_normalizado_victimas, 
                                                                                    self.mapeo_composicion_hogar, 
                                                                                    'id_victima'
                                                                                    )

        df_transformado_cambio_victima_composicion_hogar = self.transformar_dataframe(df_normalizado_victimas, 
                                                                                           self.mapeo_cambio_composicion_hogar, 
                                                                                           'id_victima'
                                                                                           )

        df_transformado_denunciado_vif = self.transformar_dataframe(df_normalizado_denunciados, 
                                                                         self.mapeo_preguntas_vif, 
                                                                         'id_denunciado'
                                                                         )
        df_transformado_denunciado_antecedentes = self.transformar_dataframe(df_normalizado_denunciados, 
                                                                                  self.mapeo_antecedentes, 
                                                                                  'id_denunciado')
        
        df_transformado_policial = self.transformar_dataframe(
                                                            df = df_normalized_antedecentes_delito_data,
                                                            mapeo_preguntas = self.mapeo_preguntas_medidas,
                                                            id_column_name = 'id_antedecentes_delito',
                                                            columns_to_add=['plazo', 'interpone_recurso', 'demanda_reconvencional']
                                                        )
        df_transformado_medidas_preparatoria = self.transformar_dataframe(df_normalized_datos_audiencia_preparatoria, 
                                                                               self.mapeo_preguntas_medidas, 
                                                                               'id_audiencia_preparatoria')

        df_transformado_medida_juicio = self.transformar_dataframe(df_normalized_datos_juicio_completo_data, 
                                                                        self.mapeo_preguntas_medidas, 
                                                                        'id_audiencia_juicio')

        self.progress_bar.value = 0.5  # Actualizar el valor de la barra de progreso
        await self.progress_bar.update_async()

        self.df_tabla_causa = df_normalized_datos_causa.apply(
            lambda col: col.map(self.a_minusculas).map(self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra) 
            if col.dtypes == 'object' else col
            )
  

        columnas_seleccionadas_victima = [
            'id_causa', 
            'id_victima', 
            'vic_rol_rit', 
            'vic_edad', 
            'vic_sexo', 
            'vic_nacionalidad',
            'vic_nacionalidad_Extranjera', 
            'vic_profesion', 'vic_estudios', 
            'vic_parentesco_acusado',
            'vic_parentesco_acusado_otro', 
            'vic_caracter_lesion', 
            'vic_descripcion_lesion', 
            'vic_estado_temperancia',
            'vic_estado_temperancia_otro', 
            'vic_descripcion_temperancia', 
            'vic_comuna', 
            'vic_estado_civil',
            'tiempo_relacion_victima_acusado',
            'vic_parentesco_demandante', 
            'vic_parentesco_demandante_otro', 
            'vic_caracter_lesion_antecedentes',
            'vic_estado_temperancia_antecedentes',
            'vic_violencia_patrimonial',
            'vic_violencia_economica',
            'vic_ayuda_tecnica',
            'vic_ayuda_tecnica_tipo',
            'vic_deterioro_cognitivo',
            'vic_informe_medico',
            'vic_num_enfermedades',
            'vic_listado_enfermedades',
            'vic_inasistencias_salud',
            'vic_informes_social',
            'vic_comuna_ingreso'
        ]
        df_tabla_victima = df_normalizado_victimas[columnas_seleccionadas_victima]
        df_tabla_victima = df_tabla_victima.apply(
            lambda col: col.map(self.a_minusculas).map(self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra)
            if col.dtypes == 'object' else col
            )
        df_tabla_victima['vic_edad'] = df_tabla_victima['vic_edad'].apply(self.procesar_edad)
        mapeo_parentesco = {
            '1': 'conyuge',
            '2': 'ex conyuge',
            '3': 'pareja',
            '4': 'ex pareja',
            '5': 'conviviente',
            '6': 'ex conviviente',
            '7': 'conviviente de hecho',
            '8': 'ex conviviente de hecho',
            '9': 'padre/madre',
            '10': 'padrastro/madrastra',
            '11': 'hijo/a',
            '12': 'hermano/a',
            '13': 'tio/a',
            '14': 'suegro/a',
            '15': 'abuelo/a',
            '16': 'nieto/a',
            '17': 'otro',
            '18': 'no aplica',
            '19': 'sin informacion',
        }
    
        def aplicar_mapeo(valor):
            if isinstance(valor, str) and valor in mapeo_parentesco:
                return mapeo_parentesco[valor]
            else:
                return valor
        # Aplicar el mapeo a la columna vic_parentesco_acusado en minúsculas
        df_tabla_victima['vic_parentesco_acusado'] = df_tabla_victima['vic_parentesco_acusado'].apply(aplicar_mapeo)

        self.df_tabla_victima = df_tabla_victima
        # composición de hogar
        df_transformado_victima_composicion_hogar['id_composicion'] = df_transformado_victima_composicion_hogar.index + 1
        self.df_tabla_composicion_hogar = df_transformado_victima_composicion_hogar.apply(
            lambda col: col.map(self.a_minusculas).map(self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra) 
            if col.dtypes == 'object' else col
            )
        # primero, filtramos el DataFrame
        self.df_tabla_composicion_hogar = self.df_tabla_composicion_hogar[self.df_tabla_composicion_hogar['Respuesta'] == 'si']

        # luego, reseteamos el índice para que comience desde 0 de nuevo
        self.df_tabla_composicion_hogar = self.df_tabla_composicion_hogar.reset_index(drop=True)

        # ahora, asignamos un identificador único que comience en 1
        self.df_tabla_composicion_hogar['id_composicion'] = self.df_tabla_composicion_hogar.index + 1

        # mostramos el DataFrame resultante
        self.df_tabla_composicion_hogar

        # tablas para denunciado y riesgo vif y antecedentes
        columnas_seleccionadas_denunciado = [
            'id_causa', 'id_denunciado', 'den_edad', 'den_sexo',
            'den_nacionalidad', 'den_nacionalidad_extranjera', 'den_profesion', 'den_estudios',
            'den_caracter_lesion', 'den_descripcion_lesion', 'den_estado_temperancia', 'den_estado_temperancia_otro', 'den_descripcion_temperancia',
            'den_comuna', 'den_estado_civil', 'den_otros_antecedentes', 'vif_resultado_nivel', 'vif_resultado_numero'
        ]
        df_tabla_denunciado = df_normalizado_denunciados[columnas_seleccionadas_denunciado]
        df_tabla_denunciado = df_tabla_denunciado.apply(
            lambda col: col.map(self.a_minusculas).map(self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra) 
            if col.dtypes == 'object' else col
            )
        df_tabla_denunciado['den_edad'] = df_tabla_denunciado['den_edad'].apply(self.procesar_edad)
        self.df_tabla_denunciado = df_tabla_denunciado

        df_transformado_denunciado_vif['id_vif'] = df_transformado_denunciado_vif.index + 1
        self.df_tabla_denunciado_vif = df_transformado_denunciado_vif.apply(
            lambda col: col.map(self.a_minusculas).map(self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra) 
            if col.dtypes == 'object' else col)
        

        # filtrar el DataFrame para incluir solo las filas donde 'Respuesta' es 'si'
        self.df_tabla_denunciado_vif = self.df_tabla_denunciado_vif[self.df_tabla_denunciado_vif['Respuesta'] == 'si'].copy()
        # resetear el índice para que comience desde 0
        self.df_tabla_denunciado_vif = self.df_tabla_denunciado_vif.reset_index(drop=True)
        # asignar un identificador único que comience en 1
        self.df_tabla_denunciado_vif['id_vif'] = self.df_tabla_denunciado_vif.index + 1


        self.df_tabla_denunciado_antecedentes = df_transformado_denunciado_antecedentes.apply(
            lambda col: col.map(self.a_minusculas).map(self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra)
              if col.dtypes == 'object' else col
              )
        
        # filtrar el DataFrame para incluir solo las filas donde 'Respuesta' es 'si'
        self.df_tabla_denunciado_antecedentes = self.df_tabla_denunciado_antecedentes[self.df_tabla_denunciado_antecedentes['Respuesta'] == 'si'].copy()
        # resetear el índice para que comience desde 0
        self.df_tabla_denunciado_antecedentes = self.df_tabla_denunciado_antecedentes.reset_index(drop=True)
        # asignar un identificador único que comience en 1
        self.df_tabla_denunciado_antecedentes['id_antecedente'] = self.df_tabla_denunciado_antecedentes.index + 1
        # visualizar el DataFrame resultante
        self.df_tabla_denunciado_antecedentes
        


        # Tabla antededentes delito, correspondiente a la medida

        self.df_tabla_antecetendes_delito = df_normalized_antedecentes_delito_data.apply(lambda col: col.map(self.a_minusculas).map(
            self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra) if col.dtypes == 'object' else col)
        self.df_tabla_antecetendes_delito['id_antecedente_delito'] = self.df_tabla_antecetendes_delito.index + 1

        # Medida policial hay solo 1 causa dentro de antecedentes de delito, asi qeu el mismo IDCASE deberia servir #TODO
        self.df_tabla_medida_policial = df_transformado_policial.apply(lambda col: col.map(self.a_minusculas).map(
            self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra) if col.dtypes == 'object' else col)
        self.df_tabla_medida_policial['id_medida'] = range(1, len(self.df_tabla_medida_policial) + 1)

        # Filtrar el DataFrame para incluir solo las filas donde 'Respuesta' es 'si'
        self.df_tabla_medida_policial = self.df_tabla_medida_policial[self.df_tabla_medida_policial['Respuesta'] == 'si'].copy()

        # Resetear el índice para que comience desde 0
        self.df_tabla_medida_policial = self.df_tabla_medida_policial.reset_index(drop=True)

        # Asignar un identificador único que comience en 1
        self.df_tabla_medida_policial['id_antecedentes_delito'] = self.df_tabla_medida_policial.index + 1

        # Visualizar el DataFrame resultante



        # tabla Aundecia preparatoria y su respectiva medida en el caso
        self.df_tabla_audiencia_preparatoria = df_normalized_datos_audiencia_preparatoria.apply(lambda col: col.map(self.a_minusculas).map(
            self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra) if col.dtypes == 'object' else col)

        # Medida preparatoria
        self.df_tabla_medida_preparatoria = df_transformado_medidas_preparatoria.apply(lambda col: col.map(self.a_minusculas).map(
            self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra) if col.dtypes == 'object' else col)
        self.df_tabla_medida_preparatoria['id_medida'] = range(1, len(self.df_tabla_medida_preparatoria) + 1)



        # Filtrar el DataFrame para incluir solo las filas donde 'Respuesta' es 'si'
        self.df_tabla_medida_preparatoria = self.df_tabla_medida_preparatoria[self.df_tabla_medida_preparatoria['Respuesta'] == 'si'].copy()

        # Resetear el índice para que comience desde 0
        self.df_tabla_medida_preparatoria = self.df_tabla_medida_preparatoria.reset_index(drop=True)

        # Asignar un identificador único que comience en 1
        self.df_tabla_medida_preparatoria['id_medida'] = self.df_tabla_medida_preparatoria.index + 1

        # Visualizar el DataFrame resultante



        # tabla Audencia jucio y su respectiva medida en el caso
        self.df_tabla_audencia_jucio = df_normalized_datos_juicio_completo_data.apply(
            lambda col: col.map(self.a_minusculas).map(self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra)
              if col.dtypes == 'object' else col)
        
        self.df_tabla_audencia_jucio['id_medida'] = range(1, len(self.df_tabla_audencia_jucio) + 1)

        # Medida sentencial del jucio
        self.df_tabla_medida_juicio = df_transformado_medida_juicio.apply(
            lambda col: col.map(self.a_minusculas).map(self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra) 
            if col.dtypes == 'object' else col)
        self.df_tabla_medida_juicio['id_medida'] = range(1, len(self.df_tabla_medida_juicio) + 1)


                # Filtrar el DataFrame para incluir solo las filas donde 'Respuesta' es 'si'
        self.df_tabla_medida_juicio = self.df_tabla_medida_juicio[self.df_tabla_medida_juicio['Respuesta'] == 'si'].copy()

        # Resetear el índice para que comience desde 0
        self.df_tabla_medida_juicio = self.df_tabla_medida_juicio.reset_index(drop=True)

        # Asignar un identificador único que comience en 1
        self.df_tabla_medida_juicio['id_medida'] = self.df_tabla_medida_juicio.index + 1

        # Visualizar el DataFrame resultante


        # conposición de hogar
        self.df_tabla_composicion_hogar_cambio = df_transformado_cambio_victima_composicion_hogar.apply(lambda col: col.map(self.a_minusculas).map(
            self.eliminar_tildes).map(self.quitar_espacios).map(self.quitar_espacios_extra) if col.dtypes == 'object' else col)

            # Primero, filtramos el DataFrame
        self.df_tabla_composicion_hogar_cambio = self.df_tabla_composicion_hogar_cambio[self.df_tabla_composicion_hogar_cambio['Respuesta'] == 'si']

            # Luego, reseteamos el índice para que comience desde 0 de nuevo
        self.df_tabla_composicion_hogar_cambio = self.df_tabla_composicion_hogar_cambio.reset_index(drop=True)

            # Ahora, asignamos un identificador único que comience en 1
        self.df_tabla_composicion_hogar_cambio['id_cambio_composicion'] = self.df_tabla_composicion_hogar_cambio.index + 1

            # Mostramos el DataFrame resultante
        self.df_tabla_composicion_hogar_cambio


        # Denunciantes

        self.df_tabla_denunciantes = df_normalized_datos_denunciantes.apply(
            lambda col: col.map(self.a_minusculas).map(self.eliminar_tildes).map(
                self.quitar_espacios).map(self.quitar_espacios_extra)
            if col.dtypes == 'object' else col
        )

        # Procesa la edad
        self.df_tabla_denunciantes['dtn_edad'] = self.df_tabla_denunciantes['dtn_edad'].apply(
            self.procesar_edad)

        # Agrega la columna 'tipo_relacion'
        self.df_tabla_denunciantes['tipo_relacion'] = range(
            1, len(self.df_tabla_denunciantes) + 1)
        # Asumiendo que df_tabla_victima y df_tabla_denunciado ya están definidos y procesados
     
        # Seleccionar las columnas relevantes de cada DataFrame
        columnas_victima = ['id_causa', 'id_victima',
                            'vic_representante_legal', 'juicio_vic_representante_legal']
        columnas_denunciado = ['id_causa', 'id_denunciado',
                               'den_representante_legal', 'juicio_den_representante_legal']
        columna_denunciantes = [
            'id_causa', 'dtn_representante_Legal', 'dtn_juicio_representante_legal']

        # Crear DataFrames más pequeños con solo las columnas seleccionadas
        df_victima_reducido = df_normalizado_victimas[columnas_victima]
        df_denunciado_reducido = df_normalizado_denunciados[columnas_denunciado]
        df_denunciantes_reducido = self.df_tabla_denunciantes[columna_denunciantes]
        df_denunciantes_reducido = df_denunciantes_reducido.copy()
        df_denunciantes_reducido['tipo_relacion'] = range(
            1, len(df_denunciantes_reducido) + 1)

        self.df_involucrados_audencia_preparatoria_y_juicio = self.combinar_y_procesar(
            df_victima_reducido, df_denunciado_reducido, df_denunciantes_reducido)

        self.df_involucrados_audencia_preparatoria_y_juicio['id_involucrados'] = range(
            1, len(self.df_involucrados_audencia_preparatoria_y_juicio) + 1)

        self.df_involucrados_audencia_preparatoria_y_juicio = self.df_involucrados_audencia_preparatoria_y_juicio.apply(
            lambda col: col.map(self.a_minusculas).map(self.eliminar_tildes).map(
                self.quitar_espacios).map(self.quitar_espacios_extra)
            if col.dtypes == 'object' else col
        )


        # Asegúrate de que los IDs sean numéricos o NaN. Si no lo son, conviértelos primero.
        self.df_involucrados_audencia_preparatoria_y_juicio['id_victima'] = pd.to_numeric(self.df_involucrados_audencia_preparatoria_y_juicio['id_victima'], errors='coerce')
        self.df_involucrados_audencia_preparatoria_y_juicio['id_denunciado'] = pd.to_numeric(self.df_involucrados_audencia_preparatoria_y_juicio['id_denunciado'], errors='coerce')
        self.df_involucrados_audencia_preparatoria_y_juicio['tipo_relacion'] = pd.to_numeric(self.df_involucrados_audencia_preparatoria_y_juicio['tipo_relacion'], errors='coerce')

        # Filtrar las filas donde todos los IDs son numéricos (no NaN)
        self.df_involucrados_audencia_preparatoria_y_juicio = self.df_involucrados_audencia_preparatoria_y_juicio.dropna(subset=['id_victima', 'id_denunciado','tipo_relacion'], how='any')

        df_tabla_denunciante_es_victima = self.df_tabla_denunciantes[self.df_tabla_denunciantes['es_victima'] == 'si']
        df_tabla_denunciante_es_victima = df_tabla_denunciante_es_victima[['id_causa','dtn_edad','dtn_sexo','dtn_nacionalidad','dtn_nacionalidad_Extranjera','dtn_profesion','dtn_estudios','dtn_parentesco_Acusado','dtn_parentesco_Acusado_Otro','dtn_caracter_Lesion','dtn_descripcion_Lesion','dtn_estado_Temperancia','dtn_estado_Temperancia_Otro','dtn_descripcion_Temperancia','dtn_comuna','dtn_estado_civil']]
        df_tabla_victima_exportacion = self.df_tabla_victima[['id_causa','vic_edad','vic_sexo','vic_nacionalidad','vic_nacionalidad_Extranjera','vic_profesion','vic_estudios','vic_parentesco_acusado','vic_parentesco_acusado_otro','vic_caracter_lesion','vic_descripcion_lesion','vic_estado_temperancia','vic_estado_temperancia_otro','vic_descripcion_temperancia','vic_comuna','vic_estado_civil']]

        df_tabla_denunciante_es_victima = df_tabla_denunciante_es_victima.rename(columns={
                                                        'dtn_edad':'vic_edad',
                                                    'dtn_sexo':'vic_sexo',
                                                    'dtn_nacionalidad':'vic_nacionalidad',
                                                    'dtn_nacionalidad_Extranjera':'vic_nacionalidad_Extranjera',
                                                    'dtn_profesion':'vic_profesion',
                                                    'dtn_estudios':'vic_estudios',
                                                    'dtn_parentesco_Acusado':'vic_parentesco_acusado',
                                                    'dtn_parentesco_Acusado_Otro':'vic_parentesco_acusado_otro',
                                                    'dtn_caracter_lesion':'vic_caracter_lesion',
                                                    'dtn_descripcion_Lesion':'vic_descripcion_lesion',
                                                    'dtn_estado_Temperancia':'vic_estado_temperancia',
                                                    'dtn_estado_Temperancia_Otro':'vic_estado_temperancia_otro',
                                                    'dtn_descripcion_Temperancia	':'vic_descripcion_temperancia',
                                                    'dtn_comuna':'vic_comuna',
                                                    'dtn_estado_civil':'vic_estado_civil'
                                                    })
        df_combinado_victimas_denunciantes = pd.concat([df_tabla_victima_exportacion,df_tabla_denunciante_es_victima],ignore_index=True)
        df_tabla_causa_reducido = self.df_tabla_causa[['id_causa', 'fecha_ingreso', 'via_ingreso']]

        # Realizamos un merge (unión) de los DataFrames en la columna 'id_causa'
        df_combinado_victimas_denunciantes = pd.merge(df_combinado_victimas_denunciantes, 
                                                    df_tabla_causa_reducido, 
                                                    on='id_causa', 
                                                    how='left')
        

        bins = [0, 1, 18, 59, float('inf')]
        labels = ['desconocido', '1-17', '18-59', '60+']
        df_combinado_victimas_denunciantes['rango_edad'] = pd.cut(df_combinado_victimas_denunciantes['vic_edad'], bins=bins, labels=labels, right=True, include_lowest=True)
        df_combinado_victimas_denunciantes = df_combinado_victimas_denunciantes.drop('vic_edad', axis=1)
        # Definimos los límites de los rangos de edad y sus etiquetas correspondientes
        bins = [0, 1, 18, 59, float('inf')]
        labels = ['desconocido', '1-17', '18-59', '60+']
        

        df_tabla_denunciado_exportacion = self.df_tabla_denunciado
        df_tabla_denunciado_exportacion['rango_edad'] = pd.cut(self.df_tabla_denunciado['den_edad'], bins=bins, labels=labels, right=True, include_lowest=True)
        # Eliminamos la columna de edad original
        df_tabla_denunciado_exportacion = df_tabla_denunciado_exportacion.drop('den_edad', axis=1)

        df_filtrado_instituciones = self.df_tabla_denunciantes[
            (self.df_tabla_denunciantes['es_persona_juridica'] == 'si') &
            (self.df_tabla_denunciantes['es_victima'] != 'si')
        ]


        if e.control.key == "process_data_button":
            self.progress_bar.value = 0.5  # Actualizar el valor de la barra de progreso
            await self.progress_bar.update_async()
            await self.insertar_datos_en_bd()
            await self.mostrar_mensaje(self.page, 'Carga en la base de datos completada')


        elif e.control.key == "data_button":
            await self.open_get_file(e)

            # Esperar hasta que se seleccione un directorio
            await self.directory_selected_event.wait()
            # Definir una función para limpiar las columnas

            def fill_empty_cells(df, fill_value='no aplica'):
                return df.apply(lambda x: x.map(lambda y: fill_value if pd.isna(y) or y == '' or (isinstance(y, str) and y.isspace()) else y))

            # Aplicar la función a las columnas que contienen 'ann' en cada DataFrame
            df_combinado_victimas_denunciantes = fill_empty_cells(df_combinado_victimas_denunciantes)
            df_tabla_denunciado_exportacion = fill_empty_cells(df_tabla_denunciado_exportacion)
            df_filtrado_instituciones = fill_empty_cells(df_filtrado_instituciones)
            df_combinado_victimas_denunciantes['fecha_ingreso'] = pd.to_datetime(df_combinado_victimas_denunciantes['fecha_ingreso'], format='%d-%m-%Y')
            df_combinado_victimas_denunciantes['fecha_ingreso'] = df_combinado_victimas_denunciantes['fecha_ingreso'].dt.year

            dfs_dict = {
                'df_victimas': df_combinado_victimas_denunciantes, 
                'df_denunciado': df_tabla_denunciado_exportacion, 
                'df_denunciantes_instituciones': df_filtrado_instituciones,
            }
            await asyncio.sleep(2)  
            await self.exportar_dfs_a_excel(dfs_dict)
            await self.mostrar_mensaje(self.page, f'Archivos guardadados en {self.file_path_save}')

    

        self.progress_bar.value = 1.0
        await self.progress_bar.update_async()

    async def exportar_dfs_a_excel(self, dfs_dict):
        try:
            # Usar la ruta de guardado seleccionada o una ruta predeterminada
            base_dir = self.file_path_save 

            # Crear la carpeta si no existe
            os.makedirs(base_dir, exist_ok=True)

            # Iterar sobre cada DataFrame y guardarlo en la ruta especificada
            for nombre_archivo, df in dfs_dict.items():
                # Ruta completa del archivo Excel a guardar
                excel_path = os.path.join(base_dir, f'{nombre_archivo}.xlsx')
                # Guardar el DataFrame en un archivo Excel
                df.to_excel(excel_path, index=False)

        except Exception as e:
            print(f"Error al guardar los archivos Excel: {e}")


        
    async def insertar_datos_en_bd(self):

        # Insertar datos de cada tabla
        await self.mostrar_mensaje(self.page, 'Iniciando la inserción de datos en la base de datos...')

        await self.mostrar_mensaje(self.page, 'Insertando causas...')
        await self.insertar_causas_en_bd()
        self.progress_bar.value = 0.53 
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando datos de víctimas...')
        await self.insertar_datos_tabla_victima()
        self.progress_bar.value = 0.56
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando datos de composición del hogar...')
        await self.insertar_datos_tabla_composicion_hogar()
        self.progress_bar.value = 0.59
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando datos del denunciado...')
        await self.insertar_datos_tabla_denunciado()
        self.progress_bar.value = 0.63
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando antecedentes del denunciado...')
        await self.insertar_datos_tabla_antecedentes_denunciado()
        self.progress_bar.value = 0.66
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando datos de riesgo VIF...')
        await self.insertar_datos_tabla_riesgo_vif()
        self.progress_bar.value = 0.70
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando datos del denunciante...')
        await self.insertar_datos_tabla_denunciante()
        self.progress_bar.value = 0.73
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando antecedentes del delito...')
        await self.insertar_datos_tabla_antecedentes_delito()
        self.progress_bar.value = 0.76
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando medidas policiales...')
        await self.insertar_datos_tabla_medida_policial()
        self.progress_bar.value = 0.80
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando datos de la audiencia preparatoria...')
        await self.insertar_datos_tabla_audiencia_preparatoria()
        self.progress_bar.value = 0.83
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando medidas preparatorias...')
        await self.insertar_datos_tabla_medida_preparatoria()
        self.progress_bar.value = 0.86
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando datos de la audiencia de juicio...')
        await self.insertar_datos_tabla_audiencia_juicio()
        self.progress_bar.value = 0.90
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando medidas de juicio...')
        await self.insertar_datos_tabla_medida_juicio()
        self.progress_bar.value = 0.92
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando cambios en la composición del hogar...')
        await self.insertar_datos_tabla_composicion_hogar_cambio()
        self.progress_bar.value = 0.94
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando relaciones de la audiencia preparatoria...')
        await self.insertar_relaciones_audiencia_preparatoria()
        self.progress_bar.value = 0.96
        await self.progress_bar.update_async()
        await self.mostrar_mensaje(self.page, 'Insertando relaciones de la audiencia de juicio...')
        await self.insertar_relaciones_audiencia_juicio()
     

    async def insertar_causas_en_bd(self):
        #print(self.df_tabla_causa)
        for index, row in self.df_tabla_causa.iterrows():
            # Verifica si la causa ya existe en la base de datos
            existe_causa = await self.db.existe_causa(row['id_causa'])
            # Solo inserta la causa si no existe
            if not existe_causa:
                causa = Causa(
                    digitador=row['digitador'],
                    rol_rit=row['rol_rit'],
                    fecha_ingreso=row['fecha_ingreso'],
                    cartulado=row['caratulado'],
                    procedimiento=row['procedimiento'],
                    materia=row['materia'],
                    estado_admin=row['estado_admin'],
                    ubicacion=row['ubicacion'],
                    cuaderno=row['cuaderno'],
                    etapa=row['etapa'],
                    estado_procesal=row['estado_proceso'],
                    etapa_actual=row['etapa_actual'],
                    via_ingreso=row['via_ingreso'],
                    causa_proteccion_abierta=row['causa_proteccion_abierta'],
                    causa_penal_abierta=row['causa_penal_abierta'],
                    id_causa=row['id_causa']
                )
                await self.db.add_causa(causa)

    async def insertar_datos_tabla_victima(self):
        #print(self.df_tabla_victima)
        for index, row in self.df_tabla_victima.iterrows():
            existe_victima = await self.db.existe_victima(row['id_victima'])
            if not existe_victima:
                victima = Victima(
                    id_causa=row['id_causa'],
                    edad=row['vic_edad'],
                    sexo=row['vic_sexo'],
                    nacionalidad=row['vic_nacionalidad'],
                    nacionalidad_extranjera=row['vic_nacionalidad_Extranjera'],
                    profesion_oficio=row['vic_profesion'],
                    estudios=row['vic_estudios'],
                    parentesco_acusado=row['vic_parentesco_acusado'],
                    parentesco_acusado_otro=row['vic_parentesco_acusado_otro'],
                    caracter_lesion=row['vic_caracter_lesion'],
                    descripcion_lesion=row['vic_descripcion_lesion'],
                    estado_temperancia=row['vic_estado_temperancia'],
                    estado_temperancia_otro=row['vic_estado_temperancia_otro'],
                    descripcion_temperancia=row['vic_descripcion_temperancia'],
                    comuna=row['vic_comuna'],
                    tiempo_relacion=row['tiempo_relacion_victima_acusado'],
                    estado_civil=row['vic_estado_civil'],
                    parentesco_denunciante=row['vic_parentesco_demandante'],
                    parentesco_denunciante_otro=row['vic_parentesco_demandante_otro'],
                    violencia_patrimonial=row['vic_violencia_patrimonial'],
                    vic_violencia_economica=row['vic_violencia_economica'],
                    vic_ayuda_tecnica=row['vic_ayuda_tecnica'],
                    vic_ayuda_tecnica_tipo=row['vic_ayuda_tecnica_tipo'],
                    vic_deterioro_cognitivo=row['vic_deterioro_cognitivo'],
                    vic_informe_medico=row['vic_informe_medico'],
                    vic_num_enfermedades=row['vic_num_enfermedades'],
                    vic_inasistencias_salud=row['vic_inasistencias_salud'],
                    vic_informes_social=row['vic_informes_social'],
                    vic_comuna_ingreso=row['vic_comuna_ingreso'],
                    listado_enfermedades=row['vic_listado_enfermedades'],
                    id_victima=row['id_victima']
                )
                await self.db.add_victima(row['id_causa'], victima=victima)

    async def insertar_datos_tabla_composicion_hogar(self):
        #print(self.df_tabla_composicion_hogar)
        for index, row in self.df_tabla_composicion_hogar.iterrows():
            # Aquí asumimos que tienes una función para verificar si la composición de hogar ya existe
            existe_composicion = await self.db.existe_composicion_hogar(row['id_composicion'])

            if not existe_composicion:
                composicion_hogar = ComposicionHogar(
                    id_victima=row['id_victima'],
                    tipo_relacion=row['Tipo'],
                    respuesta=row['Respuesta'],
                    cantidad=0
                )
                await self.db.add_composition(row['id_victima'], composicion_hogar)

    async def insertar_datos_tabla_denunciado(self):
        #print(self.df_tabla_denunciado)
        for index, row in self.df_tabla_denunciado.iterrows():
            if not await self.db.existe_denunciado(row['id_denunciado']):
                denunciado = Denunciado(
                    id_causa=row['id_causa'],
                    edad=row['den_edad'],
                    sexo=row['den_sexo'],
                    nacionalidad=row['den_nacionalidad'],
                    nacionalidad_extranjera=row['den_nacionalidad_extranjera'],
                    profesion_oficio=row['den_profesion'],
                    estudios=row['den_estudios'],
                    caracter_lesion=row['den_caracter_lesion'],
                    lesiones_descripcion=row['den_descripcion_lesion'],
                    estado_temperancia=row['den_estado_temperancia'],
                    temperancia_otro=row['den_estado_temperancia_otro'],
                    temperancia_descripcion=row['den_descripcion_temperancia'],
                    estado_civil=row['den_estado_civil'],
                    otros_antecedentes=row['den_otros_antecedentes'],
                    comuna=row['den_comuna'],
                    nivel_riesgo=row['vif_resultado_nivel'],
                    vif_numero=row['vif_resultado_numero'],
                    id_denunciado=row['id_denunciado'],
                )
                await self.db.add_denunciado(row['id_causa'], denunciado)

    async def insertar_datos_tabla_antecedentes_denunciado(self):
        for index, row in self.df_tabla_denunciado_antecedentes.iterrows():
            if not await self.db.existe_antecedente_denunciado(row['id_antecedente']):
                antecedente = AntecedentesDenunciado(
                    id_denunciado=row['id_denunciado'],
                    tipo_antecedente=row['Tipo'],
                    descripcion=row['Respuesta']
                )
                # Llama aquí a tu método para agregar el antecedente a la base de datos
                await self.db.add_antecedentes_denunciado(row['id_denunciado'], antecedente)

    async def insertar_datos_tabla_riesgo_vif(self):
        for index, row in self.df_tabla_denunciado_vif.iterrows():
            if not await self.db.existe_indicador_riesgo_vif(row['id_vif']):
                indicador_vif = DenunciadoIndicadoresRiesgoVIF(
                    id_denunciado=row['id_denunciado'],
                    descripcion_indicador=row['Tipo'],
                    respuesta=row['Respuesta']
                )
                await self.db.add_indicador_riesgo_vif(row['id_denunciado'], indicador_vif)

    async def insertar_datos_tabla_denunciante(self):
        for index, row in self.df_tabla_denunciantes.iterrows():
            if not await self.db.existe_denunciante(row['tipo_relacion']):
                denunciante = Denunciante(
                    id_causa=row['id_causa'],
                    es_denunciante_victima=row['es_victima'],
                    es_denunciante_persona_juridica=row['es_persona_juridica'],
                    nombre_persona_juridica=row['dtn_persona_juridica_cual'],
                    edad_denunciante=row['dtn_edad'],
                    sexo_denunciante=row['dtn_sexo'],
                    nacionalidad_denunciante=row['dtn_nacionalidad'],
                    nacionalidad_extranjera_denunciante=row['dtn_nacionalidad_Extranjera'],
                    profesion_oficio_denunciante=row['dtn_profesion'],
                    estudios_denunciante=row['dtn_estudios'],
                    parentesco_acusado=row['dtn_parentesco_Acusado'],
                    parentesco_acusado_otro=row['dtn_parentesco_Acusado_Otro'],
                    caracter_lesion_denunciante=row['dtn_caracter_Lesion'],
                    descripcion_lesion_denunciante=row['dtn_descripcion_Lesion'],
                    estado_temperancia_denunciante=row['dtn_estado_Temperancia'],
                    estado_temperancia_denunciante_otro=row['dtn_estado_Temperancia_Otro'],
                    descripcion_temperancia_denunciante=row['dtn_descripcion_Temperancia'],
                    comuna=row['dtn_comuna'],
                    estado_civil=row['dtn_estado_civil'],
                )
                await self.db.add_denunciante(row['id_causa'], denunciante)

    async def insertar_datos_tabla_antecedentes_delito(self):
        for index, row in self.df_tabla_antecetendes_delito.iterrows():
            if not await self.db.existe_antecedente_delito(row['id_antecedente_delito']):
                antecedente_delito = AntecedentePolicial(
                    id_causa=row['id_causa'],
                    codigo_delito=row['codigo_delito'],
                    fecha_delito=row['fecha_delito'],
                    hora_delito=row['hora_delito'],
                    lugar_ocurrencia=row['lugar_ocurrencia'],
                    lugar_ocurrencia_otro=row['lugar_ocurrencia_otro'],
                    comuna=row['comuna_delito'],
                    unidad=row['unidad_policial'],
                    cuadrante=row['cuadrante_delito']
                )
                await self.db.add_antecedente_policial(row['id_causa'], antecedente_delito)

    async def insertar_datos_tabla_medida_policial(self):
        for index, row in self.df_tabla_medida_policial.iterrows():
            if not await self.db.existe_medida_policial(row['id_medida']):
                medida_policial = MedidaCautelarEspecial(
                    id_evento=row['id_medida'],
                    tipo_medida=row['Tipo'],
                    respuesta=row['Respuesta'],
                    plazo=row['plazo'],
                    interpone_recurso= row['interpone_recurso'],
                    demanda_reconvencional= row['demanda_reconvencional']
                )
                await self.db.add_medida_policial(row['id_antedecentes_delito'], medida_policial)

    async def insertar_datos_tabla_audiencia_preparatoria(self):
        for index, row in self.df_tabla_audiencia_preparatoria.iterrows():
            if not await self.db.existe_audiencia_preparatoria(row['id_audiencia_preparatoria']):
                audiencia_preparatoria = AudienciaPreparatoria(
                    id_causa=row['id_causa'],
                    fecha_citacion=row['fecha_primera_citacion'],
                    fecha_realizacion=row['fecha_realizacion_audiencia'],
                    suspension_anterior=row['audiencia_suspendida'],
                    solicita_informes_oficios=row['pre_solicitan_informes_oficios'],
                    resolucion=row['resolucion_audiencia'],
                    salida_colaborativa=row['resolucion_salida_colaborativa'],
                    otras_observaciones="",  # Puedes adaptar esto según tus necesidades
                    informes_solicitados_a_quien =  row['pre_solicitan_informes_oficios'],
                    informes_entregados = row['informes_entregados'],
                    informes_entregados_cuales = row['informes_entregados_cuales'],
                    informes_pendientes = row['informes_pendientes'],
                    demora_entrega_informes = row['demora_entrega_informes'],
                    pericia_solicitada = row['pericia_solicitada'],
                    pericia_cual = row['pericia_cual'],
                    pericia_solicitante = row['pericia_solicitante']
                )
                await self.db.add_audiencia_preparatoria(row['id_causa'], audiencia_preparatoria)

    async def insertar_datos_tabla_medida_preparatoria(self):
        for index, row in self.df_tabla_medida_preparatoria.iterrows():
            
            if not await self.db.existe_medida_preparatoria(row['id_medida']):
                medida_preparatoria = MedidaCautelar(
                    id_evento=row['id_medida'],
                    tipo_medida=row['Tipo'],
                    respuesta=row['Respuesta'],
                    plazo='',
                )
                await self.db.add_medida_cautelar_preparatoria(row['id_audiencia_preparatoria'], medida_preparatoria)

    async def insertar_datos_tabla_audiencia_juicio(self):
        for index, row in self.df_tabla_audencia_jucio.iterrows():
            if not await self.db.existe_audiencia_juicio(row['id_audiencia_juicio']):
                audiencia_juicio = AudienciaJuicioAntecedentes(
                id_causa=row['id_causa'],
                fecha_citacion=row['fecha_primera_citacion_juicio'],
                fecha_realizacion=row['fecha_realizacion'],
                cambio_composicion_hogar=row['cambio_composicion_hogar_juicio'],
                suspendido=row['juicio_audiencia_suspendida'],
                resolucion=row['juicio_resolucion'],
                sentencia=row['juicio_sentencia_cual'],
                salida_colaborativa=row['juicio_salida_colaborativa_cual'],
                carabineros_informa_cese_medidas=row['juicio_carabineros_cese_medidas'],
                recurso_procesal=row['sentencia_recurso_procesal'],
                recurso_procesal_otro=row['sentencia_recurso_procesal_otro'],
                abre_causa_cumplimiento=row['causa_cumplimiento_abierta'],
                causa_cumplimiento_rol_rit=row['causa_cumplimiento_rol_rit'],
                solicitan_informes_oficios=row['solicitan_informes_oficios'],
                informes_solicitados_a_quien=row['juicio_informes_solicitados_a_quien'],
                informes_entregados=row['informes_entregados'],
                informes_entregados_cuales=row['informes_entregados_cuales'],
                informes_pendientes=row['informes_pendientes'],
                demora_informes=row['demora_informes'],
                suspension_condicional=row['suspension_condicional'],
                otro_acuerdo_cual=row['otro_acuerdo_cual'],
                pericia_solicitada=row['pericia_solicitada'],
                pericia_cual=row['pericia_cual'],
                pericia_solicitante=row['pericia_solicitante'],
                pericia_resultado=row['pericia_resultado'],
                pericia_evaluado=row['pericia_evaluado'],
                medidas_cautelares=row['medidas_cautelares'],
                medidas_recurso=row['medidas_recurso'],
            )
            await self.db.add_audiencia_juicio(row['id_causa'], audiencia_juicio)

    async def insertar_datos_tabla_medida_juicio(self):
        for index, row in self.df_tabla_medida_juicio.iterrows():
            if not await self.db.existe_medida_juicio(row['id_medida']):
                medidas_juicio = MedidaCautelar(
                    id_evento=row['id_medida'],
                    tipo_medida=row['Tipo'],
                    respuesta=row['Respuesta'],
                    plazo='',
                )
                await self.db.add_medida_provisoria_juicio(row['id_audiencia_juicio'], medidas_juicio)

    async def insertar_datos_tabla_composicion_hogar_cambio(self):
        for index, row in self.df_tabla_composicion_hogar_cambio.iterrows():
            existe_composicion = await self.db.existe_composicion_hogar_cambio(row['id_cambio_composicion'])
            if not existe_composicion:
                composicion_hogar = ComposicionHogarEnJuicio(
                    id_victima=row['id_victima'],
                    tipo_relacion=row['Tipo'],
                    respuesta=row['Respuesta'],
                    cantidad=0,  # Considera actualizar este valor
                    # Asegúrate de que este es el ID correcto
                    id_juicio=row['id_causa']
                )
                await self.db.add_composicion_hogar_en_juicio(row['id_causa'], composicion_hogar)

    # Suponiendo que df_victimas y df_denunciados son tus DataFrames para víctimas y denunciados
    async def insertar_relaciones_audiencia_preparatoria(self):
        for index, row in self.df_involucrados_audencia_preparatoria_y_juicio.iterrows():
            existe_audiencia_preparatoria_relacion = await self.db.existe_audiencia_preparatoria_relacion(row['id_involucrados'])
            if not existe_audiencia_preparatoria_relacion:
                audiencia_relacion = AudienciaRelaciones(
                    id_audiencia=row['id_causa'],
                    id_victima=row['id_victima'],
                    id_denunciado=row['id_denunciado'],
                    tipo_relacion=row['tipo_relacion'],
                    victima_representante_legal=row['vic_representante_legal'],
                    denunciado_representante_legal=row['den_representante_legal'],
                    denunciante_representante_legal=row['dtn_representante_Legal']
                )
                await self.db.add_audiencia_preparatoria_relacion(row['id_causa'], audiencia_relacion)

    async def insertar_relaciones_audiencia_juicio(self):
        for index, row in self.df_involucrados_audencia_preparatoria_y_juicio.iterrows():
            existe_audiencia_preparatoria_relacion = await self.db.existe_audiencia_juicio_relacion(row['id_involucrados'])
            if not existe_audiencia_preparatoria_relacion:
                audiencia_relacion = AudienciaRelaciones(
                    id_audiencia=row['id_causa'],
                    id_victima=row['id_victima'],
                    id_denunciado=row['id_denunciado'],
                    tipo_relacion=row['tipo_relacion'],
                    victima_representante_legal=row['juicio_vic_representante_legal'],
                    denunciado_representante_legal=row['juicio_den_representante_legal'],
                    denunciante_representante_legal=row['dtn_juicio_representante_legal']
                )
                await self.db.add_audiencia_juicio_relacion(row['id_causa'], audiencia_relacion)

    def procesar_datos_victima(self, row, i,es_primer_victima,victim_id):
        # Procesa y devuelve los datos de una víctima específica
        victima_data = {
            'id_causa': row['id_causa'],
            'id_victima': victim_id,
            'vic_rol_rit': row['rol_rit'],
            'vic_edad': row.get(f'vic{i}_edad', None),
            'vic_sexo': row.get(f'vic{i}_sexo', "sin informacion"),
            'vic_nacionalidad': row.get(f"vic{i}_nacionalidad", "sin informacion"),
            'vic_nacionalidad_Extranjera': row.get(f"vic{i}_nacionalidad_extranjera", "sin informacion"),
            'vic_profesion': row.get(f"vic{i}_profesion","Sin informacion"),
            'vic_estudios': row.get(f'vic{i}_estudios',"Sin informacion"),
            'vic_parentesco_acusado': row.get(f'vic{i}_parentesco_acusado',"sin informacion"),
            'vic_parentesco_acusado_otro': row.get(f'vic{i}_parentesco_acusado_otro',"sin informacion"),
            'vic_caracter_lesion': row.get(f'vic{i}_caracter_lesion',"sin informacion"),
            'vic_descripcion_lesion': row.get(f'vic{i}_descripcion_lesion',"sin informacion"),
            'vic_estado_temperancia': row.get(f'vic{i}_estado_temperancia',"sin informacion"),
            'vic_estado_temperancia_otro': row.get(f'vic{i}_estado_temperancia_otro',"sin informacion"),
            'vic_descripcion_temperancia': row.get(f'vic{i}_descripcion_temperancia',"sin informacion"),
            'vic_comuna': row.get(f'vic{i}_comuna',"sin informacion"),
            'vic_estado_civil': row.get(f'vic{i}_estado_civil',"sin informacion"),
            'vic_parentesco_demandante': row.get(f'vic{i}_parentesco_demandante',"sin informacion"),
            'vic_parentesco_demandante_otro': row.get(f'vic{i}_parentesco_demandante_otro',"sin informacion"),
            'vic_caracter_lesion_antecedentes': row.get(f'vic1_caracter_lesion_antecedentes','sin informacion'),
            'vic_estado_temperancia_antecedentes': row.get(f'vic{i}_estado_temperancia_antecedentes'),
            
            #campos nuevos!!!!!!!!
            'vic_violencia_patrimonial': row.get(f'vic{i}_violencia_economica'),
            'vic_violencia_economica': row.get(f'vic{i}_violencia_economica'),
            'vic_ayuda_tecnica': row.get(f'vic{i}_ayuda_tecnica'),
            'vic_ayuda_tecnica_tipo': row.get(f'vic{i}_ayuda_tecnica_tipo'),
            'vic_deterioro_cognitivo': row.get(f'vic{i}_deterioro_cognitivo'),
            'vic_informe_medico': row.get(f'vic{i}_informe_medico'),
            'vic_num_enfermedades': row.get(f'vic{i}_num_enfermedades'),
            'vic_listado_enfermedades': row.get(f'vic{i}_listado_enfermedades'),
            'vic_inasistencias_salud':row.get(f'vic{i}_inasistencias_salud'),
            'vic_informes_social': row.get(f'vic{i}_informes_social'),
            'vic_comuna_ingreso': "sin informacion" if not es_primer_victima else row.get(f'vic_comuna_ingreso'),


            # Campos de convivencia
            'vic_tipo_hogar': row.get(f'vic{i}_tipo_hogar', 'sin informacion'),
            'vic_vive_con_conyuge': row.get(f'vic{i}_vive_con_conyuge', 'sin informacion'),
            'vic_vive_con_exconyuge': row.get(f'vic{i}_vive_con_exconyuge', 'sin informacion'),
            'vic_vive_con_pareja': row.get(f'vic{i}_vive_con_pareja', 'sin informacion'),
            'vic_vive_con_expareja': row.get(f'vic{i}_vive_con_expareja', 'sin informacion'),
            'vic_vive_con_conviviente_auc': row.get(f'vic{i}_vive_con_conviviente_auc', 'sin informacion'),
            'vic_vive_con_exconviviente_auc': row.get(f'vic{i}_vive_con_exconviviente_auc', 'sin informacion'),
            'vic_vive_con_conviviente_hecho': row.get(f'vic{i}_vive_con_conviviente_hecho', 'sin informacion'),
            'vic_vive_con_exconviviente_hecho': row.get(f'vic{i}_vive_con_exconviviente_hecho', 'sin informacion'),
            'vic_vive_con_papa': row.get(f'vic{i}_vive_con_papa', 'sin informacion'),
            'vic_vive_con_mama': row.get(f'vic{i}_vive_con_mama', 'sin informacion'),
            'vic_vive_con_padrastro': row.get(f'vic{i}_vive_con_padrastro', 'sin informacion'),
            'vic_vive_con_madrastra': row.get(f'vic{i}_vive_con_madrastra', 'sin informacion'),
            'vic_vive_con_1_hijo': row.get(f'vic{i}_vive_con_1_hijo', 'sin informacion'),
            'vic_vive_con_hijos': row.get(f'vic{i}_vive_con_hijos', 'sin informacion'),
            'vic_vive_con_1_hija': row.get(f'vic{i}_vive_con_1_hija', 'sin informacion'),
            'vic_vive_con_hijas': row.get(f'vic{i}_vive_con_hijas', 'sin informacion'),
            'vic_vive_con_hijastro': row.get(f'vic{i}_vive_con_hijastro', 'sin informacion'),
            'vic_vive_con_hijastra': row.get(f'vic{i}_vive_con_hijastra', 'sin informacion'),
            'vic_vive_con_1_hermano': row.get(f'vic{i}_vive_con_1_hermano', 'sin informacion'),
            'vic_vive_con_hermanos': row.get(f'vic{i}_vive_con_hermanos', 'sin informacion'),
            'vic_vive_con_1_hermana': row.get(f'vic{i}_vive_con_1_hermana', 'sin informacion'),
            'vic_vive_con_hermanas': row.get(f'vic{i}_vive_con_hermanas', 'sin informacion'),
            'vic_vive_con_hermanastro': row.get(f'vic{i}_vive_con_hermanastro', 'sin informacion'),
            'vic_vive_con_hermanastra': row.get(f'vic{i}_vive_con_hermanastra', 'sin informacion'),
            'vic_vive_con_tio': row.get(f'vic{i}_vive_con_tio', 'sin informacion'),
            'vic_vive_con_tia': row.get(f'vic{i}_vive_con_tia', 'sin informacion'),
            'vic_vive_con_suegro': row.get(f'vic{i}_vive_con_suegro', 'sin informacion'),
            'vic_vive_con_suegra': row.get(f'vic{i}_vive_con_suegra', 'sin informacion'),
            'vic_vive_con_abuelo': row.get(f'vic{i}_vive_con_abuelo', 'sin informacion'),
            'vic_vive_con_abuela': row.get(f'vic{i}_vive_con_abuela', 'Sin informacion'),
            'vic_vive_con_nieto': row.get(f'vic{i}_vive_con_nieto', 'sin informacion'),
            'vic_vive_con_nieta': row.get(f'vic{i}_vive_con_nieta', 'sin informacion'),
            'vic_vive_con_otro': row.get(f'vic{i}_vive_con_otro', 'sin informacion'),   
            # representante legal en preparatoria y en jucio

            'vic_representante_legal': row.get(f'vic{i}_representante_legal', 'Sin informacion'),
            'juicio_vic_representante_legal': row.get(f'juicio_vic{i}_representante_legal', 'Sin informacion'),
            'tiempo_relacion_victima_acusado': "sin informacion" if not es_primer_victima else row.get('tiempo_relacion_victima_acusado', "sin informacion"),
            
            # Campos de convivencia y otros
            'cambio_vic_tipo_hogar': row.get(f'cambio_vic{i}_tipo_hogar'),
            'cambio_vic_vive_con_conyuge': row.get(f'cambio_vic{i}_vive_con_conyuge', "sin informacion"),
            'cambio_vic_vive_con_exconyuge': row.get(f'cambio_vic{i}_vive_con_exconyuge', "sin informacion"),
            'cambio_vic_vive_con_pareja': row.get(f'cambio_vic{i}_vive_con_pareja', "sin informacion"),
            'cambio_vic_vive_con_expareja': row.get(f'cambio_vic{i}_vive_con_expareja', "sin informacion"),
            'cambio_vic_vive_con_conviviente_auc': row.get(f'cambio_vic{i}_vive_con_conviviente_auc', "sin informacion"),
            'cambio_vic_vive_con_exconviviente_auc': row.get(f'cambio_vic{i}_vive_con_exconviviente_auc', "sin informacion"),
            'cambio_vic_vive_con_conviviente_hecho': row.get(f'cambio_vic{i}_vive_con_conviviente_hecho', "sin informacion"),
            'cambio_vic_vive_con_exconviviente_hecho': row.get(f'cambio_vic{i}_vive_con_exconviviente_hecho', "sin informacion"),
            'cambio_vic_vive_con_papa': row.get(f'cambio_vic{i}_vive_con_papa', "sin informacion"),
            'cambio_vic_vive_con_mama': row.get(f'cambio_vic{i}_vive_con_mama', "sin informacion"),
            'cambio_vic_vive_con_padrastro': row.get(f'cambio_vic{i}_vive_con_padrastro', "sin informacion"),
            'cambio_vic_vive_con_madrastra': row.get(f'cambio_vic{i}_vive_con_madrastra', "sin informacion"),
            'cambio_vic_vive_con_1_hijo': row.get(f'cambio_vic{i}_vive_con_1_hijo', "sin informacion"),
            'cambio_vic_vive_con_hijos': row.get(f'cambio_vic{i}_vive_con_hijos', "sin informacion"),
            'cambio_vic_vive_con_1_hija': row.get(f'cambio_vic{i}_vive_con_1_hija', "sin informacion"),
            'cambio_vic_vive_con_hijas': row.get(f'cambio_vic{i}_vive_con_hijas', "sin informacion"),
            'cambio_vic_vive_con_hijastro': row.get(f'cambio_vic{i}_vive_con_hijastro', "sin informacion"),
            'cambio_vic_vive_con_hijastra': row.get(f'cambio_vic{i}_vive_con_hijastra', "sin informacion"),
            'cambio_vic_vive_con_1_hermano': row.get(f'cambio_vic{i}_vive_con_1_hermano', "sin informacion"),
            'cambio_vic_vive_con_hermanos': row.get(f'cambio_vic{i}_vive_con_hermanos', "sin informacion"),
            'cambio_vic_vive_con_1_hermana': row.get(f'cambio_vic{i}_vive_con_1_hermana', "sin informacion"),
            'cambio_vic_vive_con_hermanas': row.get(f'cambio_vic{i}_vive_con_hermanas', "sin informacion"),
            'cambio_vic_vive_con_hermanastro': row.get(f'cambio_vic{i}_vive_con_hermanastro', "sin informacion"),
            'cambio_vic_vive_con_hermanastra': row.get(f'cambio_vic{i}_vive_con_hermanastra', "sin informacion"),
            'cambio_vic_vive_con_tio': row.get(f'cambio_vic{i}_vive_con_tio', "sin informacion"),
            'cambio_vic_vive_con_tia': row.get(f'cambio_vic{i}_vive_con_tia', "sin informacion"),
            'cambio_vic_vive_con_suegro': row.get(f'cambio_vic{i}_vive_con_suegro', "sin informacion"),
            'cambio_vic_vive_con_suegra': row.get(f'cambio_vic{i}_vive_con_suegra', "sin informacion"),
            'cambio_vic_vive_con_abuelo': row.get(f'cambio_vic{i}_vive_con_abuelo', "sin informacion"),
            'cambio_vic_vive_con_abuela': row.get(f'cambio_vic{i}_vive_con_abuela', "sin informacion"),
            'cambio_vic_vive_con_nieto': row.get(f'cambio_vic{i}_vive_con_nieto', "sin informacion"),
            'cambio_vic_vive_con_nieta': row.get(f'cambio_vic{i}_vive_con_nieta', "sin informacion"),
            'cambio_vic_vive_con_otro': row.get(f'cambio_vic{i}_vive_con_otro', "sin informacion")
        }
        return victima_data

    def procesar_datos_denunciados(self, row, j, es_primer_denunciado, id_denunciado):
        # Procesa y devuelve los datos de un denunciante específico
        denounced_data = {
            'id_causa': row['id_causa'],
            'id_denunciado': id_denunciado,
            'den_edad': row.get(f'den{j}_edad', None),
            'den_sexo': row.get(f'den{j}_sexo',"sin informacion"),
            'den_nacionalidad': row.get(f'den{j}_nacionalidad',"sin informacion"),
            'den_nacionalidad_extranjera': row.get(f'den{j}_nacionalidad_extranjera',"sin informacion"),
            'den_profesion': row.get(f'den{j}_profesion',"sin informacion"),
            'den_estudios': row.get(f'den{j}_estudios',"sin informacion"),
            'den_caracter_lesion': row.get(f'den{j}_caracter_lesion',"sin informacion"),
            'den_descripcion_lesion': row.get(f'den{j}_descripcion_lesion',"sin informacion"),
            'den_estado_temperancia': row.get(f'den{j}_estado_temperancia',"sin informacion"),
            'den_estado_temperancia_otro': row.get(f'den{j}_estado_temperancia_otro', "sin informacion"),
            'den_descripcion_temperancia': row.get(f'den{j}_descripcion_temperancia',"sin informacion"),
            'den_comuna': row.get(f'den{j}_comuna', "sin informacion"),
            'den_estado_civil': row.get(f'den{j}_estado_civil','sin informacion'),
            'den_otros_antecedentes': row.get(f'den{j}_otros_antecedentes',"sin informacion"),

   
            # Antecedentes de los denunciados
            'antecedente_aborto': row.get(f'den{j}_ant_aborto',"sin informacion"),
            'antecedente_abandono': row.get(f'den{j}_ant_abandono',"sin informacion"),
            'antecedente_violacion': row.get(f'den{j}_ant_violacion',"sin informacion"),
            'antecedente_estupro': row.get(f'den{j}_ant_estupro',"sin informacion"),
            'antecedente_abuso_sexual': row.get(f'den{j}_ant_abuso_sexual',"sin informacion"),
            'antecedente_pornografia': row.get(f'den{j}_ant_pornografia',"sin informacion"),
            'antecedente_prostitucion_menores': row.get(f'den{j}_ant_prost_menores',"sin informacion"),
            'antecedente_incesto': row.get(f'den{j}_ant_incesto',"sin informacion"),
            'antecedente_parricidio': row.get(f'den{j}_ant_parricidio',"sin informacion"),
            'antecedente_femicidio': row.get(f'den{j}_ant_femicidio',"sin informacion"),
            'antecedente_homicidio': row.get(f'den{j}_ant_homicidio',"sin informacion"),
            'antecedente_infanticidio': row.get(f'den{j}_ant_infanticidio',"sin informacion"),
            'antecedente_lesiones_corporales': row.get(f'den{j}_ant_lesiones',"sin informacion"),
            'antecedente_maltrato': row.get(f'den{j}_ant_maltrato',"sin informacion"),
            'antecedente_trafico_migrantes': row.get(f'den{j}_ant_trafico_migrantes',"sin informacion"),
            'antecedente_trata_personas': row.get(f'den{j}_ant_trata_personas',"sin informacion"),
            'antecedente_robo': row.get(f'den{j}_ant_robo',"sin informacion"),
            'antecedente_hurto': row.get(f'den{j}_ant_hurto',"sin informacion"),
            'antecedente_estafa': row.get(f'den{j}_ant_estafa',"sin informacion"),
            'antecedente_incendio': row.get(f'den{j}_ant_incendio',"sin informacion"),
            'antecedente_trafico_estupefacientes': row.get(f'den{j}_ant_trafico_drogas',"sin informacion"),
            'antecedente_registro_vif': row.get(f'den{j}_ant_reg_especial_vif',"sin informacion"),
            #representante legal en preparatoria y jucui

            'den_representante_legal': row.get(f'den{j}_representante_legal','sin informacion'),
            'juicio_den_representante_legal': row.get(f'juicio_den{j}_representante_legal','sin informacion'),
            #riesgo vif
            'vif_parentesco_denunciado': "sin informacion" if not es_primer_denunciado else row.get('vif_parentesco_denunciado', "sin informacion"),
            'vif_parentesco_denunciado_otro': "sin informacion" if not es_primer_denunciado else row.get('vif_parentesco_denunciado_otro', "sin informacion"),
            'vif_hijos_menores': "sin informacion" if not es_primer_denunciado else row.get('vif_hijos_menores', "sin informacion"),
            'vif_hecho_golpes': "sin informacion" if not es_primer_denunciado else row.get('vif_hecho_golpes', "sin informacion"),
            'vif_hecho_lesiones': "sin informacion" if not es_primer_denunciado else row.get('vif_hecho_lesiones', "sin informacion"),
            'vif_hecho_amenaza_muerte': "sin informacion" if not es_primer_denunciado else row.get('vif_hecho_amenaza_muerte', "sin informacion"),
            'vif_hecho_uso_arma': "sin informacion" if not es_primer_denunciado else row.get('vif_hecho_uso_arma', "sin informacion"),
            'vif_hecho_violencia_sexual': "sin informacion" if not es_primer_denunciado else row.get('vif_hecho_violencia_sexual', "sin informacion"),
            'vif_denunciado_acceso_armas': "sin informacion" if not es_primer_denunciado else  row.get('vif_denunciado_acceso_armas', "sin informacion"),
            'vif_denunciado_consumo_sustancias': "sin informacion" if not es_primer_denunciado else  row.get('vif_denunciado_consumo_sustancias', "sin informacion"),
            'vif_denunciado_violencia_consumo': "sin informacion" if not es_primer_denunciado else row.get('vif_denunciado_violencia_consumo', "sin informacion"),
            'vif_denunciado_trastorno_psiquiatrico': "sin informacion" if not es_primer_denunciado else  row.get('vif_denunciado_trastorno_psiquiatrico', "sin informacion"),
            'vif_historia_golpes_previos': "sin informacion" if not es_primer_denunciado else row.get('vif_historia_golpes_previos', "sin informacion"),
            'vif_historia_aumento_golpes': "sin informacion" if not es_primer_denunciado else row.get('vif_historia_aumento_golpes', "sin informacion"),
            'vif_historia_amenaza_arma': "sin informacion" if not es_primer_denunciado else row.get('vif_historia_amenaza_arma', "sin informacion"),
            'vif_historia_amenaza_muerte_previa': "sin informacion" if not es_primer_denunciado else row.get('vif_historia_amenaza_muerte_previa', "sin informacion"),
            'vif_historia_violencia_menores': "sin informacion" if not es_primer_denunciado else  row.get('vif_historia_violencia_menores', "sin informacion"),
            'vif_historia_celos_violentos': "Sin informacion" if not es_primer_denunciado else row.get('vif_historia_celos_violentos', "sin informacion"),
            'vif_historia_separacion': "Sin informacion" if not es_primer_denunciado else row.get('vif_historia_separacion', "sin informacion"),
            'vif_historia_rechazo_separacion': "Sin informacion" if not es_primer_denunciado else row.get('vif_historia_rechazo_separacion', "sin informacion"),
            'vif_usted_discapacidad': "Sin informacion" if not es_primer_denunciado else row.get('vif_usted_discapacidad', "sin informacion"),
            'vif_usted_embarazo': "Sin informacion" if not es_primer_denunciado else  row.get('vif_usted_embarazo', "sin informacion"),
            'vif_usted_convivencia_denunciado': "Sin informacion" if not es_primer_denunciado else row.get('vif_usted_convivencia_denunciado', "sin informacion"),
            'vif_usted_dependencia_economica': "Sin informacion" if not es_primer_denunciado else row.get('vif_usted_dependencia_economica', "sin informacion"),
            'vif_reaccion_denuncia_agresion': "Sin informacion" if not es_primer_denunciado else row.get('vif_reaccion_denuncia_agresion', "sin informacion"),
            'vif_reaccion_denuncia_riesgo_fatal': "Sin informacion" if not es_primer_denunciado else  row.get('vif_reaccion_denuncia_riesgo_fatal', "sin informacion"),
            'vif_imputado_denuncias_vif': "Sin informacion" if not es_primer_denunciado else row.get('vif_imputado_denuncias_vif', "sin informacion"),
            'vif_imputado_condenas_vif': "Sin informacion" if not es_primer_denunciado else row.get('vif_imputado_condenas_vif', "sin informacion"),
            'vif_imputado_desacato_vif': "Sin informacion" if not es_primer_denunciado else row.get('vif_imputado_desacato_vif', "sin informacion"),
            'vif_imputado_delitos_pendientes': "Sin informacion" if not es_primer_denunciado else row.get('vif_imputado_delitos_pendientes', "sin informacion"),
            'vif_resultado_numero': "Sin informacion" if not es_primer_denunciado else row.get('vif_resultado_numero', "sin informacion"),
            'vif_resultado_nivel': "Sin informacion" if not es_primer_denunciado else row.get('vif_resultado_nivel', "sin informacion"),

        }
        return denounced_data

    def procesar_datos_denunciantes(self,row):
        # Procesa y devuelve los datos de un denunciante específico
        datos_denunciante = {
            'id_causa': row['id_causa'],
            'es_victima': row.get('dnt_es_victima', "sin informacion"),
            'es_persona_juridica': row.get('dnt_es_persona_juridica', "sin informacion"),
            'dtn_persona_juridica_cual': row.get('dnt_persona_juridica_cual', "sin informacion"),
            'dtn_edad': row.get('dnt_edad', "sin informacion"),
            'dtn_sexo': row.get('dnt_sexo', "sin informacion"),
            'dtn_nacionalidad': row.get('dnt_nacionalidad', "sin informacion"),
            'dtn_nacionalidad_Extranjera': row.get('dnt_nacionalidad_extranjera', "sin informacion"),
            'dtn_profesion': row.get('dnt_profesion', "sin informacion"),
            'dtn_estudios': row.get('dnt_estudios', "sin informacion"),
            'dtn_parentesco_Acusado': row.get('dnt_parentesco_acusado', "sin informacion"),
            'dtn_parentesco_Acusado_Otro': row.get('dnt_parentesco_acusado_otro', "sin informacion"),
            'dtn_caracter_Lesion': row.get('dnt_caracter_lesion', "sin informacion"),
            'dtn_descripcion_Lesion': row.get('dnt_descripcion_lesion', "sin informacion"),
            'dtn_estado_Temperancia': row.get('dnt_estado_temperancia', "sin informacion"),
            'dtn_estado_Temperancia_Otro': row.get('dnt_estado_temperancia_otro', "sin informacion"),
            'dtn_descripcion_Temperancia': row.get('dnt_descripcion_temperancia', "sin informacion"),
            'dtn_comuna': row.get('dnt_comuna', "sin informacion"),
            'dtn_estado_civil': row.get('denunciante_estado_civil', "sin informacion"),
            'dtn_representante_Legal': row.get('dnt_representante_legal', "sin informacion"),
            'dtn_juicio_representante_legal': row.get('juicio_dnt_representante_legal', "sin informacion"),
        }
        return datos_denunciante

    def procesar_datos_causa(self, row):
        # Procesa y devuelve los datos específicos de la causa
        datos_causa = {
            'id_causa': row['id_causa'],
            'digitador': row.get('digitador', "sin informacion"),
            'rol_rit': row.get('rol_rit', "sin informacion"),
            'fecha_ingreso': row.get('fecha_ingreso', "sin informacion"),
            'caratulado': row.get('caratulado', "sin informacion"),
            'procedimiento': row.get('procedimiento', "sin informacion"),
            'materia': row.get('materia', "sin informacion"),
            'estado_admin': row.get('estado_admin', "sin informacion"),
            'ubicacion': row.get('ubicacion', "sin informacion"),
            'cuaderno': row.get('cuaderno', "sin informacion"),
            'etapa': row.get('etapa', "sin informacion"),
            'estado_proceso': row.get('estado_proceso', "sin informacion"),
            'etapa_actual': row.get('etapa_actual', "sin informacion"),
            'etapa_actual_otro': row.get('etapa_actual_otro', "sin informacion"),
            'via_ingreso': row.get('via_ingreso', "sin informacion"),
            'causa_proteccion_abierta': row.get('causa_proteccion_abierta', "sin informacion"),
            'causa_penal_abierta': row.get('causa_penal_abierta', "sin informacion"),
            'composicion_hogar_convivencia_victimas': row.get('composicion_hogar_convivencia_victimas', "sin informacion")
        }
        return datos_causa

    def procesar_antedecentes_delito(self, row):
        # Procesa y devuelve los antecedentes específicos del delito
        antecedentes_delito = {
            'id_causa': row['id_causa'],
            'codigo_delito': row.get('codigo_delito', "sin informacion"),
            'fecha_delito': row.get('fecha_delito', "sin informacion"),
            'hora_delito': row.get('hora_delito', "sin informacion"),
            'lugar_ocurrencia': row.get('lugar_ocurrencia', "sin informacion"),
            'lugar_ocurrencia_otro': row.get('lugar_ocurrencia_otro', "sin informacion"),
            'comuna_delito': row.get('comuna_delito', "sin informacion"),
            'unidad_policial': row.get('unidad_policial', "sin informacion"),
            'cuadrante_delito': row.get('cuadrante_delito', "sin informacion"),

            # Su respectiva medida
            'rondas_domicilio': row.get('medidas_provisorias_rondas_domicilio', "sin informacion"),
            'telefono_cuadrante': row.get('medidas_provisorias_telefono_cuadrante', "sin informacion"),
            'prohibicion_acercamiento': row.get('medidas_provisorias_prohibicion_acercamiento', "sin informacion"),
            'restriccion_presencia_ofensor': row.get('medidas_provisorias_restriccion_presencia_ofensor', "sin informacion"),
            'entrega_efectos_personales': row.get('medidas_provisorias_entrega_efectos_personales', "sin informacion"),
            'fijacion_alimentos': row.get('medidas_provisorias_fijacion_alimentos', "sin informacion"),
            'regimen_cuidado_nna': row.get('medidas_provisorias_regimen_cuidado_nna', "sin informacion"),
            'prohibicion_actos_contratos': row.get('medidas_provisorias_prohibicion_actos_contratos', "sin informacion"),
            'prohibicion_armas': row.get('medidas_provisorias_prohibicion_armas', "sin informacion"),
            'reserva_identidad_denunciante': row.get('medidas_provisorias_reserva_identidad_denunciante', "sin informacion"),
            'proteccion_adultos_mayores_discapacidad': row.get('medidas_provisorias_proteccion_adultos_mayores_discapacidad', "sin informacion"),
            'asistencia_terapeutica': row.get('medidas_provisorias_asistencia_terapeutica', "sin informacion"),
            'presentacion_unidad_policial': row.get('medidas_provisorias_presentacion_unidad_policial', "sin informacion"),
            'otra_cautelar': row.get('medidas_provisorias_otra', "sin informacion"),
            #campos nuevos
            'plazo': row.get('medidas_cautelares_plazo', "sin informacion"),
            'interpone_recurso': row.get('medidas_cautelares_interpone_recurso', "sin informacion"),
            'demanda_reconvencional': row.get('demanda_reconvencional', "sin informacion"),

        }
        return antecedentes_delito

    def procesar_datos_audiencia_preparatoria(self, row):
        # Procesa y devuelve los datos específicos de la audiencia
        datos_audiencia = {
            'id_causa': row['id_causa'],
            'fecha_primera_citacion': row.get('fecha_primera_citacion', "sin informacion"),
            'audiencia_suspendida': row.get('audiencia_suspendida', "sin informacion"),
            'fecha_realizacion_audiencia': row.get('fecha_realizacion_audiencia', "sin informacion"),
            'pre_solicitan_informes_oficios': row.get('pre_solicitan_informes_oficios', "sin informacion"),
            'resolucion_audiencia': row.get('prep_aud_resolucion', "sin informacion"),
            'resolucion_salida_colaborativa': row.get('prep_aud_resolucion_salida_colaborativa', "sin informacion"),
            'prep_aud_resolucion_incompetencia_tipo': row.get('prep_aud_resolucion_incompetencia_tipo', "sin informacion"),
            #campos nuevos
            'pre_solicitan_informes_oficios': row.get('pre_solicitan_informes_oficios', "sin informacion"),
            'informes_entregados':row.get('prep_aud_informes_entregados', "sin informacion"),
            'informes_entregados_cuales': row.get('prep_aud_informes_entregados_cuales', "sin informacion"),
            'informes_pendientes': row.get('prep_aud_informes_pendientes', "sin informacion"),
            'demora_entrega_informes': row.get('prep_aud_demora_entrega_informes', "sin informacion"),
            'pericia_solicitada': row.get('prep_aud_pericia_solicitada', "sin informacion"),
            'pericia_cual': row.get('prep_aud_pericia_cual', "sin informacion"),
            'pericia_solicitante': row.get('prep_aud_pericia_solicitante', "sin informacion"),
            #---
            # Con su respectivas medidas
            'rondas_domicilio': row.get('medidas_rondas_domicilio', "sin informacion"),
            'telefono_cuadrante': row.get('medidas_telefono_cuadrante', "sin informacion"),
            'prohibicion_acercamiento': row.get('medidas_prohibicion_acercamiento_victima', "sin informacion"),
            'restriccion_presencia_ofensor': row.get('medidas_restriccion_presencia_ofensor', "sin informacion"),
            'entrega_efectos_personales': row.get('medidas_entrega_efectos_personales', "sin informacion"),
            'fijacion_alimentos': row.get('medidas_fijar_alimentos_provisorios', "sin informacion"),
            'regimen_cuidado_nna': row.get('medidas_regimen_cuidado_nna', "sin informacion"),
            'prohibicion_actos_contratos': row.get('medidas_prohibicion_actos_contratos', "sin informacion"),
            'prohibicion_armas': row.get('medidas_prohibicion_porte_armas', "sin informacion"),
            'reserva_identidad_denunciante': row.get('medidas_reserva_identidad_denunciante', "sin informacion"),
            'proteccion_adultos_mayores_discapacidad': row.get('medidas_proteccion_adultos_mayores_discapacidad', "sin informacion"),
            'asistencia_terapeutica': row.get('medidas_asistencia_terapeutica', "sin informacion"),
            'presentacion_unidad_policial': row.get('medidas_presentacion_unidad_policial', "sin informacion"),
            'otra_cautelar': row.get('medidas_otra_cautelar', "sin informacion"),
        }
        return datos_audiencia

    def procesar_datos_juicio_completo(self, row):
        # Procesa y devuelve los datos completos del juicio
        datos_juicio_completo = {
            'id_causa': row['id_causa'],
            'fecha_primera_citacion_juicio': row.get('fecha_primera_citacion_juicio', "sin informacion"),
            'cambio_composicion_hogar_juicio': row.get('cambio_composicion_hogar_juicio', "sin informacion"),
            'fecha_realizacion': row.get('juicio_fecha_realizacion', "sin informacion"),
            'juicio_audiencia_suspendida': row.get('juicio_audiencia_suspendida', "sin informacion"),
            'juicio_dnt_representante_legal': row.get('juicio_dnt_representante_legal', "sin informacion"),
            'juicio_resolucion': row.get('juicio_resolucion', "sin informacion"),
            'juicio_sentencia_cual': row.get('juicio_sentencia_cual', "sin informacion"),
            'juicio_salida_colaborativa_cual': row.get('juicio_salida_colaborativa_cual', "sin informacion"),
            'juicio_carabineros_cese_medidas': row.get('juicio_carabineros_cese_medidas', "sin informacion"),
            'sentencia_recurso_procesal': row.get('sentencia_recurso_procesal', "sin informacion"),
            'sentencia_recurso_procesal_otro': row.get('sentencia_recurso_procesal_otro', "sin informacion"),
            'causa_cumplimiento_abierta': row.get('causa_cumplimiento_abierta', "sin informacion"),
            'causa_cumplimiento_rol_rit': row.get('causa_cumplimiento_rol_rit', 'sin informacion'),
            #campos nuevos
            'solicitan_informes_oficios': row.get('juicio_solicitan_informes_oficios','sin informacion'),
            'juicio_informes_solicitados_a_quien': row.get('juicio_informes_solicitados_a_quien','sin informacion'),
            'informes_entregados': row.get('juicio_informes_entregados','sin informacion'),
            'informes_entregados_cuales': row.get('juicio_informes_entregados_cuales','sin informacion'),
            'informes_pendientes': row.get('juicio_informes_pendientes','sin informacion'),
            'demora_informes': row.get('juicio_demora_informes','sin informacion'),
            'suspension_condicional': row.get('juicio_suspension_condicional','sin informacion'),
            'otro_acuerdo_cual': row.get('juicio_otro_acuerdo_cual','sin informacion'),
            'pericia_solicitada': row.get('juicio_pericia_solicitada', 'sin informacion'),
            'pericia_cual': row.get('juicio_pericia_cual','sin informacion'),
            'pericia_solicitante': row.get('juicio_pericia_solicitante','sin informacion'),
            'pericia_resultado': row.get('juicio_pericia_resultado','sin informacion'),
            'pericia_evaluado': row.get('juicio_pericia_evaluado', 'sin informacion'),
            'medidas_cautelares': row.get('juicio_medidas_cautelares','sin informacion'),
            'medidas_recurso':row.get('juicio_medidas_recurso','juicio_medidas_recurso'),
            #---

            'rondas_domicilio': row.get('juicio_medidas_rondas_domicilio', "sin informacion"),
            'telefono_cuadrante': row.get('juicio_medidas_telefono_cuadrante', "sin informacion"),
            'prohibicion_acercamiento': row.get('juicio_medidas_prohibicion_acercamiento_victima', "sin informacion"),
            'restriccion_presencia_ofensor': row.get('juicio_medidas_restriccion_presencia_ofensor', "sin informacion"),
            'entrega_efectos_personales': row.get('juicio_medidas_entrega_efectos_personales', "sin informacion"),
            'fijacion_alimentos': row.get('juicio_medidas_fijar_alimentos_provisorios', "sin informacion"),
            'regimen_cuidado_nna': row.get('juicio_medidas_regimen_cuidado_nna', "sin informacion"),
            'prohibicion_actos_contratos': row.get('juicio_medidas_prohibicion_actos_contratos', "sin informacion"),
            'prohibicion_armas': row.get('juicio_medidas_prohibicion_porte_armas', "sin informacion"),
            'reserva_identidad_denunciante': row.get('juicio_medidas_reserva_identidad_denunciante', "sin informacion"),
            'proteccion_adultos_mayores_discapacidad': row.get('juicio_medidas_proteccion_adultos_mayores_discapacidad', "sin informacion"),
            'asistencia_terapeutica': row.get('juicio_medidas_asistencia_terapeutica', "sin informacion"),
            'presentacion_unidad_policial': row.get('juicio_medidas_presentacion_unidad_policial', "sin informacion"),
            'otra_cautelar': row.get('juicio_medidas_otra_cautelar', "sin informacion"),
        }
        return datos_juicio_completo

    def combinar_y_procesar(self, df_victima, df_denunciado, df_denunciante):
        # Crear un diccionario de víctimas, denunciados y denunciantes agrupados por id_causa
        victimas_por_causa = df_victima.groupby('id_causa').apply(
            lambda x: x[['id_victima', 'vic_representante_legal',
                         'juicio_vic_representante_legal']].to_dict('records')
        ).to_dict()
        denunciados_por_causa = df_denunciado.groupby('id_causa').apply(
            lambda x: x[['id_denunciado', 'den_representante_legal',
                         'juicio_den_representante_legal']].to_dict('records')
        ).to_dict()
        denunciantes_por_causa = df_denunciante.groupby('id_causa').apply(
            lambda x: x[['tipo_relacion', 'dtn_representante_Legal',
                         'dtn_juicio_representante_legal']].to_dict('records')
        ).to_dict()
        combined_rows = []
        for id_causa in set(df_victima['id_causa']).union(df_denunciado['id_causa']).union(df_denunciante['id_causa']):
            victimas = victimas_por_causa.get(id_causa, [])
            denunciados = denunciados_por_causa.get(id_causa, [])
            denunciantes = denunciantes_por_causa.get(id_causa, [])

            # Extender listas para igualar la longitud y combinarlas
            max_length = max(len(victimas), len(
                denunciados), len(denunciantes))
            victimas.extend([{}] * (max_length - len(victimas)))
            denunciados.extend([{}] * (max_length - len(denunciados)))
            denunciantes.extend([{}] * (max_length - len(denunciantes)))

            for i in range(max_length):
                combined_row = {'id_causa': id_causa}
                combined_row.update(victimas[i] if i < len(victimas) else {})
                combined_row.update(
                    denunciados[i] if i < len(denunciados) else {})
                combined_row.update(
                    denunciantes[i] if i < len(denunciantes) else {})
                combined_rows.append(combined_row)

        # Crear DataFrame combinado
        df_combinado = pd.DataFrame(combined_rows)

        # Procesar id_denunciado e tipo_relacion
        df_combinado['id_denunciado'] = df_combinado['id_denunciado'].apply(
            lambda x: int(x) if pd.notna(x) and not isinstance(
                x, str) else None
        )
        df_combinado['tipo_relacion'] = df_combinado['tipo_relacion'].apply(
            lambda x: int(x) if pd.notna(x) and not isinstance(
                x, str) else None
        )

        # Reemplazar NaN con 'sin información'
        df_combinado.replace({np.nan: None}, inplace=True)

        return df_combinado

    def transformar_dataframe(self, df, mapeo_preguntas, id_column_name=None, columns_to_add=None):
        if columns_to_add is None:
            columns_to_add = []

        for medida in mapeo_preguntas.keys():
            if medida not in df.columns:
                return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

        # Si todas las columnas requeridas están presentes, procedemos con el mapeo
        if all(column in df.columns for column in mapeo_preguntas.keys()):
            # Crear listas para almacenar los datos transformados
            case_ids = []
            ids = [] if id_column_name else None
            tipos_medida = []
            respuestas = []
            # Incluimos las nuevas columnas
            additional_columns_data = {column: [] for column in columns_to_add}

            # Rellenar las listas con los datos normalizados
            for index, row in df.iterrows():
                for medida, pregunta in mapeo_preguntas.items():
                    case_ids.append(row['id_causa'])
                    if id_column_name:
                        ids.append(row[id_column_name])
                    tipos_medida.append(pregunta)
                    respuestas.append(row[medida])

                    # Agregamos los datos de las nuevas columnas
                    for column in columns_to_add:
                        additional_columns_data[column].append(row[column])

            # Crear un nuevo DataFrame con las listas
            data_dict = {
                'id_causa': case_ids,
                'Tipo': tipos_medida,
                'Respuesta': respuestas
            }
            if id_column_name:
                data_dict[id_column_name] = ids

            # Agregamos los datos de las nuevas columnas al diccionario
            data_dict.update(additional_columns_data)

            df_mapeado = pd.DataFrame(data_dict)

            return df_mapeado

        else:
            print("Algunas columnas requeridas no están presentes en el DataFrame.")
            return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

    # Función para eliminar tildes y reemplazar 'ñ' por 'anio'
    def eliminar_tildes(self, x):
        if isinstance(x, str):
            x = x.replace('ñ', 'ny')
            return ''.join((c for c in unicodedata.normalize('NFD', x) if unicodedata.category(c) != 'Mn'))
        return x

    # Función para convertir texto a minúsculas
    def a_minusculas(self, x):
        if isinstance(x, str):
            return x.lower()
        return x

    # Función para eliminar espacios al inicio y al final
    def quitar_espacios(self, x):
        return x.strip() if isinstance(x, str) else x

    # Función para eliminar espacios adicionales en medio
    def quitar_espacios_extra(self, x):
        return re.sub(r'\s{2,}', ' ', x) if isinstance(x, str) else x

    # Función para procesar la columna 'edad'
    def procesar_edad(self, edad):
        # Eliminar texto no numérico conservando el punto decimal para números flotantes
        edad_limpia = re.sub(r'[^\d.]', '', str(edad))
        try:
            # Convertir a flotante y luego a entero
            return int(float(edad_limpia))
        except ValueError:
            # Si la conversión falla, devolver 0
            return 0
        

    def combinar_dataframes_por_id_causa(lista_dfs, columna_id='id_causa'):
        combined_rows = []
        # Obtener todos los IDs únicos de las causas
        ids_unicos = set()
        for df in lista_dfs:
            ids_unicos.update(df[columna_id].unique())

        # Combinar los DataFrames por id_causa
        for id_causa in ids_unicos:
            # Lista para guardar los registros de cada DataFrame para el id_causa actual
            registros_por_id = [df[df[columna_id] == id_causa].to_dict(
                'records') for df in lista_dfs]

            # Calcular la cantidad máxima de filas a generar por id_causa
            max_length = max(len(registros) for registros in registros_por_id)

            # Extender las listas de registros para tener la misma longitud
            for registros in registros_por_id:
                registros.extend([{}] * (max_length - len(registros)))

            # Combinar las filas extendidas
            for i in range(max_length):
                combined_row = {columna_id: id_causa}
                for registros in registros_por_id:
                    combined_row.update(registros[i])
                combined_rows.append(combined_row)

        # Crear y retornar el DataFrame combinado
        df_final_combinado = pd.DataFrame(combined_rows)
        df_final_combinado.replace({pd.NA: ''}, inplace=True)
        return df_final_combinado
    
    async def process_delete_bd(self, event=None):
        documents_folder = os.path.join(os.path.expanduser('~'), 'Documents')

        # Construir la ruta completa hacia la base de datos
        database_path = os.path.join(documents_folder, 'LIACDD', 'LIACDD.db')

        # Verificar si la base de datos existe
        if os.path.exists(database_path):
            try:
                # Eliminar la base de datos
                os.remove(database_path)
                await self.mostrar_mensaje(self.page, 'Base de datos eliminada con éxito.')
                await self.db.initialize_database()
                # Guarda el tiempo de finalización
            except Exception as e:
                await self.mostrar_mensaje(self.page, 'Error al eliminar la base de datos.', 'error')
        else:
            await self.mostrar_mensaje(self.page, 'La base de datos no existe.', 'error')

    async def prompt_delete_database(self, e):
        # Instancia y abre el diálogo de confirmación
        
        confirm_dialog = ConfirmationDialog(
            self.page, 
            "Confirmación", 
            "¿Estás seguro de que quieres eliminar la base de datos?", 
            self.process_delete_bd
        )
        await confirm_dialog.open()