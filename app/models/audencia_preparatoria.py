import unicodedata
import pandas as pd
import datetime

class AudienciaPreparatoria:
    def __init__(self,
                 id_causa: int,
                 fecha_citacion: str,
                 fecha_realizacion: str,
                 suspension_anterior: str,
                 solicita_informes_oficios: str,
                 resolucion: str,
                 salida_colaborativa: str,
                 otras_observaciones: str,
                 informes_solicitados_a_quien :str,
                 informes_entregados: str,
                 informes_entregados_cuales: str,
                 informes_pendientes: str,  
                 demora_entrega_informes: str,
                 pericia_solicitada:str,
                 pericia_cual: str, 
                 pericia_solicitante: str):
        self.id_audiencia_preparatoria = None
        self.id_causa = id_causa
        self.fecha_citacion = self.normalizar_texto(fecha_citacion)
        self.fecha_realizacion = self.normalizar_texto(fecha_realizacion)
        self.suspension_anterior = self.normalizar_texto(suspension_anterior)
        self.solicita_informes_oficios = self.normalizar_texto(solicita_informes_oficios)
        self.resolucion = self.normalizar_texto(resolucion)
        self.salida_colaborativa = self.normalizar_texto(salida_colaborativa)
        self.informes_solicitados_a_quien = self.normalizar_texto(informes_solicitados_a_quien)
        self.informes_entregados = self.normalizar_texto(informes_entregados)
        self.salida_colaborativa = self.normalizar_texto(salida_colaborativa)
        self.otras_observaciones = self.normalizar_texto(otras_observaciones)
        self.informes_entregados_cuales = self.normalizar_texto(informes_entregados_cuales)
        self.informes_pendientes = self.normalizar_texto(informes_pendientes)
        self.demora_entrega_informes = self.normalizar_texto(demora_entrega_informes)
        self.pericia_solicitada = self.normalizar_texto(pericia_solicitada)
        self.pericia_cual = self.normalizar_texto(pericia_cual)
        self.pericia_solicitante = self.normalizar_texto(pericia_solicitante)
        
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
