import unicodedata
import pandas as pd
import datetime


class AudienciaRelaciones:
    def __init__(self, id_audiencia: int,
                 id_victima: int,
                 id_denunciado: int,
                 tipo_relacion: int,
                 victima_representante_legal: str,
                 denunciado_representante_legal: str,
                 denunciante_representante_legal: str):
        # Se configuraría automáticamente si estás utilizando un ORM.
        self.id_audencia_preparatoria_relaciones = None
        self.id_audiencia = id_audiencia
        self.id_victima = id_victima
        self.id_denunciado = id_denunciado
        self.tipo_relacion = tipo_relacion
        self.victima_representante_legal = self.normalizar_texto(
            victima_representante_legal)
        self.denunciado_representante_legal = self.normalizar_texto(
            denunciado_representante_legal)
        self.denunciante_representante_legal = self.normalizar_texto(
            denunciante_representante_legal)

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
