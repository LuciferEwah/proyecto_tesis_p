import flet as ft


class TablaWidget(ft.UserControl):
    def __init__(self, data, columns, on_row_selected, titulo, text_button,db = None, disabled=None, use_default_size=True, fixed_width=1280, rows_per_page = 50, boton_extra=None):
        super().__init__()
        self.data = data
        self.columns = columns
        self.on_row_selected = on_row_selected
        self.titulo = titulo  # Nuevo parámetro para el título
        self.database = db
        self.use_default_size = use_default_size
        self.tabla = None  # Inicializa aquí el atributo tabla
        self.disabled = disabled
        self.fixed_width = fixed_width
        self.rows_per_page = rows_per_page
        self.text_button = text_button
        self.boton_extra = boton_extra  
    def build(self):

        # Crear el Container con el título y padding
        titulo_container = ft.Container(
            content=ft.Text(self.titulo, size=24, weight=ft.FontWeight.BOLD),
            padding=20  # Aumenta el padding para más espacio alrededor del texto
        )

        # Crear la Card para el título
        titulo_card = ft.Card(
            content=titulo_container,
            elevation=10,
            margin=10,
        )

        ft_columns = [ft.DataColumn(ft.Text(col_name))
                      for col_name in self.columns]

        ft_rows = []
        for row_data in self.data:
            cells = [ft.DataCell(ft.Text(str(item))) for item in row_data]
            ft_row = ft.DataRow(
                cells, on_select_changed=self.on_row_select_changed)
            ft_rows.append(ft_row)

        agregar_button = ft.OutlinedButton(
            self.text_button,
            icon=ft.icons.ADD,
            icon_color="green400",
            on_click=self.on_agregar_clicked,
            disabled=self.disabled
        )

    # Crear el DataTable
        self.tabla = ft.DataTable(
            width=self.fixed_width,
            border=ft.border.all(2, "purple"),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(3, "white"),
            horizontal_lines=ft.border.BorderSide(1, "white"),
            heading_row_color=ft.colors.BLACK12,
            heading_row_height=100,
            data_row_color={"hovered": "0x30FF0000"},
            divider_thickness=0,
            column_spacing=20,
            columns=ft_columns,
            rows=ft_rows,

        )

        scrollable_table = ft.Column(
            controls=[self.tabla],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=1,

        )

        tabla_card = ft.Card(
            content=scrollable_table,
            elevation=15,


        )
        if self.use_default_size:
            tabla_card.width = None
            tabla_card.height = 450
        else:
            tabla_card.width = None
            tabla_card.height = None

        botones_card = ft.Card(
            content=ft.Column(
                controls=[agregar_button],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=300,
            height=70,  # Ajusta el height para los botones
            elevation=15
        )

        # Crear un contenedor principal para ambos Card
        main_container = ft.Column(
            controls=[
                titulo_card,  # Card del título
                tabla_card,  # Card de la tabla
                ft.Row(controls=[botones_card, self.boton_extra]) if self.boton_extra else botones_card
            ],
        )

        # Devolver el contenedor principal
        return main_container

    async def on_row_select_changed(self, event):
        selected_id = event.control.cells[0].content.value
        await self.on_row_selected(selected_id)
        # print("Selected ID:", selected_id)

    async def update_table(self, new_data, new_columns):
        # Create new columns and rows based on the new data
        ft_columns = [ft.DataColumn(label=ft.Text(col)) for col in new_columns]
        ft_rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(str(item))) for item in row_data],
                              on_select_changed=self.on_row_select_changed)  # Agrega el controlador de eventos aquí
                   for row_data in new_data]

        # Update the DataTable's columns and rows
        self.tabla.columns = ft_columns
        self.tabla.rows = ft_rows
        # Call the update method with no arguments to refresh the control
        await self.tabla.update_async()

    async def on_agregar_clicked(self, event):
        selected_id = None
        await self.on_row_selected(selected_id)


    async def calcular_total_paginas(self):
        try:
            total_causas_count = await self.database.get_total_causas_count()
            self.total_pages = max(1, -(-total_causas_count // self.rows_per_page))
        except Exception as e:
            print(f"Error al calcular el total de páginas: {e}")
            self.total_pages = 1