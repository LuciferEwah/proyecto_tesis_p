import unicodedata
import pandas as pd
import datetime


class Victima:
    def __init__(self,
                 id_causa: int,
                 edad: int,
                 sexo: str,
                 nacionalidad: str,
                 nacionalidad_extranjera: str,
                 profesion_oficio: str,
                 estudios: str,
                 parentesco_acusado: str,
                 parentesco_acusado_otro: str,
                 caracter_lesion: str,
                 descripcion_lesion: str,
                 estado_temperancia: str,
                 estado_temperancia_otro: str,
                 descripcion_temperancia: str,
                 comuna: str,
                 tiempo_relacion: str,
                 estado_civil: str,
                 parentesco_denunciante: str,
                 parentesco_denunciante_otro: str,
                 violencia_patrimonial: str,
                 vic_violencia_economica: str,
                 vic_ayuda_tecnica: str,
                 vic_ayuda_tecnica_tipo: str,
                 vic_deterioro_cognitivo: str,
                 vic_informe_medico: str,
                 vic_num_enfermedades: str,
                 vic_inasistencias_salud: str,
                 vic_informes_social: str,
                 vic_comuna_ingreso:str,
                 listado_enfermedades: str,
                 id_victima=None):

        # Esto se configuraría automáticamente si estás utilizando un ORM con una clave primaria autoincremental.
        self.id_victima = id_victima
        self.id_causa = id_causa
        self.edad = edad
        self.sexo = self.normalizar_texto(sexo)
        self.nacionalidad = self.normalizar_texto(nacionalidad)
        self.nacionalidad_extranjera = self.normalizar_texto(nacionalidad_extranjera)
        self.profesion_oficio = self.normalizar_texto(profesion_oficio)
        self.estudios = self.normalizar_texto(estudios)
        self.parentesco_acusado = self.normalizar_texto(parentesco_acusado)
        self.parentesco_acusado_otro = self.normalizar_texto(parentesco_acusado_otro)
        self.caracter_lesion = self.normalizar_texto(caracter_lesion)
        self.descripcion_lesion = self.normalizar_texto(descripcion_lesion)
        self.estado_temperancia = self.normalizar_texto(estado_temperancia)
        self.estado_temperancia_otro = self.normalizar_texto(estado_temperancia_otro)
        self.descripcion_temperancia = self.normalizar_texto(descripcion_temperancia)
        self.comuna = self.normalizar_texto(comuna)
        self.tiempo_relacion = self.normalizar_texto(tiempo_relacion)
        self.estado_civil = self.normalizar_texto(estado_civil)
        self.parentesco_denunciante = self.normalizar_texto(parentesco_denunciante)
        self.parentesco_denunciante_otro = self.normalizar_texto(parentesco_denunciante_otro) 
        self.violencia_patrimonial = self.normalizar_texto(violencia_patrimonial) # campos nuevos
        self.vic_violencia_economica = self.normalizar_texto(vic_violencia_economica)
        self.vic_ayuda_tecnica = self.normalizar_texto(vic_ayuda_tecnica)
        self.vic_ayuda_tecnica_tipo = self.normalizar_texto(vic_ayuda_tecnica_tipo)
        self.vic_deterioro_cognitivo = self.normalizar_texto(vic_deterioro_cognitivo)
        self.vic_informe_medico = self.normalizar_texto(vic_informe_medico)
        self.vic_num_enfermedades = self.normalizar_texto(vic_num_enfermedades)
        self.vic_inasistencias_salud = self.normalizar_texto(vic_inasistencias_salud)
        self.vic_informes_social = self.normalizar_texto(vic_informes_social)
        self.vic_comuna_ingreso = self.normalizar_texto(vic_comuna_ingreso)
        self.listado_enfermedades = self.normalizar_texto(listado_enfermedades)
        

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
