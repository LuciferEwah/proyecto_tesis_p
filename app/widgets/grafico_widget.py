import flet as ft
import pandas as pd
import random


def random_color():
    r = random.randint(0, 100)
    g = random.randint(0, 100)
    b = random.randint(0, 100)
    return f"#{r:02x}{g:02x}{b:02x}"

class GraficoBarraWidget(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.card = None
        self.df = None  
        self.chart = None  # Añade este atributo

    def build(self):

        
        # Crear la gráfica inicial
        initial_chart = self.generate_bar_chart([], [])
        self.card = ft.Card(
            content=ft.Container(
                content=initial_chart,
                height=600,
                padding=40
            ),
            elevation=15
        )
        return self.card

    async def on_dropdown_change(self, e):
        categoria = e.control.value
        if categoria != "Seleccione una categoría":
            conteo = self.df[categoria].value_counts().reset_index()
            conteo.columns = [categoria, 'count']
            categorias = conteo[categoria].tolist()
            datos = conteo['count'].tolist()
            await self.update_chart(categorias, datos)

    async def update_chart(self, categorias, datos, categoria_seleccionada):
        new_chart = self.generate_bar_chart(categorias, datos, categoria_seleccionada)  # Pasar la categoría seleccionada al método de generación
        self.card.content.content = new_chart
        await self.card.update_async()


    def generate_bar_chart(self, categorias, datos, categoria_seleccionada=None):
        if categoria_seleccionada is None:
            top_axis_title = "Seleccione una categoría"
        else:
            top_axis_title = "cantidad de casos vs " + categoria_seleccionada.replace('_', ' ')
        if categorias is None or datos is None:
            categorias = []
            datos = [0]

        self.bar_original_colors = [random_color() for _ in categorias]
        global PALETA_COLORES
        PALETA_COLORES = dict(zip(categorias, self.bar_original_colors))  # Usar colores originales
        
        bar_groups = [
            ft.BarChartGroup(
                x=i,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=datos[i],
                        width=40,
                        color=self.bar_original_colors[i],  # Usar color almacenado
                        border_radius=0,
                        tooltip=f"{categorias[i]}: {datos[i]}"
                    )
                ],
            ) for i in range(len(categorias))
        ]

        chart = ft.BarChart(
            bar_groups=bar_groups,
            left_axis=ft.ChartAxis(
                labels=[ft.ChartAxisLabel(value=i, label=ft.Text(" ")) for i in range(0, max(datos, default=0) + 10, 10)],
                title=ft.Text("cantidad"),
                title_size=20
            ),
            bottom_axis=ft.ChartAxis(
                labels=[ft.ChartAxisLabel(value=i, label=ft.Text(self.split_label(categorias[i]))) for i in range(len(categorias))],
                labels_size=20,
            ),
            top_axis=ft.ChartAxis(
            title=ft.Text(top_axis_title,size=20),  # Configura el título del eje superior
            title_size=50,  # Tamaño del área del título
            show_labels=False  # Oculta las etiquetas (puedes cambiarlo si necesitas mostrar etiquetas)
            ),
            interactive=True,
            expand=True,
            horizontal_grid_lines=ft.ChartGridLines(interval=25, color=ft.colors.GREY_300, width=0.5),  # Añade líneas horizontales

        )


        self.chart = chart  # Asigna el gráfico a self.chart
        chart.on_chart_event = self.on_chart_event
        return chart


    async def on_chart_event(self, e):
        if e.type == "PointerHoverEvent":
            if e.group_index is not None and e.rod_index is not None:
                for idx, group in enumerate(self.chart.bar_groups):
                    for rod in group.bar_rods:
                        # Cambiar color si el ratón está sobre la barra
                        rod.color = ft.colors.WHITE if idx == e.group_index else self.bar_original_colors[idx]
                await self.chart.update_async()

        elif e.type == "PointerExitEvent":
            # Restablecer el color original de todas las barras cuando el ratón sale del gráfico
            for idx, group in enumerate(self.chart.bar_groups):
                for rod in group.bar_rods:
                    rod.color = self.bar_original_colors[idx]
            await self.chart.update_async()


    def split_label(self, label):
        # Divide las etiquetas más largas en líneas separadas
        max_chars_per_line = 10  # Ajusta este valor según sea necesario
        return '\n'.join([label[i:i+max_chars_per_line] for i in range(0, len(label), max_chars_per_line)])


    async def update_data(self, data, tipo):
        if tipo == "Victimas":
            self.df = pd.DataFrame(data, columns=[
                                                'grupo_edad', 'sexo', 'nacionalidad',
                                                'nacionalidad_extranjera', 'profesion_oficio', 'estudios',
                                                'parentesco_acusado', 'parentesco_acusado_otro', 'caracter_lesion',
                                                'descripcion_lesion', 'estado_temperancia', 'temperancia_otro',
                                                'temperancia_descripcion', 'comuna', 'estado_civil'
                                            ])
            

        elif tipo == "Denunciados":
            self.df = pd.DataFrame(data, columns=[
        "grupo_edad", "sexo", "nacionalidad",
        "nacionalidad_Extranjera", "profesion_oficio", "estudios",
        "caracter_lesion", "lesiones_descripcion", "estado_temperancia",
        "temperancia_otro", "temperancia_descripcion", "otros_antecedentes",
        "comuna", "estado_civil", "nivel_riesgo"
    ])




