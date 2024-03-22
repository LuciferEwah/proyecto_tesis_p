import flet as ft
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import asyncio 
from widgets.dialog import AssociationRulesDialog

class ReglasAsociacion(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.df = pd.DataFrame()
        self.terms_to_exclude = {"no aplica", "sin informacion"}
        self.data_table = ft.DataTable(columns=[], rows=[])
        self.min_support = 0.10 #TODO: Cambiar a valores mas bajo para el final, esto es solo para la presentación
        self.max_support = 0.3
        self.min_confidence = 0.7
        self.sort_criterion = "support"  
        self.color_title = ft.colors.DEEP_PURPLE_300
        self.color_general = ft.colors.DEEP_PURPLE_500
        self.weight_title = ft.FontWeight.BOLD
        self.calculated_rules = None  
        self.active_chips = set()
        self.chips = []
        self.chip_values = ["vic_estudios", "vic_sexo", "vic_parentesco_acusado_otro", "vic_nacionalidad_extranjera", 
                    "vic_profesion_oficio", "vic_nacionalidad", "vic_estado_civil", "vic_descripcion_lesion", 
                    "vic_estado_temperancia", "vic_descripcion_temperancia", "vic_año_ingreso", 
                    "vic_estado_temperancia_otro", "vic_grupo_edad", "vic_caracter_lesion", 
                    "vic_parentesco_acusado", "vic_comuna"]


    async def on_support_change(self, e):
        self.min_support = float(e.control.start_value) / 100  # Convertir a porcentaje
        self.max_support = float(e.control.end_value) / 100    # Convertir a porcentaje
        

    async def on_confidence_change(self, e):
        self.min_confidence = float(e.control.value) / 100  # Convertir a porcentaje
        

    async def on_analyze_clicked(self, e):
        self.progress_ring.visible = True
        await self.progress_ring.update_async()
        await asyncio.sleep(1)
        await self.apply_association_rules()
        self.progress_ring.visible = False
        await asyncio.sleep(1)
        await self.progress_ring.update_async()

    async def on_chip_selected(self, e):
        chip_value = e.control.data
        if e.control.selected:
            self.active_chips.add(chip_value)
        else:
            self.active_chips.discard(chip_value)
        if self.calculated_rules is not None:
            filtered_rules = self.filter_dataframe_based_on_fields(self.active_chips)
            ordered_rules = self.ordenar_reglas(filtered_rules)
            await self.actualizar_interfaz_usuario(ordered_rules)

    def filter_dataframe_based_on_fields(self, selected_fields):
        if not selected_fields:
            return pd.DataFrame(columns=self.calculated_rules.columns)

        def filter_rules(row):
            # Convertir conjuntos de frozenset a set para poder iterar
            antecedents = set(row['antecedents'])
            consequents = set(row['consequents'])
            # Verificar si algún antecedente o consecuente comienza con alguna de las categorías seleccionadas
            return any(field.startswith(category) for field in antecedents.union(consequents) for category in selected_fields)

        # Filtrar las reglas
        filtered_rules = self.calculated_rules[self.calculated_rules.apply(filter_rules, axis=1)]
        return filtered_rules

    def build(self):
        info_dialog = AssociationRulesDialog(
            self.page,  
        )
        async def open_info_dialog(e):
            self.page.dialog = info_dialog.dialog
            info_dialog.dialog.open = True
            await self.page.update_async()
            
        self.dialogo_manual = ft.IconButton(icon= ft.icons.INFO_OUTLINE ,icon_color="green400", on_click=open_info_dialog)

        self.sort_criterion_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("support", "Soporte"),
                ft.dropdown.Option("confidence", "Confianza")
            ],
            value="support",
            on_change=self.on_sort_criterion_change,
            width=150
        )
        sort_criterion_title = ft.Text("Ordenar por mayor a menor:", size=16, weight= self.weight_title)
        
        # Contenedor para el título y el Dropdown
        sort_criterion_container = ft.Container(
            content=ft.Column(
                controls=[sort_criterion_title, self.sort_criterion_dropdown],
                spacing=5
            ),
            padding=10
        )
        
        for value in self.chip_values:
            chip = ft.Chip(
                label=ft.Text(value),
                selected=False,  # Establecer todos los chips como seleccionados
                on_select=self.on_chip_selected,
                data=value,  # Usar 'data' para almacenar el valor que se usará para filtrar
                bgcolor = self.color_general,
                selected_color = ft.colors.DEEP_PURPLE_900,
            )
            self.chips.append(chip)

        chips_title = ft.Container(
            content=ft.Text(
                "Agrega o quita filtro(s) para los Resultados, por defecto están todos desactivados",
                size=18,
                weight=ft.FontWeight.BOLD
            ),
            padding=10
        )
        # Agregar los chips a la interfaz de usuario
        chips_container = ft.Container(
            content=ft.Row(controls=self.chips, wrap=True, width=1200),
            padding=10
        )

        chips_card = ft.Card(
            content=ft.Column(controls=[chips_title, chips_container]),
            elevation=5,
            margin=10
        )

        card_tabla = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(content=ft.Text("Resultados", size=20, color= self.color_title, weight= self.weight_title)),
                        ft.Column(controls=[self.data_table], scroll=ft.ScrollMode.ADAPTIVE, expand=1)
                    ],
                    expand=1
                ),
                padding=10
                ),  
            elevation=15,
            margin=10,
            height=580)

        # RangeSlider personalizado
        self.support_slider = ft.RangeSlider(
            min=1, 
            max=100, 
            start_value=int(self.min_support * 100),
            end_value=int(self.max_support * 100),
            divisions=99,
            inactive_color=ft.colors.DEEP_PURPLE_300,
            active_color=ft.colors.DEEP_PURPLE_700,
            overlay_color=ft.colors.DEEP_PURPLE_100,
            label="{value}%",
            on_change=self.on_support_change,
            width=300
        )

        support_slider_container = ft.Container(
            padding=10,
            content=ft.Row(controls=[self.support_slider])
        )

        card_support_slider = ft.Card(
            content=ft.Container(
                content=ft.Column(controls=[
                    ft.Text("Ajustar Soporte Mínimo y Máximo", size=20 , color= self.color_title, weight= self.weight_title),
                    support_slider_container
                ]),
                padding=20),  
            width=400,
            elevation=15)

        self.confidence_slider = ft.Slider(
            min=0, max=100, value=int(self.min_confidence * 100),
            divisions=100, label="{value}%", on_change=self.on_confidence_change,
            inactive_color=ft.colors.DEEP_PURPLE_300,
            active_color=ft.colors.DEEP_PURPLE_700,
            width=300
        )
        confidence_slider_container = ft.Container(
            padding=10,
            content=ft.Row(controls=[self.confidence_slider])
        )
        card_confidence_slider = ft.Card(
            content=ft.Container(
                content=ft.Column(controls=[
                    ft.Text("Ajustar Valor Mínimo de Confianza", size=20, color= self.color_title, weight= self.weight_title),
                    confidence_slider_container
                ]),
                padding=20
            ),  
            width=400,
            elevation=15)
        # Botón para ejecutar el análisis
        self.analyze_button = ft.ElevatedButton(
            text="Iniciar análisis",
            on_click=self.on_analyze_clicked,
            width=180
        )
        # Indicador de progreso
        self.progress_ring = ft.ProgressRing(width=30, height=30, stroke_width=5, visible=False)

        # Contenedor para el botón y el indicador de progreso
        button_container = ft.Card(
            content=ft.Container(
                content=ft.Row(controls=[self.analyze_button, self.progress_ring , sort_criterion_container, self.dialogo_manual],spacing=20),
                padding=10
            ),
            width=550,
            elevation=15  # Asegúrate de que la elevación sea consistente con otros Cards
        )
        divider = ft.Container(content=ft.Divider(height=2, color="white"),width=1500)
        return ft.Column(controls=[divider,
                                   ft.Row(controls=[card_support_slider, card_confidence_slider]),ft.Row(controls=[button_container]), chips_card,card_tabla,
                                   divider], spacing=10)
    

    async def on_sort_criterion_change(self, e):
        self.sort_criterion = e.control.value
        if self.calculated_rules is not None:
            await self.actualizar_interfaz_usuario(self.ordenar_reglas(self.calculated_rules))

    async def load_data(self, new_df):
        try:
            self.df = new_df
        except Exception as e:
            print(f"Ocurrió un error al cargar los datos: {e}")


    def ordenar_reglas(self, reglas_filtradas):
        # Ordenar las reglas por el criterio seleccionado
        if self.sort_criterion == "support":
            reglas_ordenadas = reglas_filtradas.sort_values(by='support', ascending=False)
        else:  # self.sort_criterion == "confidence"
            reglas_ordenadas = reglas_filtradas.sort_values(by='confidence', ascending=False)
        return reglas_ordenadas

    async def apply_association_rules(self):
        try:
            df_encoded = pd.get_dummies(self.df)
            df_encoded = df_encoded[df_encoded.columns[~df_encoded.columns.str.contains('no aplica|sin informacion')]]
            frecuentes = apriori(df_encoded, min_support=self.min_support, use_colnames=True, low_memory=True)
            reglas = association_rules(frecuentes, metric="confidence", min_threshold=self.min_confidence)
            reglas_filtradas = self.filtrar_reglas(reglas)
            await self.actualizar_interfaz_usuario(reglas_filtradas)
            self.calculated_rules = reglas_filtradas  
        except Exception as e:
            print(f"Ocurrió un error en las reglas de asociación: {e}")

    def filtrar_reglas(self, reglas):
        reglas_filtradas = reglas.copy()
        reglas_filtradas['num_antecedents'] = reglas_filtradas['antecedents'].apply(lambda x: len(x))
        reglas_filtradas['num_consequents'] = reglas_filtradas['consequents'].apply(lambda x: len(x))
        reglas_filtradas = reglas_filtradas[reglas_filtradas['support'] <= self.max_support]
        reglas_filtradas = reglas_filtradas[(reglas_filtradas['num_antecedents'] <= 3) & (reglas_filtradas['num_consequents'] >= 3) & (reglas_filtradas['num_consequents'] <= 10)]


        return self.ordenar_reglas(reglas_filtradas)


    def format_percentage(self, value):
        
        try:
            # Si 'value' es una cadena y ya contiene '%', devuélvela tal cual
            if isinstance(value, str) and '%' in value:
                return value
            # De lo contrario, intenta convertirlo a flotante y formatearlo
            return f"{float(value):.2f}%" 
        except ValueError:
            return value  # En caso de error, devuelve el valor original
    def format_float(self, value):
    
        try:
            # Intenta convertirlo a flotante y formatearlo
            return f"{float(value):.2f}"
        except ValueError:
            return value  
        
    async def actualizar_interfaz_usuario(self, reglas_ordenadas):
        try:
            if not self.active_chips:
                self.data_table.columns = []
                self.data_table.rows = []
                await self.data_table.update_async()
                return
            reglas_ordenadas['support'] = reglas_ordenadas['support'].apply(lambda x: x * 100 if isinstance(x, float) else x)
            reglas_ordenadas['support'] = reglas_ordenadas['support'].apply(self.format_percentage)
            
            reglas_ordenadas['confidence'] = reglas_ordenadas['confidence'].apply(lambda x: x * 100 if isinstance(x, float) else x)
            reglas_ordenadas['confidence'] = reglas_ordenadas['confidence'].apply(self.format_percentage)

            # Formatea 'lift' como un número flotante con dos decimales
            reglas_ordenadas['lift'] = reglas_ordenadas['lift'].apply(self.format_float)

            columns = [
                ft.DataColumn(label=ft.Text("Antecedentes"), numeric=False),
                ft.DataColumn(label=ft.Text("Consecuencias"), numeric=False),
                ft.DataColumn(label=ft.Text("Soporte"), numeric=False),
                ft.DataColumn(label=ft.Text("Confianza"), numeric=False),
                ft.DataColumn(label=ft.Text("Elevación"), numeric=False),
            ]
            
            rows = [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(', '.join(map(str, row['antecedents'])))),
                    ft.DataCell(ft.Text(', '.join(map(str, row['consequents'])))),
                    ft.DataCell(ft.Text(str(row['support']))),
                    ft.DataCell(ft.Text(str(row['confidence']))),
                    ft.DataCell(ft.Text(str(row['lift'])))
                ])
                for _, row in reglas_ordenadas.iterrows()
            ]

            self.data_table.columns = columns
            self.data_table.rows = rows
            await self.data_table.update_async()
        except Exception as e:
            print(f"Ocurrió un error al actualizar interfaz usuario: {e}")