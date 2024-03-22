import unicodedata
import pandas as pd
import datetime

class AudienciaJuicioAntecedentes:
    def __init__(self, id_causa: int,
                 fecha_citacion: str,
                 fecha_realizacion: str,
                 cambio_composicion_hogar: str,
                 suspendido: str,
                 resolucion: str,
                 sentencia: str,
                 salida_colaborativa: str,
                 carabineros_informa_cese_medidas: str,
                 recurso_procesal: str,
                 recurso_procesal_otro: str,
                 abre_causa_cumplimiento: str,
                 causa_cumplimiento_rol_rit: str,
                 solicitan_informes_oficios: str,
                 informes_solicitados_a_quien: str,
                 informes_entregados: str,
                 informes_entregados_cuales: str,
                 informes_pendientes: str,
                 demora_informes: str,
                 suspension_condicional: str,
                 otro_acuerdo_cual: str, 
                 pericia_solicitada: str,
                 pericia_cual: str,
                 pericia_solicitante: str,
                 pericia_resultado: str, 
                 pericia_evaluado: str,
                 medidas_cautelares: str, 
                 medidas_recurso: str
                 ):

        self.id_audiencia_juicio = None
        self.id_causa = id_causa
        self.fecha_citacion = self.normalizar_texto(fecha_citacion)
        self.fecha_realizacion = self.normalizar_texto(fecha_realizacion)
        self.cambio_composicion_hogar = self.normalizar_texto(cambio_composicion_hogar)
        self.suspendido = self.normalizar_texto(suspendido)
        self.resolucion = self.normalizar_texto(resolucion)
        self.sentencia = self.normalizar_texto(sentencia)
        self.salida_colaborativa = self.normalizar_texto(salida_colaborativa)
        self.carabineros_informa_cese_medidas = self.normalizar_texto(carabineros_informa_cese_medidas)
        self.recurso_procesal = self.normalizar_texto(recurso_procesal)
        self.recurso_procesal_otro = self.normalizar_texto(recurso_procesal_otro)
        self.abre_causa_cumplimiento = self.normalizar_texto(abre_causa_cumplimiento)
        self.causa_cumplimiento_rol_rit = self.normalizar_texto(causa_cumplimiento_rol_rit)
        self.solicitan_informes_oficios = self.normalizar_texto(solicitan_informes_oficios)
        self.informes_solicitados_a_quien = self.normalizar_texto(informes_solicitados_a_quien)
        self.informes_entregados = self.normalizar_texto(informes_entregados)
        self.informes_entregados_cuales = self.normalizar_texto(informes_entregados_cuales)
        self.informes_pendientes = self.normalizar_texto(informes_pendientes)
        self.demora_informes = self.normalizar_texto(demora_informes)
        self.suspension_condicional = self.normalizar_texto(suspension_condicional)
        self.otro_acuerdo_cual = self.normalizar_texto(otro_acuerdo_cual)
        self.pericia_solicitada = self.normalizar_texto(pericia_solicitada)
        self.pericia_cual = self.normalizar_texto(pericia_cual)
        self.pericia_solicitante = self.normalizar_texto(pericia_solicitante)
        self.pericia_resultado = self.normalizar_texto(pericia_resultado)
        self.pericia_evaluado = self.normalizar_texto(pericia_evaluado)
        self.medidas_cautelares = self.normalizar_texto(medidas_cautelares)
        self.medidas_recurso = self.normalizar_texto(medidas_recurso)


    def normalizar_texto(self, texto):
        # Verifica si el texto es None y retorna una cadena vacía si es así
        if texto is None:
            return ""
        elif isinstance(texto, pd.Timestamp):
            # Cambio del formato de fecha a día-mes-año
            texto = texto.strftime('%d-%m-%Y')

        elif isinstance(texto, datetime.time):
            # Formatea el tiempo a una cadena en formato HH:MM
            texto = texto.strftime('%H:%M')
        # A partir de aquí, asegúrate de que el texto es una cadena antes de aplicar métodos específicos de cadena
        if isinstance(texto, str):
            # Elimina espacios iniciales y finales
            texto = texto.strip()

            # Reemplaza 'años' por 'anio' específicamente
            texto = texto.replace('años', 'anio')

            # Normaliza el texto para descomponer los caracteres en sus componentes
            texto_normalizado = unicodedata.normalize('NFD', texto)

            # Elimina los diacríticos (tildes) y convierte el texto a minúsculas
            texto_sin_tildes = ''.join(
                c for c in texto_normalizado if unicodedata.category(c) != 'Mn').lower()

            # Reemplaza 'ñ' por 'n' en el resto del texto
            texto_sin_tildes = texto_sin_tildes.replace('ñ', 'n')

            return texto_sin_tildes
        else:
            # Si no es una cadena, simplemente devuelve el valor original
            return texto