class GraficoCircularWidget(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.card = None
        self.df = None  # DataFrame que contendrá los datos reales
        self.is_hovering = False  # Agregar una variable para rastrear el estado de hover

    def build(self):

        
        # Crear el gráfico circular inicial
        initial_chart = self.generate_pie_chart([], [])
        self.card = ft.Card(
            content=ft.Container(
                content=initial_chart,
                height=650,
                width=650,
                padding=40
            ),
            elevation=15
        )
        return self.card

    async def on_dropdown_change(self, e):
        categoria = e.control.value
        if categoria != "Seleccione una categoría":
            conteo = self.df[categoria].value_counts().reset_index()
            conteo.columns = [categoria, 'count']
            categorias = conteo[categoria].tolist()
            datos = conteo['count'].tolist()
            await self.update_chart(categorias, datos, categoria)

    async def update_chart(self, categorias, datos, _):
        self.categorias = categorias  # Guarda las categorías en la instancia
        new_chart = self.generate_pie_chart(categorias, datos)
        self.card.content.content = new_chart
        await self.card.update_async()




    def generate_pie_chart(self, categorias, datos):


        self.total_datos = sum(datos)
        self.normal_radius = 300
        self.hover_radius = 310
        self.normal_title_style = ft.TextStyle(
            size=12, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD
        )
        self.hover_title_style = ft.TextStyle(
            size=16,
            color=ft.colors.WHITE,
            weight=ft.FontWeight.BOLD,
            shadow=ft.BoxShadow(blur_radius=2, color=ft.colors.BLACK54),
        )

        sections = [
            ft.PieChartSection(
                value=valor,
                title=f"{round((valor / self.total_datos) * 100, 2)}%",
                title_style=self.normal_title_style,
                color=PALETA_COLORES[categoria],
                radius=self.normal_radius
            ) for categoria, valor in zip(categorias, datos)
        ]

        self.chart = ft.PieChart(
            sections=sections,
            expand=True,
            center_space_radius=0,  # Sin espacio en el centro
            sections_space=0,
            on_chart_event=self.on_chart_event
        )
        return self.chart
    
    async def on_chart_event(self, e: ft.PieChartEvent):
        if e.type == "PointerHoverEvent":
            # Ratón sobre una sección
            for idx, section in enumerate(self.chart.sections):
                if idx == e.section_index:
                    # Resaltar el segmento seleccionado
                    section.radius = self.hover_radius
                    section.title_style = self.hover_title_style
                    valor = section.value
                    categoria = self.categorias[idx]
                    porcentaje = round((valor / self.total_datos) * 100, 2)
                    section.title = f"{categoria}: {porcentaje}%"
                else:
                    # Ocultar los títulos de los segmentos no seleccionados
                    section.title = ""
                    section.radius = self.normal_radius
                    section.title_style = self.normal_title_style
        elif e.type == "PointerExitEvent":
            # Ratón deja una sección
            for section in self.chart.sections:
                # Restablecer el estilo normal de todos los segmentos
                valor = section.value
                porcentaje = round((valor / self.total_datos) * 100, 2)
                section.title = f"{porcentaje}%"
                section.radius = self.normal_radius
                section.title_style = self.normal_title_style

        await self.chart.update_async()

    async def update_data(self, data, tipo):
        if tipo == "Victimas":
            self.df = pd.DataFrame(data, columns=[
                                                'grupo_edad', 'sexo', 'nacionalidad',
                                                'nacionalidad_extranjera', 'profesion_oficio', 'estudios',
                                                'parentesco_acusado', 'parentesco_acusado_otro', 'caracter_lesion',
                                                'descripcion_lesion', 'estado_temperancia', 'temperancia_otro',
                                                'temperancia_descripcion', 'comuna', 'estado_civil'
                                            ])

        elif tipo == "Denunciados":
            
            self.df = pd.DataFrame(data, columns=[
                "grupo_edad", "sexo", "nacionalidad",
                "nacionalidad_Extranjera", "profesion_oficio", "estudios",
                "caracter_lesion", "lesiones_descripcion", "estado_temperancia",
                "temperancia_otro", "temperancia_descripcion", "otros_antecedentes",
                "comuna", "estado_civil", "nivel_riesgo"
            ])