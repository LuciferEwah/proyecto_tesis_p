import flet as ft
from widgets.grafico_widget import GraficoBarraWidget, GraficoCircularWidget
import pandas as pd
from widgets.kpi import DataCardWidget
import asyncio

class GraphScreen(ft.UserControl):
    def __init__(self, db, page, route_change_handler, nav_rail_class):
        super().__init__()
        self.db = db
        self.page = page
        self.route_change_handler = route_change_handler
        self.nav_rail_class = nav_rail_class



    def build(self):
        self.pr = ft.ProgressRing(width=30, height=30, stroke_width = 5, visible  = False)

        self.dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Seleccione una categoría"),
                ft.dropdown.Option("Victimas"),
                ft.dropdown.Option("Denunciados")
            ],
            on_change=self.dropdown_changed,
            value="Seleccione una categoría",
        )
        self.button = ft.ElevatedButton(text="Mostrar graficos", on_click=self.button_clicked, visible=False)


        
        botones_card = ft.Card(
            content=ft.Row(
                controls=[self.dropdown, self.button, self.pr],
                spacing=15,
                alignment=ft.MainAxisAlignment.START
            ),
            elevation=15,
            width=750,
            height=100,
            margin=10
        )
        self.dropdown_categorias = ft.Dropdown(
            width=200,
            on_change=self.categoria_seleccionada
        )
   
            

        # Título para el dropdown de categorías
        self.categorias_title = ft.Text(
            value="Seleccione una categoría: ",
            style=ft.TextStyle(size=16),
        )

        # Row para centrar el título y el dropdown de categorías
        categorias_row = ft.Row(
            controls=[self.categorias_title, self.dropdown_categorias],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        # Card para el dropdown de categorías centrado
        card_dropdown_categorias = ft.Card(
            elevation=15,
            width=500,  # Ajusta este valor si es necesario
            content= ft.Container(content=categorias_row,
            padding=20,

        ))
        

        self.grafico_barra = GraficoBarraWidget(self.page)
        
        self.grafico_circular = GraficoCircularWidget(self.page)



        grafico_circular_container = ft.Row(
            controls=[self.grafico_circular],
            alignment=ft.MainAxisAlignment.CENTER,  # Centra el gráfico circular en el Row

        )
        self.total_vic_data_card = DataCardWidget(
            self.page, "Total de Víctimas")
        self.total_denounced_data_card = DataCardWidget(
            self.page, "Total de Denunciados")
        asyncio.create_task(self.initialize_async_data())
        # Contenedor general para gráficos
        self.grafico_container = ft.Container(
            content=ft.Column(
                controls=[
                    card_dropdown_categorias,   # Control para selección de categorías
                    self.grafico_barra,         # Widget para el gráfico de barras
                    grafico_circular_container, # Contenedor del gráfico circular centrado
                    # Otros controles que quieras agregar después del gráfico circular
                ],
                alignment=ft.MainAxisAlignment.CENTER,
 
            ),
            visible=False
        )

        self.contenedor_vic_kpi =  ft.Container(content=self.total_vic_data_card,visible=False)
        self.contenedor_den_kpi =  ft.Container(content=self.total_denounced_data_card, visible= False)
        
        scrollable_content = ft.Column(
            [ft.Row(controls=[botones_card, self.contenedor_vic_kpi , self.contenedor_den_kpi]), self.grafico_container],  
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

        return ft.Row(
            [
                self.nav_rail_class.create_rail(),
                ft.VerticalDivider(width=3),
                scrollable_content
            ],
            vertical_alignment=ft.CrossAxisAlignment.START
        )
    async def get_total_victims(self):
        total_victims = await self.db.get_total_victimas()
        return total_victims
    
    async def get_age_stats_denounced(self):
        total_denounced = await self.db.get_total_denunciados()
        return total_denounced
    
    async def initialize_async_data(self):

        total_victims = await self.get_total_victims()
        total_denounced = await self.get_age_stats_denounced()
        await self.total_vic_data_card.update_data(total_victims)
        await self.total_denounced_data_card.update_data(total_denounced)

    async def dropdown_changed(self, e):
        tipo = e.control.value
        opciones_categorias = []
        if tipo != "Seleccione una categoría":
            if tipo == "Victimas":
                self.grafico_container.visible = False
                self.contenedor_vic_kpi.visible = True
                await self.contenedor_vic_kpi.update_async()
                self.contenedor_den_kpi.visible = False
                await self.contenedor_den_kpi.update_async()
                _, columnas_comunes = await self.combinado_victimas()
                opciones_categorias = list(columnas_comunes)
                
            elif tipo == "Denunciados":
                # Obtener nombres de columnas para denunciados
                self.contenedor_den_kpi.visible = True
                await self.contenedor_den_kpi.update_async()
                self.contenedor_vic_kpi.visible = False
                await self.contenedor_vic_kpi.update_async()
                _, columnas_denunciantes = await self.db.get_all_denunciados()
                opciones_categorias = columnas_denunciantes
                opciones_categorias.remove('id_causa')

            # Actualizar las opciones del dropdown de categorías
            self.dropdown_categorias.options = [ft.dropdown.Option(opcion) for opcion in opciones_categorias]
            

            # Actualizar la visibilidad de los botones y contenedores
            self.button.visible = tipo != ""
            self.grafico_container.visible = False
            await self.grafico_container.update_async()
            await self.dropdown_categorias.update_async()
            await self.button.update_async()
            await self.page.update_async()
        else:
            self.contenedor_den_kpi.visible = False
            await self.contenedor_den_kpi.update_async()
            self.contenedor_vic_kpi.visible = False
            await self.contenedor_vic_kpi.update_async()
            self.grafico_container.visible = False
            await self.grafico_container.update_async()

    async def categoria_seleccionada(self, e):
        categoria = e.control.value
        tipo = self.dropdown.value  

        if categoria != "Seleccione una categoría":
            if tipo == "Victimas":
                df_combinado, _ = await self.combinado_victimas()  # Separar DataFrame y conjunto
                datos_df = pd.DataFrame(df_combinado)
            elif tipo == "Denunciados":
                datos, columnas_denunciados = await self.db.get_all_denunciados()
                datos_df = pd.DataFrame(datos, columns=columnas_denunciados)

                
            # Filtra los datos basándote en la categoría seleccionada
            conteo = datos_df[categoria].value_counts().reset_index()
            conteo.columns = [categoria, 'count']
            categorias = conteo[categoria].tolist()
            valores = conteo['count'].tolist()

            # Actualiza los gráficos con los datos filtrados
            await self.grafico_barra.update_chart(categorias, valores,categoria)
            await self.grafico_circular.update_chart(categorias, valores,categoria)

    async def button_clicked(self, e):
        if self.dropdown.value == "Victimas":
                self.grafico_container.visible = True
                await self.grafico_container.update_async()
        
        elif self.dropdown.value == "Denunciados":
                self.grafico_container.visible = True
                await self.grafico_container.update_async()
        await self.page.update_async()


    async def combinado_victimas(self):
        # Obtener datos y columnas de víctimas y denunciantes
        victimas_data, columnas_victimas = await self.db.get_all_victimas()
        denunciantes_data, columnas_denunciantes = await self.db.get_all_denunciantes()
        
        # Crear DataFrames para víctimas y denunciantes
        df_victimas = pd.DataFrame(victimas_data, columns=columnas_victimas)
        df_denunciantes = pd.DataFrame(denunciantes_data, columns=columnas_denunciantes)

        # Asegurar que df_denunciantes tenga las mismas columnas que df_victimas
        columnas_comunes = set(columnas_victimas).intersection(columnas_denunciantes)
        df_tabla_denunciante_es_victima = df_denunciantes[df_denunciantes['es_denunciante_victima'] == 'si']
        df_tabla_denunciante_es_victima = df_tabla_denunciante_es_victima[list(columnas_comunes)]

        # Concatenar DataFrames asegurando que tienen las mismas columnas
        df_combinado = pd.concat([df_victimas[list(columnas_comunes)], df_tabla_denunciante_es_victima], ignore_index=True)
        df_combinado.drop('id_causa', axis=1, inplace=True)
        columnas_comunes.remove('id_causa')
        return df_combinado, columnas_comunes