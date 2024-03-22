# main.py
import flet as ft
from screen.login import LoginScreen
from screen.dashboard import DashboardScreen
from screen.configuracion import ConfigurationScreen
from screen.graficos import GraphScreen
from db.database import BaseDeDatos
from widgets.nav import NavigationRailClass
from screen.forms_causa import ScreenFormsCausa
from screen.froms_victima import ScreenFormsVictima
from screen.froms_home_composition import ScreenFormsHomeComposition
from screen.froms_denounced import ScreenFormsDenunciado
from screen.froms_background_denounced import ScreenFormsBackgroundDenounced
from screen.froms_denounced_vif_risk_indicators import ScreenFormsVifRiskIndicators
from screen.froms_denunciantes import ScreenFormsDenunciante
from screen.audencias import ScreenFormsAudencias
from screen.froms_preparatory_hearing import ScreenFormsAudienciaPreparatoria
from screen.froms_preparatory_hearing_involved import ScreenPreparatoryHearingInvolved
from screen.froms_precautionary_measures_preparatory_hearing import ScreenPreparatoriaMedidasCautelares
from screen.froms_trial_hearing import ScreenFormsJuicio
from screen.froms_trial_hearing_involved import ScreenTrialHearingInvolved
from screen.froms_trial_hearing_home_composicion import ScreenCompositionHogarEnJuicio
from screen.froms_trial_interim_measures import ScreenJuicioMedidasCautelares
from screen.policial import ScreenInformacionPolicial
from screen.froms_police import ScreenFormsPolice
from screen.froms_police_measures import ScreenMedidasPoliciales
from screen.rules_association import RulesAssociantionScreen
from screen.tree_models import TreeModelsScreen
from screen.admin import Admin
from widgets.utils import *
import logging


logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

