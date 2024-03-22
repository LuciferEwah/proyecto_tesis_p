import flet as ft


def get_custom_color_scheme():
    return ft.ColorScheme(
        primary=ft.colors.WHITE,

        # on_primary=ft.colors.RED_500,  # Blanco para texto sobre elementos primarios
        # primary_container=ft.colors.RED_500,
        # on_primary_container=ft.colors.RED_500,
        # secondary=ft.colors.INDIGO_500,  # Un tono de naranja para elementos secundarios
        # on_secondary=ft.colors.INDIGO_500,  # Blanco para texto sobre elementos secundarios
        # Color claro para contenedores secundarios
        secondary_container=ft.colors.INDIGO_900,

        on_secondary_container=ft.colors.INDIGO_100,
        #tertiary=ft.colors.RED_900,  # Un tono de verde para elementos terciarios
        # on_tertiary=ft.colors.RED_900,  # Blanco para texto sobre elementos terciarios
        # tertiary_container="#B2DFDB",  # Color claro para contenedores terciarios
        # on_tertiary_container="#00695C",  # Verde para texto sobre contenedores terciarios
        # error_container="#FFCDD2",  # Color claro para contenedores de error
        # on_error_container="#D32F2F",  # Rojo para texto sobre contenedores de error
        # background="#FFFFFF",  # Blanco para el fondo
        # on_background="#000000",  # Negro para texto sobre fondo
        surface="#23262a",  # Blanco para superficies de widgets
        # =on_surface="#000000",  # Negro para texto sobre superficies
        # surface_variant=ft.colors.RED_900,  # Gris claro para variantes de superficie
        # on_surface_variant="#000000",  # Negro para texto sobre variantes de superficie
        # outline="#BDBDBD",  # Gris para contornos
        # outline_variant="#757575",  # Gris oscuro para contornos variantes
        # shadow="#000000",  # Negro para sombras
        # scrim="#000000",  # Negro para mallas
        # inverse_surface="#424242",  # Gris oscuro para superficies inversas
        # on_inverse_surface="#FFFFFF",  # Blanco para texto sobre superficies inversas
        # inverse_primary="#82B1FF",  # Azul claro para acentos en superficies inversas
        # surface_tint="#0D47A1",  # Azul oscuro para tintes en superficies
    )


def get_text_theme():
    white_text_style = ft.TextStyle(color=ft.colors.WHITE)
    return ft.TextTheme(
        body_large=white_text_style,
        body_medium=white_text_style,
        body_small=white_text_style,
        display_large=white_text_style,
        display_medium=white_text_style,
        display_small=white_text_style,
        headline_large=white_text_style,
        headline_medium=white_text_style,
        headline_small=white_text_style,
        label_large=white_text_style,
        label_medium=white_text_style,
        label_small=white_text_style,
        title_large=white_text_style,
        title_medium=white_text_style,
        title_small=white_text_style
    )


async def mostrar_mensaje(page, mensaje, severidad='info'):
    color_mensaje = {
        'info': ft.colors.BLUE_900,
        'exito': ft.colors.GREEN_900,
        'error': ft.colors.RED_900
    }
    page.snack_bar = ft.SnackBar(
        bgcolor=color_mensaje[severidad],
        content=ft.Text(
            mensaje,
            text_align=ft.TextAlign.CENTER,
            size=26,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.WHITE
        ),
        open=True
    )
    await page.update_async()
