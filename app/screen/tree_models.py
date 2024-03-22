import flet as ft
import pandas as pd
from widgets.tree_analysis import ModelAnalysisWidget


class TreeModelsScreen(ft.UserControl):
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


        self.button_mcl = ft.ElevatedButton(text="Mostrar análisis de datos", on_click=self.button_clicked_2, visible=False)
        
        botones_card = ft.Card(
            content=ft.Row(
                controls=[self.dropdown, self.button_mcl, self.pr],
                spacing=15,
                alignment=ft.MainAxisAlignment.START
            ),
            elevation=15,
            width=750,
            height=100,
            margin=10
        )


        self.model_analysis_widget = ModelAnalysisWidget(self.page)

        scrollable_content = ft.Column(
            [botones_card, self.model_analysis_widget],  
            alignment=ft.MainAxisAlignment.START,
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

    async def dropdown_changed(self, e):
        tipo = e.control.value
        if tipo != "Seleccione una categoría":
            if tipo == "Victimas":
                pass
    
            elif tipo == "Denunciados":
                pass

            self.button_mcl.visible = tipo != ""
        
            await self.button_mcl.update_async()
        

    async def button_clicked_2(self, e):
        if self.dropdown.value == "Victimas":
            self.pr.visible = True
            await self.pr.update_async()
            # Extrae el DataFrame de la tupla devuelta por combinado_victimas
            df_combinado, _ = await self.combinado_victimas()
            df_combinado.drop('id_causa', axis=1, inplace=True)
            await self.model_analysis_widget.set_dataframe(df_combinado)
            await self.model_analysis_widget.analyze_data(df_combinado, self.model_analysis_widget.columna_objetivo)
            self.pr.visible = False
            await self.pr.update_async()

        elif self.dropdown.value == "Denunciados":
            self.pr.visible = True
            await self.pr.update_async()
            datos_denunciados, columnas_denunciantes = await self.db.get_all_denunciados()
            df_denunciados = pd.DataFrame(datos_denunciados, columns=columnas_denunciantes) 
            df_denunciados.drop('id_causa', axis=1, inplace=True)
            await self.model_analysis_widget.set_dataframe(df_denunciados)
            await self.model_analysis_widget.analyze_data(df_denunciados, self.model_analysis_widget.columna_objetivo)
            self.pr.visible = False
            await self.pr.update_async()

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
        return df_combinado, columnas_comunes