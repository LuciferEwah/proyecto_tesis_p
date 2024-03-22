import flet as ft
from widgets.popbutton import PopButton
import unicodedata


class FormCardWidget(ft.UserControl):
    def __init__(self, title, field_groups, buttons, text_fields, page, width=None, height=None):
        super().__init__()
        self.title = title
        self.field_groups = field_groups
        self.buttons = buttons
        self.text_fields = text_fields
        self.page = page
        self.width = width
        self.height = height

    def build(self):
        title_card = ft.Text(self.title, size=20, weight=ft.FontWeight.BOLD)
        pop_button = PopButton(self.page).build()
        container_fields = self._create_fields_container(self.field_groups)
        title_row = ft.Row(controls=[pop_button, title_card])

        # Crear la Card principal con los campos
        main_card = ft.Card(
            width=self.width,
            elevation=15,
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    controls=[title_row, container_fields],
                    spacing=15,
                )
            )
        )


        # Contenedor para los botones con padding
        botones_container = ft.Container(
            content=ft.Row(
                controls=self.buttons,
                spacing=15,
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            ),
            padding=20,  
        )

        # Card que envuelve el contenedor de botones
        botones_card = ft.Card(
            content=botones_container,
            elevation=15,
            width=700,  # No especificar width permite que la Card crezca con el contenido
            height=None  # No especificar height permite que la Card se ajuste al tamaño del contenido
        )

        # Crear un contenedor principal que incluya ambas Cards
        main_container = ft.Column(
            controls=[
                main_card,  # Card principal
                botones_card  # Card de los botones, ahora se ajustará al tamaño del botón
            ],
        )

        return main_container

    def _create_fields_container(self, field_groups):
        # Crea controles individuales para cada grupo de campos
        controls = [self._create_field(field_data)
                    for field_data in field_groups]
        # Organiza todos los controles en una fila responsiva
        return ft.ResponsiveRow(controls=controls, run_spacing={"xs": 10})

    def _create_field(self, field_data):
        control_type = field_data.get("type", "text")
        col = field_data.get("col", {"md": 4})
        on_change = field_data.get("on_change")

        if control_type == "text":
            control = self._create_text_field(field_data, col, on_change)
        elif control_type == "dropdown":
            control = self._create_dropdown_field(field_data, col, on_change)
        elif control_type in ["int", "float"]:
            control = self._create_numeric_field(field_data, col, on_change)
        else:
            control = ft.Text(
                f"Tipo de campo no reconocido: {control_type}", col=col)
        return control

    def _create_text_field(self, field_data, col, on_change=None):
        label = field_data["label"]
        value = field_data.get("value", "")
        text_field = ft.TextField(
            label=label, value=value, col=col, on_change=on_change, expand=True)
        self.text_fields[label] = text_field
        return text_field

    def _create_dropdown_field(self, field_data, col, on_change=None):
        label = field_data["label"]
        options = field_data.get("options", [])
        selected_value = field_data.get("value")
        selected_value_str = str(selected_value).strip()
        dropdown_options = [ft.dropdown.Option(opt) for opt in options]
        dropdown = ft.Dropdown(
            label=label, options=dropdown_options, col=col, on_change=on_change, expand=True)

        if selected_value_str and selected_value_str.strip():
            # Normalizar las opciones y el valor seleccionado
            normalized_selected_value = self.normalizar_texto(
                selected_value_str)
            normalized_options = {self.normalizar_texto(
                opt): opt for opt in options}
            # Establecer el valor seleccionado que más se acerque
            closest_match = None
            if normalized_selected_value in normalized_options:
                closest_match = normalized_options[normalized_selected_value]
            else:
                # Implementa aquí tu lógica para encontrar la coincidencia más cercana
                closest_match = self.find_closest_match(
                    normalized_options, normalized_selected_value)
            if closest_match:
                dropdown.value = closest_match
        self.text_fields[label] = dropdown
        return dropdown

    async def actualizar_opciones_dropdown(self, label, valor, nuevas_opciones, todas_las_opciones):
        dropdown = self.text_fields.get(label)

        if dropdown:
            # Obtener el valor actual del dropdown
            valor_actual = valor

            # Si el valor actual no está en las nuevas opciones y no está vacío, añadirlo
            if valor_actual and valor_actual not in nuevas_opciones:
                nuevas_opciones.insert(0, valor_actual)

            # Actualizar las opciones del desplegable
            dropdown.options = [ft.dropdown.Option(
                opt) for opt in nuevas_opciones]

            # Normalizar las opciones completas y el valor actual
            normalized_todas_opciones = {self.normalizar_texto(
                opt): opt for opt in todas_las_opciones}
            normalized_current_value = self.normalizar_texto(
                dropdown.value) if dropdown.value else ""

            # Establecer el valor más cercano o el actual si ya está en las opciones
            closest_match = self.find_closest_match(
                normalized_todas_opciones, normalized_current_value)
            dropdown.value = normalized_todas_opciones.get(
                closest_match, valor_actual)

            # Actualizar el desplegable
            await dropdown.update_async()

    def _create_numeric_field(self, field_data, col, on_change=None):
        label = field_data["label"]
        value = field_data.get("value", "")
        if field_data.get("type") == "int":
            input_filter = ft.InputFilter(
                allow=True, regex_string=r"^(?:1(?:0[0-9]|1[0-8])|[1-9]?[0-9]|1[1-8]|0)$", replacement_string="")
        elif field_data.get("type") == "float":
            input_filter = ft.InputFilter(
                allow=True, regex_string=r"[0-9.]", replacement_string="")

        # Crea el campo de texto y asigna el filtro de entrada
        numeric_field = ft.TextField(
            label=label, value=value, input_filter=input_filter, col=col, on_change=on_change)
        self.text_fields[label] = numeric_field
        return numeric_field

    def normalizar_texto(self, texto):
        # Elimina espacios iniciales y finales
        texto = texto.strip()
        # Normaliza el texto para descomponer los caracteres en sus componentes
        texto_normalizado = unicodedata.normalize('NFD', texto)
        # Elimina los diacríticos (tildes) y convierte el texto a minúsculas
        texto_sin_tildes = ''.join(
            c for c in texto_normalizado if unicodedata.category(c) != 'Mn').lower()
        # Reemplaza 'ñ' por 'n'
        texto_sin_tildes = texto_sin_tildes.replace('ñ', 'n')

        return texto_sin_tildes

    def levenshtein_distance(self, s1, s2):

        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def find_closest_match(self, normalized_options, normalized_selected_value):
        if not normalized_options:
            return None

        closest_match = min(normalized_options.keys(
        ), key=lambda opt: self.levenshtein_distance(opt, normalized_selected_value))
        return normalized_options[closest_match]