async def main(page: ft.Page):
    page.window_maximized = True 

    custom_color_scheme = get_custom_color_scheme()
    text_theme = get_text_theme()

    page.theme = ft.Theme(
        color_scheme_seed="blue",
        text_theme=text_theme,
        color_scheme=custom_color_scheme,
        primary_text_theme=text_theme,
    )

    page.theme_mode = ft.ThemeMode.DARK

    page.window_min_width = page.window_width
    page.window_min_height = page.window_height
    selected_causa = None
    selected_causa_id = None
    selected_victima = None
    selected_victima_id = None
    selected_home_composition = None
    selected_denunciado_id = None
    selected_denunciado = None
    selected_background_denounced = None
    selected_vif_denounced = None
    selected_denunciantes = None
    selected_preparatory_hearing = None
    selected_preparatory_hearing_id = None
    selected_home_preparatory_hearing_involved = None
    selected_home_preparatory_hearing_involved_id = None
    selected_medida_cautelar = None
    selected_medida_cautelar_id = None
    selected_trial_hearing = None
    selected_trial_hearing_id = None
    selected_juicio_involved = None
    selected_juicio_involved_id = None
    selected_juicio_composicion_hogar = None
    selected_juicio_composicion_hogar_id = None
    selected_juicio_interim_measures = None
    selected_juicio_interim_measures_id = None
    selected_policia_report = None
    selected_policia_report_id = None
    selected_medida_policial = None
    selected_medida_policial_id = None

    async def on_medida_policial_selected_callback(medida_policial_info):
        nonlocal selected_medida_policial
        nonlocal selected_medida_policial_id
        selected_medida_policial_id, selected_medida_policial_data = medida_policial_info
        selected_medida_policial = selected_medida_policial_data

    def get_selected_medida_policial():
        return selected_medida_policial

    async def on_policia_report_selected_callback(policia_report_info):
        nonlocal selected_policia_report
        nonlocal selected_policia_report_id
        selected_policia_report_id, selected_policia_report_data = policia_report_info
        selected_policia_report = selected_policia_report_data

    def get_selected_policia_report():
        return selected_policia_report

    def get_policia_report_id():
        return selected_policia_report_id

    async def on_home_trial_interim_measures_callback(interim_measures_info):
        nonlocal selected_juicio_interim_measures
        nonlocal selected_juicio_interim_measures_id
        selected_juicio_interim_measures_id, selected_juicio_interim_measures_data = interim_measures_info
        selected_juicio_interim_measures = selected_juicio_interim_measures_data

    def get_juicio_interim_measures_data():
        return selected_juicio_interim_measures

    async def on_home_trial_composicion_hogar_callback(composicion_hogar_info):
        nonlocal selected_juicio_composicion_hogar
        nonlocal selected_juicio_composicion_hogar_id
        selected_juicio_composicion_hogar_id, selected_juicio_composicion_hogar_data = composicion_hogar_info
        selected_juicio_composicion_hogar = selected_juicio_composicion_hogar_data

    def get_composicion_hogar_en_juicio_data():
        return selected_juicio_composicion_hogar

    async def on_selected_juicio_involved(juicio_involved_info):
        nonlocal selected_juicio_involved
        nonlocal selected_juicio_involved_id
        selected_juicio_involved_id, selected_juicio_involved_data = juicio_involved_info
        selected_juicio_involved = selected_juicio_involved_data

    # Funciones para obtener los datos y el ID de la relación en la audiencia de juicio seleccionada
    def get_juicio_involved_hearing_data():
        return selected_juicio_involved

    async def on_selected_trial_hearing(trial_hearing_info):
        nonlocal selected_trial_hearing
        nonlocal selected_trial_hearing_id
        selected_trial_hearing_id, selected_trial_hearing_data = trial_hearing_info
        selected_trial_hearing = selected_trial_hearing_data

    def get_trial_hearing_data():
        return selected_trial_hearing

    def get_trial_hearing_id():
        return selected_trial_hearing_id

    async def on_selected_medida_cautelar(medida_cautelar_info):
        nonlocal selected_medida_cautelar_id
        nonlocal selected_medida_cautelar

        if medida_cautelar_info is not None:
            selected_medida_cautelar_id, selected_medida_cautelar_data = medida_cautelar_info
            selected_medida_cautelar = selected_medida_cautelar_data

    def get_selected_medida_cautelar_data():
        return selected_medida_cautelar

    async def on_selected_preparatory_hearing_involved(preparatory_hearing_involved_info):
        nonlocal selected_home_preparatory_hearing_involved_id
        nonlocal selected_home_preparatory_hearing_involved

        selected_home_preparatory_hearing_involved_id, selected_preparatory_involved_hearing_data = preparatory_hearing_involved_info
        selected_home_preparatory_hearing_involved = selected_preparatory_involved_hearing_data

    def get_preparatory_involved_hearing_data():
        return selected_home_preparatory_hearing_involved

    async def on_selected_preparatory_seleted(preparatory_hearing_info):
        nonlocal selected_preparatory_hearing
        nonlocal selected_preparatory_hearing_id
        get_id_preparatory_hearing, selected_preparatory_hearing_data = preparatory_hearing_info
        selected_preparatory_hearing = selected_preparatory_hearing_data
        selected_preparatory_hearing_id = get_id_preparatory_hearing

    def get_preparatory_hearing_data():
        return selected_preparatory_hearing

    def get_preparatory_hearing_id():
        return selected_preparatory_hearing_id

    async def on_selected_denunciantes_selected(vif_denunciantes_info):
        nonlocal selected_denunciantes
        # Asumiendo que denunciado_background_info es una tupla donde el primer elemento es el ID
        selected_background_denounced_id, vif_denunciantes_data = vif_denunciantes_info
        selected_denunciantes = vif_denunciantes_data

    def get_denunciantes_selected():
        return selected_denunciantes

    async def on_selected_vif_denounced_selected(vif_denounced_info):
        nonlocal selected_vif_denounced
        # Asumiendo que denunciado_background_info es una tupla donde el primer elemento es el ID
        selected_background_denounced_id, vif_denounced_data = vif_denounced_info
        selected_vif_denounced = vif_denounced_data

    def get_id_data_indicadores_riesgo_vif():
        return selected_vif_denounced

    async def on_background_denunciado_selected(denunciado_background_info):
        nonlocal selected_background_denounced
        # Asumiendo que denunciado_background_info es una tupla donde el primer elemento es el ID
        selected_background_denounced_id, denunciado_background_data = denunciado_background_info
        selected_background_denounced = denunciado_background_data

    def get_background_denunciado_selected():
        return selected_background_denounced

    async def on_denunciado_selected(denunciado_info):
        nonlocal selected_denunciado_id, selected_denunciado
        selected_denunciado_id, selected_denunciado = denunciado_info

    def get_denunciado_id():
        return selected_denunciado_id

    def get_data_denunciado():
        return selected_denunciado

    async def on_home_composition(home_composition_info):
        nonlocal selected_home_composition
        selected_home_composition = home_composition_info

    def get_id_data_home_composition():
        return selected_home_composition

    async def on_victima_selected(victima_info):
        nonlocal selected_victima_id, selected_victima
        selected_victima_id, victima_data = victima_info
        selected_victima = victima_data

    def get_victima_id():
        return selected_victima_id

    def get_id_data_victima():
        return selected_victima

    def on_causa_selected(causa_info):
        nonlocal selected_causa_id, selected_causa
        selected_causa_id, causa_data = causa_info  # Desempaquetar la tupla

        selected_causa = causa_data

    def get_data_causa():
        return selected_causa

    def get_id_data_causa():
        return selected_causa_id

    db = BaseDeDatos()  # Instancia de la base de datos
    await db.initialize_database()  # Se inicializa

    async def handle_route_change(route):  # Fución retorna la pagina actual
        await page.go_async(route)
        # print(page.route)

    destinations_1 = [
        {"route": "/PaginaPrincipal", "icon": ft.icons.STAR, "label": "Principal"},
        {"route": "/Graficos", "icon": ft.icons.STACKED_BAR_CHART, "label": "Gráficos"},
        {"route": "/AnalisisArbolDecision", "icon": ft.icons.ACCOUNT_TREE_OUTLINED, "label": "Análisis con Árbol de Decisión"},
        {"route": "/AnalisisReglasAsociacion", "icon": ft.icons.DATASET_OUTLINED, "label": "Análisis con Reglas de Asociación"},
        {"route": "/Configuracion", "icon": ft.icons.SETTINGS, "label": "Configuración"}
    ]
    nav_rail_class = NavigationRailClass(
        handle_route_change, destinations_1, page)

    destinations_2 = [
        {"route": "/formulario_causa",
            "icon": ft.icons.MANAGE_ACCOUNTS, "label": "Personas"},
        {"route": "/InformacionPolicial",
            "icon": ft.icons.LOCAL_POLICE_OUTLINED, "label": "Policial"},
        {"route": "/Audencias",
            "icon": ft.icons.BUSINESS_CENTER_OUTLINED, "label": "Audiencias"},
    ]
    nav_rail_class_2 = NavigationRailClass(
        handle_route_change, destinations_2, page, show_trailing=True)

    async def route_change(e):
        if page.route == '/inicio':
            page.title = "Inicio"
            login_screen = LoginScreen(db)
            page.views.append(ft.View('/inicio', controls=[login_screen],
                                      horizontal_alignment='center',
                                      vertical_alignment='center',
                                      bgcolor='#1f262f')
                              )
        elif page.route == '/admin':
            page.title = "Admin"
            admin_screen = Admin(db,mostrar_mensaje)
            page.views.append(ft.View('/admin', controls=[admin_screen],
                                    horizontal_alignment='center',
                                    vertical_alignment='center',
                                    bgcolor='#1f262f')
                            )
        elif page.route == '/PaginaPrincipal':
            page.title = 'Pagina Principal'
            nav_rail_class.set_selected_index(0)
            if not any(view.route == '/PaginaPrincipal' for view in page.views):
                global dashboard_screen
                dashboard_screen = DashboardScreen(
                    db, handle_route_change, nav_rail_class, on_causa_selected, page)
                page.views.append(ft.View('/PaginaPrincipal',
                                          controls=[dashboard_screen],
                                          ))
            await page.update_async()

        elif page.route == '/Graficos':
            page.title = 'Graficos'
            nav_rail_class.set_selected_index(1)
            graph_screen = GraphScreen(db, page,
                handle_route_change, nav_rail_class)
            page.views.append(ft.View('/Graficos',
                                      controls=[graph_screen],
                                      scroll=ft.ScrollMode.ADAPTIVE))  # Pasando la función como argumento
            await page.update_async()

        elif page.route == '/AnalisisArbolDecision':
            page.title = 'Análisis con Árbol de Decisión'
            nav_rail_class.set_selected_index(2)
            if not any(view.route == '/AnalisisArbolDecision' for view in page.views):
                tree_screen = TreeModelsScreen(db, page,
                    handle_route_change, nav_rail_class)
                page.views.append(
                    ft.View(
                        '/AnalisisArbolDecision',
                        controls=[tree_screen],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )
            await page.update_async()

        elif page.route == '/AnalisisReglasAsociacion':
            page.title = 'Análisis de Reglas de Asociación'
            nav_rail_class.set_selected_index(3)
            if not any(view.route == '/AnalisisReglasAsociacion' for view in page.views):
                rules_screen = RulesAssociantionScreen(db, page,
                    handle_route_change, nav_rail_class)
                page.views.append(
                    ft.View(
                        '/AnalisisReglasAsociacion',
                        controls=[rules_screen],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )
            await page.update_async()


        elif page.route == '/Configuracion':
            page.title = 'Configuración'
            nav_rail_class.set_selected_index(4)
            configuration_scren = ConfigurationScreen(db, page,
                                                      handle_route_change, nav_rail_class, mostrar_mensaje)
            page.views.append(ft.View('/Configuracion',
                                      controls=[configuration_scren]))  # Pasando la función como argumento
            await page.update_async()

        elif page.route == '/formulario_causa':
            page.title = 'Formulario de Causa'
            # Asumiendo que esta es la posición correcta en el rail
            nav_rail_class_2.set_selected_index(0)
            if not any(view.route == '/formulario_causa' for view in page.views):
                global screen_forms_causa
                screen_forms_causa = ScreenFormsCausa(
                    db, get_data_causa(), page, handle_route_change, nav_rail_class_2, dashboard_screen.initialize_async_data, on_causa_selected, on_victima_selected, on_denunciado_selected, on_selected_denunciantes_selected, mostrar_mensaje)

                page.views.append(
                    ft.View(
                        '/formulario_causa',
                        controls=[screen_forms_causa],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )
            await page.update_async()

        elif page.route == '/formulario_victima':
            page.title = 'Formulario de Datos de la Víctima'
            global from_victima_scren
            from_victima_scren = ScreenFormsVictima(
                db, page, get_id_data_victima(), on_home_composition, screen_forms_causa.initialize_async_data, dashboard_screen.initialize_async_data, selected_causa_id, mostrar_mensaje)
            page.views.append(
                ft.View(
                    'Formulario de Datos de la Víctima',
                    controls=[from_victima_scren],
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
            )
            await page.update_async()

        elif page.route == '/formulario_composicion_hogar':
            page.title = 'Formulario de Composición Hogar'
            composicion_familiar_screen = ScreenFormsHomeComposition(
                db, page, get_id_data_home_composition(), get_victima_id(), from_victima_scren.initialize_async_data, mostrar_mensaje)
            page.views.append(
                ft.View(
                    'Formulario de Composición Hogar',
                    controls=[composicion_familiar_screen],
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
            )
            await page.update_async()

        elif page.route == '/formulario_denunciado':
            page.title = 'Formulario del denunciado'
            global denunciado_screen
            denunciado_screen = ScreenFormsDenunciado(
                db, get_data_denunciado(), page, selected_causa_id, screen_forms_causa.initialize_async_data, dashboard_screen.initialize_async_data, on_background_denunciado_selected, on_selected_vif_denounced_selected, mostrar_mensaje)
            page.views.append(
                ft.View(
                    'Formulario del denunciado',
                    controls=[denunciado_screen],
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
            )
            await page.update_async()

        elif page.route == '/formulario_antecedentes_denunciado':
            page.title = 'Antecedentes del denunciado'
            background_denounced_screen = ScreenFormsBackgroundDenounced(
                db, page, get_background_denunciado_selected(), get_denunciado_id(), denunciado_screen.initialize_async_data, mostrar_mensaje)
            page.views.append(
                ft.View(
                    'Antecedentes del denunciado',
                    controls=[background_denounced_screen],
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
            )
            await page.update_async()

        elif page.route == '/formulario_indicadores_riesgo_vif':
            page.title = 'Indicadores de Riesgo VIF del Denunciado'
            indicadores_riesgo_vif_screen = ScreenFormsVifRiskIndicators(
                db, page, get_id_data_indicadores_riesgo_vif(), get_denunciado_id(), denunciado_screen.initialize_async_data, mostrar_mensaje)
            page.views.append(
                ft.View(
                    'Indicadores de Riesgo VIF del Denunciado',
                    controls=[indicadores_riesgo_vif_screen],
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
            )
            await page.update_async()

        elif page.route == '/formulario_denunciante':
            page.title = 'Formulario de Denunciantes'
            screen_forms_denunciante = ScreenFormsDenunciante(
                db, page, get_denunciantes_selected(
                ), screen_forms_causa.initialize_async_data, selected_causa_id, mostrar_mensaje
            )
            page.views.append(
                ft.View(
                    'Formulario de Denunciantes',
                    controls=[screen_forms_denunciante],
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
            )
            await page.update_async()

        elif page.route == '/InformacionPolicial':
            page.title = 'Información Policial'
            nav_rail_class_2.set_selected_index(1)
            if not any(view.route == '/InformacionPolicial' for view in page.views):
                global screen_informacion_policial
                screen_informacion_policial = ScreenInformacionPolicial(handle_route_change, nav_rail_class_2, db, page, get_id_data_causa(), on_policia_report_selected_callback, mostrar_mensaje
                                                                        )
                page.views.append(
                    ft.View(
                        '/InformacionPolicial',
                        controls=[screen_informacion_policial],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )
            await page.update_async()

        elif page.route == '/AntecedentesPoliciales':
            page.title = 'Antecedentes Policiales'
            # Verifica si la vista ya existe en la página
            if not any(view.route == '/AntecedentesPoliciales' for view in page.views):
                global screen_antecedentes_policiales
                screen_antecedentes_policiales = ScreenFormsPolice(
                    db, page, get_selected_policia_report(
                    ), get_id_data_causa(), on_medida_policial_selected_callback, screen_informacion_policial.initialize_async_data, mostrar_mensaje
                )
                page.views.append(
                    ft.View(
                        '/AntecedentesPoliciales',
                        controls=[screen_antecedentes_policiales],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )
            await page.update_async()

        elif page.route == '/MedidasPoliciales':
            page.title = 'Medidas Policiales'
            # Verifica si la vista ya existe en la página
            if not any(view.route == '/MedidasPoliciales' for view in page.views):
                screen_medidas_policiales = ScreenMedidasPoliciales(
                    db, page, get_selected_medida_policial(), get_policia_report_id(
                    ), screen_antecedentes_policiales.initialize_async_data, mostrar_mensaje
                )
                page.views.append(
                    ft.View(
                        '/MedidasPoliciales',
                        controls=[screen_medidas_policiales],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )
            await page.update_async()

        elif page.route == '/Audencias':
            page.title = 'Audencias'
            nav_rail_class_2.set_selected_index(2)
            if not any(view.route == '/Audencias' for view in page.views):
                global screen_forms_Audencia
                screen_forms_Audencia = ScreenFormsAudencias(
                    handle_route_change, nav_rail_class_2, db, page, get_id_data_causa(),
                    on_selected_preparatory_seleted, on_selected_trial_hearing)
                page.views.append(
                    ft.View(
                        '/Audencias',
                        controls=[screen_forms_Audencia],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )
            await page.update_async()

        elif page.route == '/AudenciaPreparatoria':
            page.title = 'Audencia Preparatoria'
            if not any(view.route == '/AudenciaPreparatoria' for view in page.views):
                global screen_forms_audencia_preparatoria
                screen_forms_audencia_preparatoria = ScreenFormsAudienciaPreparatoria(
                    db, page, get_preparatory_hearing_data(), on_selected_preparatory_hearing_involved, on_selected_medida_cautelar, get_id_data_causa(), screen_forms_Audencia.initialize_async_data, mostrar_mensaje)
                page.views.append(
                    ft.View(
                        '/AudenciaPreparatoria',
                        controls=[screen_forms_audencia_preparatoria],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )
            await page.update_async()

        elif page.route == '/AudenciaPreparatoriaInvolucrados':
            page.title = 'Involucrados en la Audiencia Preparatoria'
            screen_forms_audencia_preparatoria_involved = ScreenPreparatoryHearingInvolved(
                db, page, get_preparatory_involved_hearing_data(), get_preparatory_hearing_id(), get_id_data_causa(), screen_forms_audencia_preparatoria.initialize_async_data, mostrar_mensaje)
            page.views.append(
                ft.View(
                    '/AudenciaPreparatoriaInvolucrados',
                    controls=[screen_forms_audencia_preparatoria_involved],
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
            )
            await page.update_async()

        elif page.route == '/AudenciaPreparatoriaMedidasCautelares':
            page.title = 'Involucrados en la Audiencia Preparatoria'

            # Verifica si ya existe una vista con la ruta '/AudenciaPreparatoriaInvolucrados'
            if not any(view.route == '/AudenciaPreparatoriaMedidasCautelares' for view in page.views):

                screen_forms_measures_preparatory_hearing = ScreenPreparatoriaMedidasCautelares(
                    db, page, get_selected_medida_cautelar_data(), get_preparatory_hearing_id(
                    ), screen_forms_audencia_preparatoria.initialize_async_data, mostrar_mensaje
                )
                page.views.append(
                    ft.View(
                        '/AudenciaPreparatoriaMedidasCautelares',
                        controls=[screen_forms_measures_preparatory_hearing],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )

            await page.update_async()

        elif page.route == '/AudienciaJuicioAntecedentes':
            page.title = 'Audiencia de Juicio Antecedentes'
            if not any(view.route == '/AudienciaJuicioAntecedentes' for view in page.views):
                global screen_forms_juicio
                screen_forms_juicio = ScreenFormsJuicio(
                    db, page, get_trial_hearing_data(), get_id_data_causa(
                    ), on_selected_juicio_involved, on_home_trial_composicion_hogar_callback, on_home_trial_interim_measures_callback, screen_forms_Audencia.initialize_async_data, mostrar_mensaje
                )
                page.views.append(
                    ft.View(
                        '/AudienciaJuicioAntecedentes',
                        controls=[screen_forms_juicio],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )

            await page.update_async()

        elif page.route == '/AudienciaJuicioInvolucrados':
            page.title = 'Involucrados en la Audiencia de Juicio'
            if not any(view.route == '/AudienciaJuicioInvolucrados' for view in page.views):
                global screen_forms_juicio_involved
                screen_forms_juicio_involved = ScreenTrialHearingInvolved(
                    db, page, get_juicio_involved_hearing_data(
                    ), get_trial_hearing_id(), get_id_data_causa(),
                    screen_forms_juicio.initialize_async_data, mostrar_mensaje
                )
                page.views.append(
                    ft.View(
                        '/AudienciaJuicioInvolucrados',
                        controls=[screen_forms_juicio_involved],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )

            await page.update_async()

        elif page.route == '/ComposicionHogarEnJuicio':
            page.title = 'Composición del Hogar en Juicio'
            # Verifica si la vista ya existe en la página
            if not any(view.route == '/ComposicionHogarEnJuicio' for view in page.views):
                # Si no existe, crea la vista y la agrega a las vistas de la página
                global screen_composition_hogar_en_juicio
                screen_composition_hogar_en_juicio = ScreenCompositionHogarEnJuicio(
                    db, page, get_composicion_hogar_en_juicio_data(
                    ), get_trial_hearing_id(), get_id_data_causa(),
                    screen_forms_juicio.initialize_async_data, mostrar_mensaje
                )
                page.views.append(
                    ft.View(
                        '/ComposicionHogarEnJuicio',
                        controls=[screen_composition_hogar_en_juicio],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )
            await page.update_async()

        elif page.route == '/MedidasCautelaresJuicio':
            page.title = 'Medidas Cautelares del Juicio'
            # Verifica si la vista ya existe en la página
            if not any(view.route == '/MedidasCautelaresJuicio' for view in page.views):
                global screen_medidas_cautelares_juicio
                screen_medidas_cautelares_juicio = ScreenJuicioMedidasCautelares(
                    db, page, get_juicio_interim_measures_data(), get_trial_hearing_id(),
                    screen_forms_juicio.initialize_async_data, mostrar_mensaje
                )
                page.views.append(
                    ft.View(
                        '/MedidasCautelaresJuicio',
                        controls=[screen_medidas_cautelares_juicio],
                        scroll=ft.ScrollMode.ADAPTIVE
                    ),
                )
                
            await page.update_async()



    page.on_route_change = route_change  # Ruta de inicios
    
    await page.go_async('/PaginaPrincipal')

if __name__ == '__main__':
    ft.app(target=main, assets_dir="assets")