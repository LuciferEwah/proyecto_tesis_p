import unicodedata
import pandas as pd
import datetime

class Denunciante:
    def __init__(self,
                 id_causa: int,
                 es_denunciante_victima: bool,
                 es_denunciante_persona_juridica: bool,
                 nombre_persona_juridica: str,
                 edad_denunciante: int,
                 sexo_denunciante: str,
                 nacionalidad_denunciante: str,
                 nacionalidad_extranjera_denunciante: str,
                 profesion_oficio_denunciante: str,
                 estudios_denunciante: str,
                 parentesco_acusado: str,
                 parentesco_acusado_otro: str,
                 caracter_lesion_denunciante: str,
                 descripcion_lesion_denunciante: str,
                 estado_temperancia_denunciante: str,
                 estado_temperancia_denunciante_otro: str,
                 descripcion_temperancia_denunciante: str,
                 comuna: str,
                 estado_civil: str):

        # La ID del denunciante se configuraría automáticamente si estás utilizando un ORM con una clave primaria autoincremental.
        self.tipo_relacion = None
        self.id_causa = id_causa
        self.es_denunciante_victima = self.normalizar_texto(
            es_denunciante_victima)
        self.es_denunciante_persona_juridica = self.normalizar_texto(
            es_denunciante_persona_juridica)
        self.nombre_persona_juridica = self.normalizar_texto(
            nombre_persona_juridica)
        self.edad_denunciante = edad_denunciante
        self.sexo_denunciante = self.normalizar_texto(sexo_denunciante)
        self.nacionalidad_denunciante = self.normalizar_texto(
            nacionalidad_denunciante)
        self.nacionalidad_extranjera_denunciante = self.normalizar_texto(
            nacionalidad_extranjera_denunciante)
        self.profesion_oficio_denunciante = self.normalizar_texto(
            profesion_oficio_denunciante)
        self.estudios_denunciante = self.normalizar_texto(estudios_denunciante)
        self.parentesco_acusado = self.normalizar_texto(parentesco_acusado)
        self.parentesco_acusado_otro = self.normalizar_texto(
            parentesco_acusado_otro)
        self.caracter_lesion_denunciante = self.normalizar_texto(
            caracter_lesion_denunciante)
        self.descripcion_lesion_denunciante = self.normalizar_texto(
            descripcion_lesion_denunciante)
        self.estado_temperancia_denunciante = self.normalizar_texto(
            estado_temperancia_denunciante)
        self.descripcion_temperancia_denunciante = self.normalizar_texto(
            descripcion_temperancia_denunciante)
        self.estado_temperancia_denunciante_otro = self.normalizar_texto(
            estado_temperancia_denunciante_otro)
        self.comuna = self.normalizar_texto(comuna)
        self.estado_civil = self.normalizar_texto(estado_civil)

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
