import unicodedata
import pandas as pd
import datetime


class AntecedentePolicial:
    def __init__(self, id_causa, codigo_delito, fecha_delito, hora_delito,
                 lugar_ocurrencia, lugar_ocurrencia_otro, comuna, unidad, cuadrante,
                 ):
        self.id_antecedente_delito = None
        self.id_causa = id_causa
        self.codigo_delito = self.normalizar_texto(codigo_delito)
        self.fecha_delito = self.normalizar_texto(fecha_delito)
        self.hora_delito = self.normalizar_texto(hora_delito)
        self.lugar_ocurrencia = self.normalizar_texto(lugar_ocurrencia)
        self.lugar_ocurrencia_otro = self.normalizar_texto(
            lugar_ocurrencia_otro)
        self.comuna = self.normalizar_texto(comuna)
        self.unidad = self.normalizar_texto(unidad)
        self.cuadrante = self.normalizar_texto(cuadrante)

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
