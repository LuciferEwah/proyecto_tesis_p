import flet as ft


class ConfirmationDialog:
    def __init__(self, page, title, content, on_confirm):
        self.page = page
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[
                ft.TextButton("Sí", on_click=self.on_yes_click),
                ft.TextButton("No", on_click=self.on_no_click),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.on_confirm = on_confirm

    async def on_yes_click(self, e):
        self.dialog.open = False
        await self.page.update_async()

        await self.on_confirm()   # Call the on_confirm function directly

    async def on_no_click(self, e):
        self.dialog.open = False
        await self.page.update_async()

    async def open(self):
        self.page.dialog = self.dialog
        self.dialog.open = True
        await self.page.update_async()


class InfoTreeModels:
    def __init__(self, page, title):
        self.page = page
        self.size_text_title = 18
        self.color_title = ft.colors.AMBER_900
        self.size_text_normal = 16
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Column([
                ft.Text("Análisis de Datos:", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=self.size_text_title, color=self.color_title)),
                ft.Text("Una vez seleccionada la categoría, el usuario puede presionar el botón 'Iniciar análisiss' para iniciar el análisis. Un anillo de progreso indica que el proceso está en curso.", size=self.size_text_normal),
                
                ft.Text("Configuración del Modelo:", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=self.size_text_title, color=self.color_title)),
                ft.Text("Antes o después de iniciar el análisis, el usuario puede ajustar los parámetros de los modelos de análisis estadístico.", size=self.size_text_normal),
                
                ft.Text("Árbol de Decisión:", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=self.size_text_title, color=self.color_title)),
                ft.Text("Se permiten ajustes en la profundidad máxima del árbol, el mínimo de muestras para dividir y el mínimo de muestras en la hoja. Además, se pueden seleccionar el criterio (entropía o gini), el método de división y la cantidad máxima de características a considerar.", size=self.size_text_normal),
                
                ft.Text("Random Forest:", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=self.size_text_title, color=self.color_title)),
                ft.Text("Similar al árbol de decisión pero con la adición de ajustar el número de estimadores. Los demás parámetros son equivalentes a los del árbol de decisión.", size=self.size_text_normal),
                
                ft.Text("Resultados del Análisis:", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=self.size_text_title, color=self.color_title)),
                ft.Text('Después de ejecutar el análisis, la interfaz muestra las "Clasificaciones de Características" para los modelos de Árbol de Decisión y Random Forest, enumerando las características más importantes y su importancia relativa en la toma de decisiones del modelo.', size=self.size_text_normal),
                
                ft.Text("Guardado de Árboles de Decisiones:", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=self.size_text_title, color=self.color_title)),
                ft.Text("Existe un botón que permite al usuario guardar la representación visual de los árboles de decisiones generados durante el análisis. Esto puede ser útil para revisión posterior o para preparar informes.", size=self.size_text_normal),
                
                ft.Text("Detalles de los Parámetros del Modelo:", style=ft.TextStyle(weight=ft.FontWeight.BOLD, size=self.size_text_title, color=self.color_title)),
                ft.Text("Profundidad Máxima: Define cuán complejo puede ser el árbol. Un árbol más profundo puede capturar más detalles, pero también puede ajustarse demasiado a los datos (overfitting).", size=self.size_text_normal),
                ft.Text("Mínimo de Muestras para Dividir: El número mínimo de muestras necesarias para dividir un nodo. Si se establece muy bajo, el modelo puede capturar demasiado ruido en los datos.", size=self.size_text_normal),
                ft.Text("Mínimo de Muestras en Hoja: El número mínimo de muestras requeridas para ser una hoja del árbol. Similar al parámetro anterior, ayuda a controlar el overfitting.", size=self.size_text_normal),
                ft.Text("Número de Estimadores: Específico para Random Forest, indica cuántos árboles individuales se deben construir en el bosque.", size=self.size_text_normal),
                ft.Text("Criterio: Puede ser 'entropía' o 'gini', y determina cómo se mide la calidad de una división.", size=self.size_text_normal),
                ft.Text("Divisor: Indica si se selecciona la mejor división o una división al azar, lo que puede ayudar a mejorar la diversidad en el modelo y a evitar el overfitting.", size=self.size_text_normal),
                ft.Text("Máx. Características: El número de características a considerar al buscar la mejor división; puede ser un número fijo, 'sqrt' o 'log2'.", size=self.size_text_normal),
            ]),
            actions=[
               ft.Container(
                    content=ft.TextButton(
                        content=ft.Text("Cerrar", style=ft.TextStyle(size=24,weight=ft.FontWeight.BOLD,color=ft.colors.BLUE_600)),
                        on_click=self.close_dialog,
                        expand=True

                    ),
                    padding=20, # Aumenta el relleno para un área clickeable más grande
                    height=200,  # Asegura que el contenedor ocupe todo el ancho disponible
                    width=1000
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
    
    async def close_dialog(self, e):
        self.dialog.open = False
        await self.page.update_async()

    async def open_dialog(self):
        self.page.dialog = self.dialog
        self.dialog.open = True
        await self.page.update_async()

class AssociationRulesDialog:
    def __init__(self, page):
        self.page = page
        self.size_text_title = 18
        self.color_title = ft.colors.AMBER_900
        self.size_text_normal = 16
        
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Manual de Usuario - Reglas de Asociación"),
            content=ft.Column([
            ft.Text("Cómo utilizar esta herramienta:", style=ft.TextStyle(size=self.size_text_title, color=self.color_title, weight=ft.FontWeight.BOLD)),
            ft.Text("Esta herramienta analiza las relaciones entre diferentes aspectos de casos legales, considerando tanto a las víctimas como a los denunciados.", size=self.size_text_normal),

            ft.Text("Ajuste de Parámetros:", style=ft.TextStyle(size=self.size_text_title, color=self.color_title, weight=ft.FontWeight.BOLD)),
            ft.Text("Establezca los valores mínimos y máximos deseados para determinar la relevancia de las relaciones encontradas. Esto se hace utilizando los deslizadores en la parte superior.", size=self.size_text_normal),

            ft.Text("Iniciar el Análisis:", style=ft.TextStyle(size=self.size_text_title, color=self.color_title, weight=ft.FontWeight.BOLD)),
            ft.Text("Una vez establecidos los parámetros, use el botón 'Iniciar análisis' para procesar la información.", size=self.size_text_normal),

            ft.Text("Filtrado de Datos:", style=ft.TextStyle(size=self.size_text_title, color=self.color_title, weight=ft.FontWeight.BOLD)),
            ft.Text("Seleccione los aspectos específicos que le interesan de los casos para refinar los resultados, como la ubicación, la descripción del caso,entre otros. Solo se mostrarán las relaciones que incluyen los aspectos seleccionados.", size=self.size_text_normal),
            ft.Text("Orden de los Resultados:", style=ft.TextStyle(size=self.size_text_title, color=self.color_title, weight=ft.FontWeight.BOLD)),
            ft.Text("Puede ordenar los resultados según su relevancia estadística, como la frecuencia o la fuerza de la relación, para identificar las tendencias más importantes.", size=self.size_text_normal),
            ft.Text("Interpretación de los Datos y Términos Clave:", style=ft.TextStyle(size=self.size_text_title, color=self.color_title, weight=ft.FontWeight.BOLD)),
            ft.Text("Cuando se presentan los resultados, encontrará términos clave que describen las relaciones en los casos legales:", size=self.size_text_normal),

            ft.Text("Antecedente y Consecuencia:", style=ft.TextStyle(size=self.size_text_title, color=self.color_title, weight=ft.FontWeight.BOLD)),
            ft.Text("Los 'antecedentes' son hechos o circunstancias que ocurren antes en los casos, mientras que las 'consecuencias' son lo que sigue. Por ejemplo, si observamos que los 'antecedentes' son 'víctima en una zona urbana', una 'consecuencia' común podría ser 'denuncias de robo'.", size=self.size_text_normal),

            ft.Text("Soporte:", style=ft.TextStyle(size=self.size_text_title, color=self.color_title, weight=ft.FontWeight.BOLD)),
            ft.Text("El soporte nos dice qué tan común es la relación en todos los casos analizados. Un soporte más alto significa que la relación ocurre en una mayor proporción de los casos.", size=self.size_text_normal),

            ft.Text("Confianza:", style=ft.TextStyle(size=self.size_text_title, color=self.color_title, weight=ft.FontWeight.BOLD)),
            ft.Text("La confianza mide la fiabilidad de la relación. Por ejemplo, una confianza alta en la relación entre 'víctima en una zona urbana' y 'denuncias de robo' significaría que, cuando se dael primer hecho, es muy probable que el segundo también sea cierto.", size=self.size_text_normal),
            ft.Text("Elevación (Lift):", style=ft.TextStyle(size=self.size_text_title, color=self.color_title, weight=ft.FontWeight.BOLD)),
            ft.Text("El 'lift' nos indica la fuerza de una relación, comparando cuán frecuente es la consecuencia en los antecedentes respecto a su frecuencia general. Un 'lift' mayor que 1 sugiere que los antecedentes aumentan la probabilidad de que ocurra la consecuencia, lo cual podría indicar una conexión fuerte entre ambos.", size=self.size_text_normal),
        ]),
            actions=[
               ft.Container(
                    content=ft.TextButton(
                        content=ft.Text("Cerrar", style=ft.TextStyle(size=24,weight=ft.FontWeight.BOLD,color=ft.colors.BLUE_600)),
                        on_click=self.close_dialog,
                        expand=True

                    ),
                    padding=20,
                    height=200,  
                    width=1000
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
    
    async def close_dialog(self, e):
        self.dialog.open = False
        await self.page.update_async()

    async def open_dialog(self):
        self.page.dialog = self.dialog
        self.dialog.open = True
        await self.page.update_async()
