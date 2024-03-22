import unicodedata
import pandas as pd


class Denunciado:
    def __init__(self, id_causa: int,
                 edad: int,
                 sexo: str,
                 nacionalidad: str,
                 nacionalidad_extranjera: str,
                 profesion_oficio: str,
                 estudios: str,
                 caracter_lesion: str,
                 lesiones_descripcion: str,
                 estado_temperancia: str,
                 temperancia_otro: str,
                 temperancia_descripcion: str,
                 otros_antecedentes: str,
                 comuna: str,
                 estado_civil: str,
                 nivel_riesgo: str,
                 vif_numero: float,
                 id_denunciado=None
                 ):
        # Este valor se configuraría automáticamente en un ORM
        self.id_denunciado = id_denunciado
        self.id_causa = id_causa
        self.edad = edad
        self.sexo = self.normalizar_texto(sexo)
        self.nacionalidad = self.normalizar_texto(nacionalidad)
        self.nacionalidad_extranjera = self.normalizar_texto(
            nacionalidad_extranjera)
        self.profesion_oficio = self.normalizar_texto(profesion_oficio)
        self.estudios = self.normalizar_texto(estudios)
        self.caracter_lesion = self.normalizar_texto(caracter_lesion)
        self.lesiones_descripcion = self.normalizar_texto(lesiones_descripcion)
        self.estado_temperancia = self.normalizar_texto(estado_temperancia)
        self.temperancia_otro = self.normalizar_texto(temperancia_otro)
        self.temperancia_descripcion = self.normalizar_texto(
            temperancia_descripcion)
        self.otros_antecedentes = self.normalizar_texto(otros_antecedentes)
        self.comuna = self.normalizar_texto(comuna)
        self.estado_civil = self.normalizar_texto(
            estado_civil)
        self.nivel_riesgo = self.normalizar_texto(nivel_riesgo)
        self.vif_numero = vif_numero
        

    def normalizar_texto(self, texto):
        # Verifica si el texto es None y retorna una cadena vacía si es así
        if texto is None:
            return ""
        elif isinstance(texto, pd.Timestamp):
            # Cambio del formato de fecha a día-mes-año
            texto = texto.strftime('%d-%m-%Y')

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
