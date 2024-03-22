import unicodedata
import pandas as pd
import datetime

class ComposicionHogarBase:
    def __init__(self, id_victima: int, tipo_relacion: str, respuesta: str, cantidad: int):
        self.id_composicion = None
        self.id_victima = id_victima
        self.respuesta = respuesta
        self.tipo_relacion = self.normalizar_texto(tipo_relacion)
        self.cantidad = cantidad

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


class ComposicionHogar(ComposicionHogarBase):
    pass  # Esta clase usa la estructura base sin cambios


class ComposicionHogarEnJuicio(ComposicionHogarBase):
    def __init__(self, id_victima: int, tipo_relacion: str, respuesta: str, cantidad: int, id_juicio: int):
        super().__init__(id_victima, tipo_relacion, respuesta, cantidad)
        # Nuevo atributo específico para este contexto
        self.id_juicio = id_juicio
