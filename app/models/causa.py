import unicodedata
import pandas as pd
import datetime

class Causa:
    def __init__(self,
                 digitador: str,
                 rol_rit: str,
                 fecha_ingreso: str,
                 cartulado: str,
                 procedimiento: str,
                 materia: str,
                 estado_admin: str,
                 ubicacion: str,
                 cuaderno: str,
                 etapa: str,
                 estado_procesal: str,
                 etapa_actual: str,
                 via_ingreso: str,
                 causa_proteccion_abierta: str,
                 causa_penal_abierta: str,
                 id_causa: int = None,  # Añadir Case_ID como un parámetro opcional
                 ):

        self.id_causa = id_causa    # Auto-incrementado en la base de datos
        self.digitador = self.normalizar_texto(digitador)
        self.rol_rit = self.normalizar_texto(rol_rit)
        self.fecha_ingreso = self.normalizar_texto(fecha_ingreso)
        self.cartulado = self.normalizar_texto(cartulado)
        self.procedimiento = self.normalizar_texto(procedimiento)
        self.materia = self.normalizar_texto(materia)
        self.estado_admin = self.normalizar_texto(estado_admin)
        self.ubicacion = self.normalizar_texto(ubicacion)
        self.cuaderno = self.normalizar_texto(cuaderno)
        self.etapa = self.normalizar_texto(etapa)
        self.estado_procesal = self.normalizar_texto(estado_procesal)
        self.etapa_actual = self.normalizar_texto(etapa_actual)
        self.via_ingreso = self.normalizar_texto(via_ingreso)
        self.causa_proteccion_abierta = self.normalizar_texto(causa_proteccion_abierta)
        self.causa_penal_abierta = self.normalizar_texto(causa_penal_abierta)

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