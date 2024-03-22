import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
import flet as ft
import asyncio 
from datetime import datetime
from widgets.dialog import InfoTreeModels

class ModelAnalysisWidget(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.df = None  # Agregar esta línea
        self.columna_objetivo = None 
        self.file_picker = ft.FilePicker(on_result=self.pick_files_save_result)
        self.file_path_save = None
        self.color_1 = ft.colors.DEEP_PURPLE_100
        self.color_2= ft.colors.DEEP_PURPLE_300
        self.color_3 = ft.colors.DEEP_PURPLE_700
        self.directory_selected_event = asyncio.Event()
    def build(self):

        divider = ft.Container(content=ft.Divider(height=2, color="white"),width=1500)
        self.page.overlay.append(self.file_picker)


        info_dialog = InfoTreeModels(
            self.page,  # Esto sería una referencia a la instancia actual de la página donde se mostrará el diálogo.
            "Manual de usuario - Arboles de decisión",
        )
        async def open_info_dialog(e):
            self.page.dialog = info_dialog.dialog
            info_dialog.dialog.open = True
            await self.page.update_async()
            
        self.dialogo_manual = ft.IconButton(icon= ft.icons.INFO_OUTLINE ,icon_color="green400", on_click=open_info_dialog)


        self.save_trees_button = ft.ElevatedButton(
            text="Seleccione una carpeta para Guardar Árboles de Decisiones",
            on_click=self.guardar_arboles_decision
        )
        
        self.pr = ft.ProgressRing(width=30, height=30, stroke_width = 5, visible  = False)


        self.dropdown_columnas = ft.Dropdown(
            options=[],
            on_change=self.columna_seleccionada
        )

        self.analyze_button = ft.ElevatedButton(
            text="Iniciar análisis",
            on_click=self.iniciar_analisis
        )


        # Parámetros del modelo Decision Tree
        self.max_depth_slider = ft.Slider(
            inactive_color= self.color_2,
            active_color=self.color_3,
            min=1, max=20, value=10, divisions=19,
            label="{value}"
        )
        self.min_samples_split_slider = ft.Slider(
            inactive_color=self.color_2,
            active_color=self.color_3,
            min=2, max=20, value=2, divisions=18,
            label="{value}"
        )
        self.criterion_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("entropy"),
                ft.dropdown.Option("gini")
            ],
            value="entropy",
            label="Criterio",
            width=120
        )

        # Parámetros del modelo Random Forest
        self.n_estimators_slider = ft.Slider(
            inactive_color=self.color_2,
            active_color=self.color_3,
            min=100, max=200, value=150, divisions=10,
            label="{value}"
        )
        self.max_features_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("sqrt"),
                ft.dropdown.Option("log2")
            ],
            value="sqrt",
            label="Máx. Características",width=150
        )
        # Nuevos controles para parámetros adicionales
        self.min_samples_leaf_slider = ft.Slider(
            inactive_color=self.color_2,
            active_color=self.color_3,
            min=1, max=10, value=3, divisions=9,
            label="{value}"
        )
        self.splitter_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("best"),
                ft.dropdown.Option("random")
            ],
            value="random",
            label="Divisor",width=120
        )

        # Crear títulos para los sliders
        titulo_arbol_decision = ft.Text("Configuración del Análisis por Árbol de Decisión", size=20, color=self.color_1,weight=ft.FontWeight.BOLD)
        max_depth_title = ft.Text("Profundidad Máxima:", size=14)
        min_samples_split_title = ft.Text("Mínimo de Muestras para Dividir:", size=14)
        min_samples_leaf_title = ft.Text("Mínimo de Muestras en Hoja:", size=14)
        n_estimators_title = ft.Text("Número de Estimadores:", size=14)

        control_row = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                            titulo_arbol_decision,
                            max_depth_title, self.max_depth_slider,
                            min_samples_split_title, self.min_samples_split_slider,
                            min_samples_leaf_title, self.min_samples_leaf_slider,
                            n_estimators_title, self.n_estimators_slider,
                        
                        ft.Row(controls=[
                            self.criterion_dropdown, self.splitter_dropdown, self.max_features_dropdown
                        ])
                    ],
                    spacing=10
                ),
                width=500, padding=20
            ), elevation=15
        )


        # Parámetros del modelo Random Forest
        self.n_estimators_slider_rf = ft.Slider(
            inactive_color=self.color_2,
            active_color=self.color_3,
            min=10, max=300, value=150, divisions=29, label="{value}"
        )

        self.max_depth_slider_rf = ft.Slider(
            inactive_color=self.color_2,
            active_color=self.color_3,
            min=1, max=20, value=20, divisions=19, label="{value}"
        )
        self.min_samples_split_slider_rf = ft.Slider(
            inactive_color=self.color_2,
            active_color=self.color_3,
            min=2, max=20, value=5, divisions=18, label="{value}"
        )
        self.min_samples_leaf_slider_rf = ft.Slider(
            inactive_color=self.color_2,
            active_color=self.color_3,
            min=1, max=10, value=1, divisions=9, label="{value}"
        )

        # Dropdown para el criterio de división del árbol
        self.criterion_dropdown_rf = ft.Dropdown(
            label="Criterio de División",
            options=[
                ft.dropdown.Option("gini"),
                ft.dropdown.Option("entropy")
            ],
            value="gini",
            width=120
        )

        # Dropdown para la selección de características máximas
        self.max_features_dropdown_rf = ft.Dropdown(
            label="Características Máximas",
            options=[
                ft.dropdown.Option("sqrt"),
                ft.dropdown.Option("log2")
            ],
            value="log2",
            width=120
        )

        # Dropdown para el peso de las clases
        self.class_weight_dropdown_rf = ft.Dropdown(
            label="Peso de las Clases",
            options=[
                ft.dropdown.Option("balanced",),
                ft.dropdown.Option("balanced_subsample")
            ],
            value="balanced",
            width=200
        )
       
        # Títulos para los controles de Random Forest
        titulo_arbol_rf = ft.Text("Configuración del Análisis por Random Forest", size=20, color=self.color_1,weight=ft.FontWeight.BOLD)
        n_estimators_title_rf = ft.Text("Número de Estimadores:", size=14)
        max_depth_title_rf = ft.Text("Profundidad Máxima:", size=14)
        min_samples_split_title_rf = ft.Text("Mínimo de Muestras para Dividir:", size=14)
        min_samples_leaf_title_rf = ft.Text("Mínimo de Muestras en Hoja:", size=14)

        # Agregar los títulos y los controles al layout
        control_row_rf = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        titulo_arbol_rf,
                        n_estimators_title_rf, self.n_estimators_slider_rf,
                        max_depth_title_rf, self.max_depth_slider_rf,
                        min_samples_split_title_rf, self.min_samples_split_slider_rf,
                        min_samples_leaf_title_rf, self.min_samples_leaf_slider,
                        ft.Row(controls=[
                            self.max_features_dropdown_rf,
                            self.criterion_dropdown_rf,
                            self.class_weight_dropdown_rf
                        ]),
                    ],
                    spacing=10
                ),
                width=500, padding=20
            ), elevation=15
        ) 
        # Título para la sección de análisis
        titulo_analisis = ft.Text("Seleccionar categoría para análisis:", size=16)

        # Contenedor para el título y el Dropdown
        seleccionar_analisis_container = ft.Row(
            controls=[titulo_analisis, self.dropdown_columnas],

            spacing=10
        )

        # Card para el título y el Dropdown
        self.seleccionar_categoria_card = ft.Card(
            content=ft.Container(
            content=seleccionar_analisis_container,
            padding=20

        ),  elevation=15,
            width=600,)

        # Contenedor para los botones
        botones_container = ft.Row(
                controls=[self.analyze_button, self.pr, self.save_trees_button , self.dialogo_manual],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15
            )


        # Card que envuelve el contenedor de botones
        botones_card = ft.Card(
            ft.Container(
            content=botones_container,
            padding=20
            
        ),elevation=15,)

        # Contenedor principal que incluye el Card
        botones_container_principal = ft.Row(
            controls=[botones_card],
            alignment=ft.MainAxisAlignment.CENTER,
         
        )

        # Contenedor para control_row y control_row_rf
        self.parameters_and_analysis_container = ft.Row(
            controls=[
                control_row,  # Contenedor de parámetros de Árbol de Decisión
                control_row_rf,  # Contenedor de parámetros de Random Forest
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,  # Espacio uniforme entre los elementos

        )

        self.text_field_1 = ft.TextField(
            multiline=True, disabled=True, value="", color=ft.colors.WHITE,
        )
        self.text_field_2 = ft.TextField(
            multiline=True, disabled=True, value="", color=ft.colors.WHITE, 
        )
        # Títulos que se actualizarán dinámicamente
        self.titulo_info_1 = ft.Text(
            value="Clasificación de Características Árbol de Decisión para: ",  # Valor inicial
            size=20,
            color=self.color_1,
            weight=ft.FontWeight.BOLD
        )

        self.titulo_info_2 = ft.Text(
            value="Clasificación de Características Random Forest para: ",  # Valor inicial
            size=20,
            color=self.color_1,
            weight=ft.FontWeight.BOLD
        )

        # Agregar los títulos y los campos de texto al layout con una pequeña separación
        self.text_1 = ft.Card(
            content= ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    self.titulo_info_1,
                    self.text_field_1
                ],
                spacing=5  
            ),
            
        ),elevation=15, width=500, margin=10)

        self.text_2 = ft.Card(
            content= ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    self.titulo_info_2,
                    self.text_field_2
                ],
                spacing=5  # Espacio entre los controles
            ),
          
        ),
          elevation=15, width=500, margin=10
        )

        self.container_info = ft.Container(
            content=ft.Row(
                controls=[self.text_1, self.text_2],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            ),
            alignment=ft.alignment.top_left,
        )
        # Contenedor principal que incluirá todos los controles en una columna
        self.main_container = ft.Container(
            content=ft.Column(
                controls=[
                    divider,
                    self.seleccionar_categoria_card,  # Contenedor de selección de categoría
                    botones_container_principal,               # Contenedor de botones
                    self.parameters_and_analysis_container,  # Fila con conjuntos de parámetros
                    self.container_info  # Información adicional o resultados del análisis
                ],
                expand=True
            ),
            visible=False
        )

        return self.main_container

    async def columna_seleccionada(self, e):
        self.columna_objetivo = e.control.value

    async def iniciar_analisis(self, e):
        if self.columna_objetivo and self.df is not None:
            
            self.pr.visible = True  # Mostrar el ProgressRing
            await self.pr.update_async()

            # Llamar a analyze_data y esperar a que termine su ejecución
            await self.analyze_data(self.df, self.columna_objetivo)
            self.titulo_info_1.value = f"Clasificación de Características Árbol de Decisión para: {self.columna_objetivo}"
            self.titulo_info_2.value = f"Clasificación de Características Random Forest para: {self.columna_objetivo}"
            await self.titulo_info_1.update_async()
            await self.titulo_info_2.update_async()
            # Esperar un breve momento antes de ocultar el ProgressRing para que el usuario note que algo está sucediendo
            await asyncio.sleep(1)

            self.pr.visible = False  # Ocultar el ProgressRing
            await self.pr.update_async()

    async def set_dataframe(self, df):
        self.df = df
        columnas = df.columns.tolist()
        self.dropdown_columnas.options = [ft.dropdown.Option(columna) for columna in columnas]
        if columnas:
            self.dropdown_columnas.value = columnas[0]
            self.columna_objetivo = columnas[0]  # Establecer un valor inicial
        await self.dropdown_columnas.update_async()


    async def analyze_data(self, df_combinado, columna_objetivo):
        exclusiones = ["no aplica", "sin informacion"]
        if columna_objetivo not in df_combinado.columns:
            print(f"La columna {columna_objetivo} no se encuentra en el DataFrame.")
            return

        # Reemplazar NaN con "no aplica"
        df_combinado = df_combinado.fillna("no aplica")

        # Generar variables dummy para el conjunto de datos
        X = pd.get_dummies(df_combinado.drop(columna_objetivo, axis=1))

        # Eliminar columnas de variables dummy para los valores en exclusiones
        X = X.loc[:, ~X.columns.isin([f"{col}_{ex}" for ex in exclusiones for col in df_combinado.columns])]

        y = df_combinado[columna_objetivo]
        self.feature_names = X.columns.tolist() 

        self.best_model = DecisionTreeClassifier(
            criterion=self.criterion_dropdown.value,
            max_depth=int(self.max_depth_slider.value),
            min_samples_split=int(self.min_samples_split_slider.value),
            min_samples_leaf=int(self.min_samples_leaf_slider.value),
            max_features=self.max_features_dropdown.value,
            splitter='random',
            random_state=42
        )
        self.best_model.fit(X, y)

        
        feature_importances_text = ""
        importances = self.best_model.feature_importances_
        indices = (-importances).argsort()
        num_caracteristicas = 0
        for i in indices:
            feature_name = self.feature_names[i]
            if not any(exclusion in feature_name.lower() for exclusion in exclusiones):
                feature_importances_text += f"{num_caracteristicas + 1}. {feature_name} ({importances[i]:.4f})\n"
                num_caracteristicas += 1
                if num_caracteristicas >= 10:
                    break

        self.best_rf_model = RandomForestClassifier(
            n_estimators=int(self.n_estimators_slider_rf.value),
            criterion=self.criterion_dropdown_rf.value,
            max_depth=int(self.max_depth_slider_rf.value),
            min_samples_split=int(self.min_samples_split_slider_rf.value),
            min_samples_leaf=int(self.min_samples_leaf_slider_rf.value),
            max_features=self.max_features_dropdown_rf.value,
            class_weight=self.class_weight_dropdown_rf.value,
            random_state=42
        )
        self.best_rf_model.fit(X, y)
       
        texto_importancias_caracteristicas_rf = ""
        importancias_rf = self.best_rf_model.feature_importances_
        indices_rf = (-importancias_rf).argsort()
        num_caracteristicas = 0
        for i in indices_rf:
            feature_name_rf = self.feature_names[i]
            if not any(exclusion in feature_name_rf.lower() for exclusion in exclusiones):
                texto_importancias_caracteristicas_rf += f"{num_caracteristicas + 1}. {feature_name_rf} ({importancias_rf[i]:.4f})\n"
                num_caracteristicas += 1
                if num_caracteristicas >= 10:
                    break

        # Actualizar los campos de texto en la interfaz de usuario
        self.text_field_1.value = feature_importances_text
        self.text_field_2.value = texto_importancias_caracteristicas_rf

        await self.text_field_1.update_async()
        await self.text_field_2.update_async()

        self.main_container.visible = True
        await self.main_container.update_async()


    async def guardar_arboles_decision(self, e):
        # Abre el FilePicker para que el usuario seleccione una carpeta
        await self.open_get_file(e)
        await self.directory_selected_event.wait()
        self.directory_selected_event.clear()

        # Usar self.file_path_save para obtener la ruta del directorio seleccionado
        folder_path = self.file_path_save
        if self.df is None or folder_path is None:
            print("No hay un modelo para guardar o no se ha seleccionado una carpeta.")
            return

        if hasattr(self, 'feature_names') and self.feature_names:
            # Función para generar un nombre de archivo con un sufijo numérico incremental
            def generate_filename(base_path, suffix, extension):
                # Obtener la fecha y hora actuales
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Crear el nombre del archivo con la fecha y hora
                new_path = f"{base_path}_{current_time}{suffix}{extension}"
                return new_path


            base_filename = os.path.join(folder_path, "decision_tree")
            extension = ".svg"
            filename_decision_tree = generate_filename(base_filename, "", extension)
            self.save_decision_tree(self.best_model, self.feature_names, filename_decision_tree)

            print(f"Árbol de decisión guardado en {filename_decision_tree}")
        else:
            print("Los nombres de las características no están disponibles.")



    async def pick_files_save_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.file_path_save = e.path  # Configurar la ruta de guardado
            self.directory_selected_event.set()  # Indicar que se ha seleccionado un directorio

    async def open_get_file(self, e):
        await self.file_picker.get_directory_path_async()

    def save_decision_tree(self, model, feature_names, filename):
        # Calcular el tamaño de la figura en función del árbol
        num_leaf_nodes = model.get_n_leaves()
        depth = model.get_depth()
        figsize_width = max(20, num_leaf_nodes * 3)  # Ajusta estos valores según tus necesidades
        figsize_height = max(10, depth * 3)

        plt.figure(figsize=(figsize_width, figsize_height))
        plot_tree(model, filled=True, feature_names=feature_names, fontsize=10)
        plt.savefig(filename, format='svg', bbox_inches='tight')  # Guardar en formato SVG
        plt.close()

