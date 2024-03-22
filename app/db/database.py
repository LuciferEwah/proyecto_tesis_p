import bcrypt
import aiosqlite
import asyncio
import time
import os
from models.causa import Causa
from datetime import datetime
from models.victima import Victima
from models.composicion_hogar import ComposicionHogar, ComposicionHogarEnJuicio
from models.denunciado import Denunciado
from models.antecedentes_denunciado import AntecedentesDenunciado
from models.denunciado_vif import DenunciadoIndicadoresRiesgoVIF
from models.denunciantes import Denunciante
from models.audencia_preparatoria import AudienciaPreparatoria
from models.audencia_relaciones import AudienciaRelaciones
from models.medida_cautelar import MedidaCautelar
from models.audencia_juicio_antecedentes import AudienciaJuicioAntecedentes
from models.antecedente_policial import AntecedentePolicial
from models.medida_cautelar import MedidaCautelar, MedidaCautelarEspecial
import math

class BaseDeDatos():
    def __init__(self, db_name='LIACDD.db'):
        self.db_name = db_name

        # Obtiene la ruta al directorio "Documentos" del usuario actual
        documents_dir = os.path.join(os.path.expanduser('~'), 'Documents')
        # Ruta a la carpeta "LIACDD" dentro de "Documentos"
        liacdd_dir = os.path.join(documents_dir, 'LIACDD')
        # Ruta completa de la base de datos
        self.db_name = os.path.join(liacdd_dir, db_name)

        if not os.path.exists(liacdd_dir):
            os.makedirs(liacdd_dir)

        # appdata_dir = os.path.join(os.getenv('APPDATA'), 'LIACDD')
        # self.db_name = os.path.join(appdata_dir, db_name)

        # Si la carpeta "LIACDD" en "AppData" no existe, la crea
        # if not os.path.exists(appdata_dir):
        #    os.makedirs(appdata_dir)

    async def add_user(self, user: str, password: str):
        task = asyncio.create_task(self._add_user(user, password))
        await task

    async def user_verification(self, usuario: str, password: str):
        task = asyncio.create_task(self._user_verification(usuario, password))
        return await task

    async def initialize_database(self):
        task = asyncio.create_task(self._initialize_database())
        await task

    async def _initialize_database(self):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.cursor()
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY,
                    usuario TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    failed_attempts INTEGER DEFAULT 0,
                    lockout_until INTEGER DEFAULT NULL
                );
            ''')
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS causa (
                    id_causa INTEGER primary key,
                    digitador TEXT,
                    rol_rit TEXT,
                    fecha_ingreso TEXT,
                    cartulado TEXT,
                    procedimiento TEXT,
                    materia TEXT,
                    estado_admin TEXT,
                    ubicacion TEXT,
                    cuaderno TEXT,
                    etapa TEXT,
                    estado_procesal TEXT,
                    etapa_actual TEXT,
                    via_ingreso TEXT,
                    causa_proteccion_abierta TEXT,
                    causa_penal_abierta TEXT    
                );
            ''')

            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS victima (
                    id_victima INTEGER PRIMARY KEY,
                    id_causa INTEGER NOT NULL,
                    edad INTEGER,
                    sexo TEXT,
                    nacionalidad TEXT,
                    nacionalidad_extranjera TEXT,
                    profesion_oficio TEXT,
                    estudios TEXT,
                    parentesco_acusado TEXT,
                    parentesco_acusado_otro TEXT,
                    caracter_lesion TEXT,
                    descripcion_lesion TEXT,
                    estado_temperancia TEXT,
                    estado_temperancia_otro TEXT,
                    descripcion_temperancia TEXT,
                    comuna TEXT,
                    tiempo_relacion TEXT,
                    estado_civil TEXT,
                    parentesco_denunciante TEXT,
                    parentesco_denunciante_otro TEXT,
                    violencia_patrimonial TEXT, --desde aqui campos nuevos
                    violencia_economica TEXT,
                    ayuda_tecnica TEXT,
                    ayuda_tecnica_tipo TEXT,
                    deterioro_cognitivo TEXT,
                    informe_medico TEXT,
                    num_enfermedades TEXT,
                    inasistencias_salud TEXT,
                    informes_social TEXT,
                    comuna_ingreso TEXT,
                    listado_enfermedades TEXT,
                    FOREIGN KEY (id_causa) REFERENCES causa(id_causa)
                ); 
            ''')
            await cursor.execute('''
            CREATE TABLE IF NOT EXISTS composicion_hogar (
                id_composicion INTEGER PRIMARY KEY,
                id_victima INTEGER NOT NULL,
                tipo_relacion TEXT,
                respuesta TEXT,
                cantidad INTEGER,
                FOREIGN KEY (id_victima) REFERENCES victima(id_victima)
            );
            ''')
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS denunciado (
                    id_denunciado INTEGER PRIMARY KEY,
                    id_causa INTEGER NOT NULL,
                    edad INTEGER,
                    sexo TEXT,
                    nacionalidad TEXT,
                    nacionalidad_Extranjera TEXT,
                    profesion_oficio TEXT,
                    estudios TEXT,
                    caracter_lesion TEXT,
                    lesiones_descripcion TEXT,
                    estado_temperancia TEXT,
                    temperancia_otro TEXT,
                    temperancia_descripcion TEXT,
                    otros_antecedentes TEXT,
                    comuna TEXT,
                    estado_civil TEXT,  
                    nivel_riesgo TEXT,
                    vif_numero INTEGER,
                    FOREIGN KEY (ID_Causa) REFERENCES causa(ID_Causa) 
                );
            ''')
            await cursor.execute('''
            CREATE TABLE IF NOT EXISTS denunciado_antecedentes (
                id_antecedente INTEGER PRIMARY KEY,
                id_denunciado INTEGER NOT NULL,
                tipo_antecedente TEXT,
                descripcion TEXT,
                FOREIGN KEY (id_denunciado) REFERENCES denunciado(id_denunciado)
            );
            ''')
            await cursor.execute('''
            CREATE TABLE IF NOT EXISTS denunciado_indicadores_riesgo_vif (
                id_riesgo_vif INTEGER PRIMARY KEY,
                id_denunciado INTEGER NOT NULL,
                descripcion_indicador TEXT,
                respuesta TEXT,
                FOREIGN KEY (id_denunciado) REFERENCES denunciado(id_denunciado)
            );
            ''')
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS denunciantes (
                    tipo_relacion INTEGER PRIMARY KEY,
                    id_causa INTEGER,
                    es_denunciante_victima TEXT,
                    es_denunciante_persona_juridica TEXT,
                    nombre_persona_juridica TEXT,
                    edad_denunciante INTEGER,
                    sexo_denunciante TEXT,
                    nacionalidad_denunciante TEXT,
                    nacionalidad_extranjera_denunciante TEXT,
                    profesion_oficio_denunciante TEXT,
                    estudios_denunciante TEXT,
                    parentesco_acusado TEXT,
                    parentesco_acusado_otro TEXT,
                    caracter_lesion_denunciante TEXT,
                    descripcion_lesion_denunciante TEXT,
                    estado_temperancia_denunciante TEXT,
                    estado_temperancia_denunciante_otro TEXT,
                    descripcion_temperancia_denunciante TEXT,
                    comuna TEXT,
                    estado_civil TEXT,
                    FOREIGN KEY (id_causa) REFERENCES causa(id_causa)
                );
            ''')
            await cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS audiencia_preparatoria (
                    id_audiencia_preparatoria INTEGER PRIMARY KEY,
                    id_causa INTEGER UNIQUE,
                    fecha_citacion TEXT,
                    fecha_realizacion TEXT,
                    suspension_anterior TEXT,  
                    solicita_informes_oficios TEXT,  
                    resolucion TEXT,
                    salida_colaborativa TEXT, 
                    otras_observaciones TEXT,
                    informes_solicitados_a_quien TEXT,
                    informes_entregados TEXT,
                    informes_entregados_cuales TEXT,
                    informes_pendientes TEXT,
                    demora_entrega_informes TEXT,
                    pericia_solicitada TEXT,
                    pericia_cual TEXT,
                    pericia_solicitante TEXT,
                    FOREIGN KEY (id_causa) REFERENCES causa(id_causa)
                );
            ''')
            await cursor.execute('''
            CREATE TABLE IF NOT EXISTS audiencia_preparatoria_relaciones (
                id_audencia_preparatoria_relaciones INTEGER PRIMARY KEY,
                id_audiencia_preparatoria INTEGER,
                id_victima INTEGER UNIQUE,
                id_denunciado INTEGER UNIQUE,
                tipo_relacion INTEGER UNIQUE,
                victima_representante_legal TEXT,
                denunciado_representante_legal TEXT,
                denunciante_representanteLegal TEXT,
                FOREIGN KEY (id_audiencia_preparatoria) REFERENCES audiencia_preparatoria(id_audiencia_preparatoria),
                FOREIGN KEY (id_victima) REFERENCES victima(id_victima),
                FOREIGN KEY (id_denunciado) REFERENCES denunciado(id_denunciado)
                FOREIGN KEY (tipo_relacion) REFERENCES denunciantes(tipo_relacion)
            );
            ''')

            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS medidas_cautelares_preparatoria (
                    id_medida_cautelar INTEGER PRIMARY KEY,
                    id_audiencia_preparatoria INTEGER,
                    tipo_medida TEXT,
                    respuesta TEXT,
                    plazo TEXT,
                    FOREIGN KEY (id_audiencia_preparatoria) REFERENCES audiencia_preparatoria(id_audiencia_preparatoria)
                );
            ''')

            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS audiencia_juicio (
                    id_audiencia_juicio INTEGER PRIMARY KEY,
                    id_causa INTEGER UNIQUE,
                    fecha_citacion TEXT,
                    fecha_realizacion TEXT,
                    cambio_composicion_hogar TEXT,
                    suspendido TEXT,
                    resolucion TEXT,
                    sentencia TEXT,
                    salida_colaborativa TEXT,
                    carabineros_informa_cese_medidas TEXT,
                    recurso_procesal TEXT,
                    recurso_procesal_otro TEXT,
                    abre_causa_cumplimiento TEXT,
                    causa_cumplimiento_rol_rit TEXT,
                    solicitan_informes_oficios TEXT,
                    informes_solicitados_a_quien TEXT,  
                    informes_entregados TEXT,
                    informes_entregados_cuales TEXT,
                    informes_pendientes TEXT,
                    demora_informes TEXT,  -- Asumo que es un campo de tipo texto
                    suspension_condicional TEXT,
                    otro_acuerdo_cual TEXT,
                    pericia_solicitada TEXT,
                    pericia_cual TEXT,
                    pericia_solicitante TEXT,
                    pericia_resultado TEXT,
                    pericia_evaluado TEXT,
                    medidas_cautelares TEXT,
                    medidas_recurso TEXT,       
                    FOREIGN KEY (ID_Causa) REFERENCES causa(id_causa)
                );
            ''')

            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS audiencia_juicio_relaciones (
                    id_audenciaJuicio_relaciones INTEGER PRIMARY KEY,
                    id_audiencia_juicio INTEGER,
                    id_victima INTEGER UNIQUE,
                    id_denunciado INTEGER UNIQUE,
                    tipo_relacion INTERGER UNIQUE,
                    victima_representante_legal TEXT,
                    denunciado_representante_legal TEXT,
                    denunciante_representanteLegal TEXT,
                    FOREIGN KEY (id_audiencia_juicio) REFERENCES audiencia_juicio(id_audiencia_juicio),
                    FOREIGN KEY (id_victima) REFERENCES victima(id_victima),
                    FOREIGN KEY (id_denunciado) REFERENCES denunciado(id_denunciado),
                    FOREIGN KEY (tipo_relacion) REFERENCES denunciantes(tipo_relacion)
                );
            ''')

            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS composicion_hogar_en_juicio (
                    id_composicion_actual INTEGER PRIMARY KEY,
                    id_audiencia_juicio INTEGER NOT NULL,
                    id_victima INTEGER NOT NULL,
                    tipo_relacion TEXT NOT NULL,
                    respuesta TEXT,
                    cantidad TEXT NOT NULL,
                    FOREIGN KEY (id_victima) REFERENCES victima(id_victima),
                    FOREIGN KEY (id_audiencia_juicio) REFERENCES audiencia_juicio(id_audiencia_juicio)
                );
            ''')

            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS medidas_provisorias_juicio (
                    id_medida_sentencia INTEGER PRIMARY KEY,
                    id_jucio INTEGER NOT NULL,
                    tipo_medida TEXT NOT NULL,
                    respuesta TEXT,
                    plazo TEXT,
                    FOREIGN KEY (id_jucio) REFERENCES audiencia_juicio(id_audiencia_juicio)
                );
            ''')

            await cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS antecedentes_delito (
                    id_antecedentes_delito INTEGER PRIMARY KEY,
                    id_causa INTEGER UNIQUE,
                    codigo_delito TEXT,
                    fecha_delito DATE,
                    hora_delito TIME,
                    lugar_ocurrencia TEXT,
                    lugar_ocurrencia_otro TEXT,
                    comuna TEXT,
                    unidad TEXT,
                    cuadrante TEXT,
                    FOREIGN KEY (ID_Causa) REFERENCES causa(id_causa)
                );
            ''')

            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS medidas_policiales (
                    id_medida_policial INTEGER PRIMARY KEY,
                    id_antecedentes_delito INTEGER NOT NULL,
                    tipo_medida TEXT,
                    respuesta TEXT,
                    plazo TEXT,
                    interpone_recurso TEXT,
                    demanda_reconvencional TEXT,
                    FOREIGN KEY (id_antecedentes_delito) REFERENCES antecedentes_delito(id_antecedentes_delito)
                );
            ''')

            await conexion.commit()

# CRUD:

    async def _add_user(self, usuario: str, password: str):
        async with aiosqlite.connect(self.db_name) as conexion:
            password_hash = bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt())
            try:
                await conexion.execute(
                    "INSERT INTO usuarios (usuario, password) VALUES (?, ?)", (usuario, password_hash))
                await conexion.commit()
                print(f"Usuario {usuario} agregado exitosamente.")
            except aiosqlite.IntegrityError:
                print(f"Ocurrió un error: El usuario {usuario} ya existe.")
                await conexion.rollback()
            except Exception as e:
                print(f"Ocurrió un error al agregar al usuario {usuario}: {e}")
                await conexion.rollback()

    async def _user_verification(self, usuario: str, password: str):

        if usuario == "liacdd":
            if password == "admin:derecho":  # Reemplaza con la contraseña real de 'liacdd'
                return True, "Entrando en modo administrador"
            else:
                return False, "Contraseña incorrecta para el modo administrador"
            
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT password, failed_attempts, lockout_until FROM usuarios WHERE usuario = ?", (usuario,))
            result = await cursor.fetchone()
            if result is None:
                return False, f"No existe el usuario {usuario}."

            stored_password_hash, failed_attempts, lockout_until = result
    
            # Si el tiempo de bloqueo ha pasado, resetea los intentos fallidos y el tiempo de bloqueo
            if lockout_until is not None and time.time() >= lockout_until:
                await conexion.execute(
                    "UPDATE usuarios SET failed_attempts = 0, lockout_until = NULL WHERE usuario = ?",
                    (usuario,))
                await conexion.commit()
                failed_attempts = 0  # Restablece también la variable en la lógica actual

            # Si la cuenta está bloqueada, informa al usuario
            elif lockout_until is not None and time.time() < lockout_until:
                unblock_time = datetime.fromtimestamp(
                    lockout_until).strftime('%H:%M:%S')
                return False, f"La cuenta está bloqueada debido a múltiples intentos fallidos de inicio de sesión. Intenta de nuevo después de las {unblock_time}."

            password_correct = bcrypt.checkpw(
                password.encode('utf-8'), stored_password_hash)
            
                
            if not password_correct:
                new_failed_attempts = failed_attempts + 1
                if new_failed_attempts >= 3:
                    # Utiliza 180 para 3 minutos
                    lockout_until = int(time.time()) + 180
                    await conexion.execute(
                        "UPDATE usuarios SET failed_attempts = ?, lockout_until = ? WHERE usuario = ?",
                        (new_failed_attempts, lockout_until, usuario))
                    await conexion.commit()
                    unblock_time = datetime.fromtimestamp(
                        lockout_until).strftime('%H:%M:%S')
                    return False, f"Cuenta bloqueada por múltiples intentos fallidos. Intenta de nuevo después de las {unblock_time}."
                else:
                    await conexion.execute(
                        "UPDATE usuarios SET failed_attempts = ? WHERE usuario = ?",
                        (new_failed_attempts, usuario))
                    await conexion.commit()
                    return False, f"Incorrecto. Has usado {new_failed_attempts} de 3 intentos."

            else:
                # reiniciar el conteo de intentos fallidos y remover el bloqueo si la contraseña es correcta
                await conexion.execute(
                    "UPDATE usuarios SET failed_attempts = 0, lockout_until = NULL WHERE usuario = ?",
                    (usuario,))
                await conexion.commit()
                return True, f"Usuario {usuario} verificado exitosamente."
    # Causa

    async def add_causa(self, causa: Causa):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute(
                '''
                INSERT INTO causa (
                    id_causa, digitador, rol_rit, fecha_ingreso, cartulado, procedimiento, 
                    materia, estado_admin, ubicacion, cuaderno, etapa, 
                    estado_procesal, etapa_actual, via_ingreso, causa_proteccion_abierta,
                    causa_penal_abierta
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    causa.id_causa, causa.digitador, causa.rol_rit, causa.fecha_ingreso, causa.cartulado, causa.procedimiento,
                    causa.materia, causa.estado_admin, causa.ubicacion, causa.cuaderno, causa.etapa,
                    causa.estado_procesal, causa.etapa_actual, causa.via_ingreso, causa.causa_proteccion_abierta,
                    causa.causa_penal_abierta
                )
            )
            await conexion.commit()

    async def update_causa(self, id_causa, causa: Causa):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute(
                '''
                UPDATE causa SET 
                    digitador = ?, 
                    rol_rit = ?, 
                    fecha_ingreso = ?, 
                    cartulado = ?, 
                    procedimiento = ?, 
                    materia = ?, 
                    estado_admin = ?,  
                    ubicacion = ?, 
                    cuaderno = ?, 
                    etapa = ?, 
                    estado_procesal = ?, 
                    etapa_actual = ?, 
                    via_ingreso = ?,
                    causa_proteccion_abierta = ?,  
                    causa_penal_abierta = ?        
                WHERE id_causa = ?
                ''', (
                    causa.digitador, causa.rol_rit, causa.fecha_ingreso, causa.cartulado, causa.procedimiento,
                    causa.materia, causa.estado_admin, causa.ubicacion, causa.cuaderno, causa.etapa,
                    causa.estado_procesal, causa.etapa_actual, causa.via_ingreso,
                    causa.causa_proteccion_abierta,
                    causa.causa_penal_abierta,
                    id_causa
                )
            )
            await conexion.commit()

    async def delete_causa(self, id_causa):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute(
                '''
                DELETE FROM CAUSA WHERE id_causa = ?
                ''', (id_causa,)
            )
            await conexion.commit()

    async def existe_causa(self, id_causa):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM causa WHERE id_causa = ?",
                (id_causa,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

        # Victima
    async def update_victima(self, id_victima, victima: Victima):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute(
            """
                UPDATE victima SET
                edad = ?,
                sexo = ?,
                nacionalidad = ?,
                nacionalidad_extranjera = ?,
                profesion_oficio = ?,
                estudios = ?,
                parentesco_acusado = ?,
                parentesco_acusado_otro = ?,
                caracter_lesion = ?,
                descripcion_lesion = ?,
                estado_temperancia = ?,
                estado_temperancia_otro = ?,
                descripcion_temperancia = ?,
                comuna = ?,
                tiempo_relacion = ?,
                estado_civil = ?,
                parentesco_denunciante = ?,
                parentesco_denunciante_otro = ?,
                violencia_patrimonial = ?, 
                violencia_economica = ?,
                ayuda_tecnica = ?,
                ayuda_tecnica_tipo = ?, 
                deterioro_cognitivo = ?,
                informe_medico = ?,
                num_enfermedades = ?,  
                inasistencias_salud = ?,
                informes_social = ?,
                comuna_ingreso = ?,
                listado_enfermedades = ?
                WHERE id_victima = ?
            """,
            (
                victima.edad, victima.sexo, victima.nacionalidad,
                victima.nacionalidad_extranjera, victima.profesion_oficio,
                victima.estudios, victima.parentesco_acusado,
                victima.parentesco_acusado_otro, victima.caracter_lesion,
                victima.descripcion_lesion, victima.estado_temperancia,
                victima.estado_temperancia_otro, victima.descripcion_temperancia,
                victima.comuna, victima.tiempo_relacion, victima.estado_civil,
                victima.parentesco_denunciante, victima.parentesco_denunciante_otro,
                victima.violencia_patrimonial, victima.vic_violencia_economica,
                victima.vic_ayuda_tecnica, victima.vic_ayuda_tecnica_tipo,
                victima.vic_deterioro_cognitivo, victima.vic_informe_medico,
                victima.vic_num_enfermedades, victima.vic_inasistencias_salud, 
                victima.vic_informes_social, victima.vic_comuna_ingreso, victima.listado_enfermedades,
                id_victima
            )
            )
            await conexion.commit()

    async def add_victima(self, id_causa, victima: Victima):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.cursor()

                query = """
                    INSERT INTO victima (
                        id_causa, edad, sexo, nacionalidad, nacionalidad_extranjera,  
                        profesion_oficio, estudios, parentesco_acusado,  
                        parentesco_acusado_otro, caracter_lesion, descripcion_lesion,  
                        estado_temperancia, estado_temperancia_otro,  
                        descripcion_temperancia, comuna, tiempo_relacion, estado_civil,  
                        parentesco_denunciante, parentesco_denunciante_otro,  
                        violencia_patrimonial, violencia_economica, ayuda_tecnica, 
                        ayuda_tecnica_tipo, deterioro_cognitivo, informe_medico, num_enfermedades, 
                        inasistencias_salud, informes_social, comuna_ingreso, listado_enfermedades
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                values = (
                    id_causa, victima.edad, victima.sexo, victima.nacionalidad, victima.nacionalidad_extranjera,  
                    victima.profesion_oficio, victima.estudios, victima.parentesco_acusado,
                    victima.parentesco_acusado_otro, victima.caracter_lesion, victima.descripcion_lesion,  
                    victima.estado_temperancia, victima.estado_temperancia_otro, victima.descripcion_temperancia,
                    victima.comuna, victima.tiempo_relacion, victima.estado_civil, victima.parentesco_denunciante, 
                    victima.parentesco_denunciante_otro, victima.violencia_patrimonial, victima.vic_violencia_economica,
                    victima.vic_ayuda_tecnica, victima.vic_ayuda_tecnica_tipo, victima.vic_deterioro_cognitivo, 
                    victima.vic_informe_medico, victima.vic_num_enfermedades, victima.vic_inasistencias_salud, 
                    victima.vic_informes_social, victima.vic_comuna_ingreso, victima.listado_enfermedades
                )
                await cursor.execute(query, values)
                await conexion.commit()
        except Exception as e:
            print(f"Error al agregar víctima: {e}")

    async def delete_victima(self, id_victima):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute(
                '''
                DELETE FROM victima WHERE id_victima = ?
                ''', (id_victima,)
            )
            await conexion.commit()

    async def existe_victima(self, id_victima):
        # Implementar la lógica para verificar si existe la víctima en la BD
        # Podría ser una consulta SQL que verifica si existe un registro con el id_victima dado
        # Retorna True si la víctima existe, False en caso contrario
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM victima WHERE id_victima = ?",
                (id_victima,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

     # Composición hogar

    async def add_composition(self, id_victima: int, composicion_hogar: ComposicionHogar):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                INSERT INTO composicion_hogar (id_victima, tipo_relacion, respuesta, cantidad) 
                VALUES (?, ?, ?, ?)
            ''', (id_victima, composicion_hogar.tipo_relacion, composicion_hogar.respuesta,
                  composicion_hogar.cantidad))
            await conexion.commit()

    async def update_composition(self, id_composicion: int, composicion_hogar: ComposicionHogar):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                UPDATE composicion_hogar 
                SET id_victima = ?, tipo_relacion = ?,respuesta = ? ,cantidad = ?
                WHERE id_composicion = ?
            ''', (composicion_hogar.id_victima, composicion_hogar.tipo_relacion, composicion_hogar.respuesta, composicion_hogar.cantidad, id_composicion))
            await conexion.commit()

    async def delete_composition(self, id_composicion: int):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                    DELETE FROM composicion_hogar 
                    WHERE id_composicion = ?
                ''', (id_composicion,))
            await conexion.commit()

    async def existe_composicion_hogar(self, id_composicion):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM composicion_hogar WHERE id_composicion = ?",
                (id_composicion,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

    # Denunciado

    async def add_denunciado(self, id_causa: int, denunciado: Denunciado):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute('''
                    INSERT INTO denunciado (
                        id_causa, edad, sexo, nacionalidad, nacionalidad_Extranjera, 
                        profesion_Oficio, estudios, caracter_lesion, lesiones_Descripcion, 
                        estado_Temperancia, temperancia_Otro, temperancia_Descripcion, 
                        otros_Antecedentes, comuna, nivel_riesgo, vif_numero,
                        estado_civil
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    id_causa, denunciado.edad, denunciado.sexo, denunciado.nacionalidad,
                    denunciado.nacionalidad_extranjera, denunciado.profesion_oficio,
                    denunciado.estudios, denunciado.caracter_lesion, denunciado.lesiones_descripcion,
                    denunciado.estado_temperancia, denunciado.temperancia_otro,
                    denunciado.temperancia_descripcion, denunciado.otros_antecedentes,
                    denunciado.comuna, denunciado.nivel_riesgo,
                    denunciado.vif_numero, denunciado.estado_civil
                ))
                await conexion.commit()

                id_denunciado = cursor.lastrowid
                return id_denunciado
        except aiosqlite.Error as e:
            # Manejo de errores (puedes personalizar el mensaje de error según tus necesidades)
            print(f"Error al agregar denunciado: {e}")
            return None

    async def update_denunciado(self, id_denunciado: int, denunciado: Denunciado):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                UPDATE denunciado 
                SET id_causa = ?, edad = ?, sexo = ?, nacionalidad = ?, nacionalidad_Extranjera = ?, profesion_Oficio = ?, estudios = ?, caracter_lesion = ?, lesiones_Descripcion = ?, estado_Temperancia = ?, temperancia_Otro = ?, temperancia_Descripcion = ?, otros_Antecedentes = ?, comuna = ?, nivel_riesgo = ?, vif_numero = ?, estado_civil = ?
                WHERE id_denunciado = ?
            ''', (
                denunciado.id_causa, denunciado.edad, denunciado.sexo,
                denunciado.nacionalidad, denunciado.nacionalidad_extranjera,
                denunciado.profesion_oficio, denunciado.estudios, denunciado.caracter_lesion,
                denunciado.lesiones_descripcion, denunciado.estado_temperancia, denunciado.temperancia_otro,
                denunciado.temperancia_descripcion, denunciado.otros_antecedentes, denunciado.comuna,
                denunciado.nivel_riesgo, denunciado.vif_numero,
                denunciado.estado_civil, id_denunciado
            ))
            await conexion.commit()

    async def delete_denunciado(self, id_denunciado: int):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                    DELETE FROM denunciado 
                    WHERE id_denunciado = ?
                ''', (id_denunciado,))
            await conexion.commit()

    async def existe_denunciado(self, id_denunciado):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM denunciado WHERE id_denunciado = ?",
                (id_denunciado,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

    # Antecedentes del denunciado

    async def add_antecedentes_denunciado(self, id_denunciado: int, antecedentes_denunciado: AntecedentesDenunciado):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                INSERT INTO denunciado_antecedentes (
                    id_denunciado, tipo_antecedente, descripcion
                ) VALUES (?, ?, ?)
            ''', (
                id_denunciado, antecedentes_denunciado.tipo_antecedente, antecedentes_denunciado.descripcion
            ))
            await conexion.commit()

    async def update_antecedentes_denunciado(self, id_antecedente: int, antecedentes_denunciado: AntecedentesDenunciado):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                UPDATE denunciado_antecedentes 
                SET id_denunciado = ?, tipo_antecedente = ?, descripcion = ?
                WHERE id_antecedente = ?
            ''', (
                antecedentes_denunciado.id_denunciado, antecedentes_denunciado.tipo_antecedente,
                antecedentes_denunciado.descripcion, id_antecedente
            ))
            await conexion.commit()

    async def delete_antecedentes_denunciado(self, id_antecedentes: int):
        try:
            query = "DELETE FROM denunciado_antecedentes WHERE id_antecedente = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_antecedentes,))
                await conexion.commit()

            print("Antecedentes del denunciado eliminados correctamente")
        except Exception as e:
            print(f"Error al eliminar antecedentes del denunciado: {e}")

    async def existe_antecedente_denunciado(self, id_antecedentes_delito):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM denunciado_antecedentes WHERE id_antecedente = ?",
                (id_antecedentes_delito,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

    #  Indicadores del riesgo del denunciado

    async def add_indicador_riesgo_vif(self, id_denunciado: int, indicador_riesgo_vif: DenunciadoIndicadoresRiesgoVIF):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                INSERT INTO denunciado_indicadores_riesgo_vif (id_denunciado, descripcion_indicador, respuesta) 
                VALUES (?, ?, ?)
            ''', (id_denunciado, indicador_riesgo_vif.descripcion_indicador, indicador_riesgo_vif.respuesta))
            await conexion.commit()

    async def update_indicador_riesgo_vif(self, id_riesgo_vif: int, indicador_riesgo_vif: DenunciadoIndicadoresRiesgoVIF):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                UPDATE denunciado_indicadores_riesgo_vif 
                SET descripcion_indicador = ?, respuesta = ?
                WHERE id_riesgo_vif = ?
            ''', (indicador_riesgo_vif.descripcion_indicador, indicador_riesgo_vif.respuesta, id_riesgo_vif))
            await conexion.commit()

    async def delete_indicador_riesgo_vif(self, id_riesgo_vif: int):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                DELETE FROM denunciado_indicadores_riesgo_vif 
                WHERE id_riesgo_vif = ?
            ''', (id_riesgo_vif,))
            await conexion.commit()

    async def existe_indicador_riesgo_vif(self, id_denunciado):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM denunciado_indicadores_riesgo_vif WHERE id_denunciado = ?",
                (id_denunciado,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

    # Crud: denunciantes

    async def add_denunciante(self, id_causa: int, denunciante: Denunciante):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                INSERT INTO denunciantes (
                    id_causa, es_denunciante_victima, es_denunciante_persona_juridica, nombre_persona_juridica,
                    edad_denunciante, sexo_denunciante, nacionalidad_denunciante, nacionalidad_extranjera_denunciante,
                    profesion_oficio_denunciante, estudios_denunciante, parentesco_acusado, parentesco_acusado_otro,
                    caracter_lesion_denunciante, descripcion_lesion_denunciante, estado_temperancia_denunciante,
                    estado_temperancia_denunciante_otro, descripcion_temperancia_denunciante, comuna, estado_civil
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                id_causa, denunciante.es_denunciante_victima, denunciante.es_denunciante_persona_juridica,
                denunciante.nombre_persona_juridica, denunciante.edad_denunciante, denunciante.sexo_denunciante,
                denunciante.nacionalidad_denunciante, denunciante.nacionalidad_extranjera_denunciante,
                denunciante.profesion_oficio_denunciante, denunciante.estudios_denunciante, denunciante.parentesco_acusado,
                denunciante.parentesco_acusado_otro, denunciante.caracter_lesion_denunciante,
                denunciante.descripcion_lesion_denunciante, denunciante.estado_temperancia_denunciante,
                denunciante.estado_temperancia_denunciante_otro, denunciante.descripcion_temperancia_denunciante,
                denunciante.comuna, denunciante.estado_civil
            ))
            await conexion.commit()

    async def update_denunciante(self, tipo_relacion: int, denunciante: Denunciante):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                UPDATE denunciantes 
                SET id_causa = ?, es_denunciante_victima = ?, es_denunciante_persona_juridica = ?, nombre_persona_juridica = ?,
                    edad_denunciante = ?, sexo_denunciante = ?, nacionalidad_denunciante = ?, nacionalidad_extranjera_denunciante = ?,
                    profesion_oficio_denunciante = ?, estudios_denunciante = ?, parentesco_acusado = ?, parentesco_acusado_otro = ?,
                    caracter_lesion_denunciante = ?, descripcion_lesion_denunciante = ?, estado_temperancia_denunciante = ?,
                    estado_temperancia_denunciante_otro = ?, descripcion_temperancia_denunciante = ?, comuna = ?, estado_civil = ?
                WHERE tipo_relacion = ?
            ''', (
                denunciante.id_causa, denunciante.es_denunciante_victima, denunciante.es_denunciante_persona_juridica,
                denunciante.nombre_persona_juridica, denunciante.edad_denunciante, denunciante.sexo_denunciante,
                denunciante.nacionalidad_denunciante, denunciante.nacionalidad_extranjera_denunciante,
                denunciante.profesion_oficio_denunciante, denunciante.estudios_denunciante, denunciante.parentesco_acusado,
                denunciante.parentesco_acusado_otro, denunciante.caracter_lesion_denunciante,
                denunciante.descripcion_lesion_denunciante, denunciante.estado_temperancia_denunciante,
                denunciante.estado_temperancia_denunciante_otro, denunciante.descripcion_temperancia_denunciante,
                denunciante.comuna, denunciante.estado_civil, tipo_relacion
            ))
            await conexion.commit()

    async def delete_denunciante(self, tipo_relacion: int):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                DELETE FROM denunciantes 
                WHERE tipo_relacion = ?
            ''', (tipo_relacion,))
            await conexion.commit()

    async def existe_denunciante(self, tipo_relacion):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM denunciantes WHERE tipo_relacion = ?",
                (tipo_relacion,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

    # audencia_preparatoria

    async def add_audiencia_preparatoria(self, id_causa: int, audiencia: AudienciaPreparatoria):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
            INSERT INTO audiencia_preparatoria (
                id_causa,
                fecha_citacion, 
                fecha_realizacion,
                suspension_anterior,
                solicita_informes_oficios,
                resolucion,
                salida_colaborativa,
                otras_observaciones,
                informes_solicitados_a_quien,
                informes_entregados,
                informes_entregados_cuales,
                informes_pendientes,
                demora_entrega_informes,
                pericia_solicitada,
                pericia_cual,
                pericia_solicitante
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
            id_causa,
            audiencia.fecha_citacion,
            audiencia.fecha_realizacion,
            audiencia.suspension_anterior,
            audiencia.solicita_informes_oficios,
            audiencia.resolucion,
            audiencia.salida_colaborativa,
            audiencia.otras_observaciones,
            audiencia.informes_solicitados_a_quien,
            audiencia.informes_entregados,
            audiencia.informes_entregados_cuales,
            audiencia.informes_pendientes,
            audiencia.demora_entrega_informes,
            audiencia.pericia_solicitada,
            audiencia.pericia_cual,
            audiencia.pericia_solicitante
            ))
            
            await conexion.commit()

    async def update_audiencia_preparatoria(self, id_audiencia_preparatoria, audiencia: AudienciaPreparatoria):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
            UPDATE audiencia_preparatoria SET
                id_causa = ?,
                fecha_citacion = ?,
                fecha_realizacion = ?,
                suspension_anterior = ?,
                solicita_informes_oficios = ?,
                resolucion = ?,
                salida_colaborativa = ?,
                otras_observaciones = ?,
                informes_solicitados_a_quien = ?,
                informes_entregados = ?,
                informes_entregados_cuales = ?,
                informes_pendientes = ?,
                demora_entrega_informes = ?,
                pericia_solicitada = ?,
                pericia_cual = ?,
                pericia_solicitante = ?
            WHERE id_audiencia_preparatoria = ?
            ''', (
            audiencia.id_causa,
            audiencia.fecha_citacion,
            audiencia.fecha_realizacion,
            audiencia.suspension_anterior,
            audiencia.solicita_informes_oficios,
            audiencia.resolucion,
            audiencia.salida_colaborativa,
            audiencia.otras_observaciones,
            audiencia.informes_solicitados_a_quien,
            audiencia.informes_entregados,
            audiencia.informes_entregados_cuales,
            audiencia.informes_pendientes,
            audiencia.demora_entrega_informes,
            audiencia.pericia_solicitada,
            audiencia.pericia_cual,
            audiencia.pericia_solicitante,
            id_audiencia_preparatoria
            ))
            
            await conexion.commit()

    async def delete_audiencia_preparatoria(self, id_audiencia_preparatoria):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute(
                '''
                DELETE FROM audiencia_preparatoria WHERE id_audiencia_preparatoria = ?
                ''', (id_audiencia_preparatoria,)
            )
            await conexion.commit()

    async def existe_audiencia_preparatoria(self, id_audiencia_preparatoria):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM audiencia_preparatoria WHERE id_audiencia_preparatoria = ?",
                (id_audiencia_preparatoria,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None
    # Crud: Aundencia preparatoria relaciones

    async def add_audiencia_preparatoria_relacion(self, id_audiencia_preparatoria, audiencia_relacion: AudienciaRelaciones):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                INSERT INTO audiencia_preparatoria_relaciones (
                    id_audiencia_preparatoria, id_victima, id_denunciado, tipo_relacion,
                    victima_representante_legal, denunciado_representante_legal, Denunciante_RepresentanteLegal
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                id_audiencia_preparatoria,
                audiencia_relacion.id_victima,
                audiencia_relacion.id_denunciado,
                audiencia_relacion.tipo_relacion,
                audiencia_relacion.victima_representante_legal,
                audiencia_relacion.denunciado_representante_legal,
                audiencia_relacion.denunciante_representante_legal
            ))
            await conexion.commit()

    async def update_audiencia_preparatoria_relacion(self, id_relacion, audiencia_relacion: AudienciaRelaciones):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                UPDATE audiencia_preparatoria_relaciones SET 
                    id_audiencia_preparatoria = ?, id_victima = ?, id_denunciado = ?, tipo_relacion = ?,
                    victima_representante_legal = ?, denunciado_representante_legal = ?, Denunciante_RepresentanteLegal = ?
                WHERE id_audencia_preparatoria_relaciones = ?
                ''', (
                audiencia_relacion.id_audiencia,
                audiencia_relacion.id_victima,
                audiencia_relacion.id_denunciado,
                audiencia_relacion.tipo_relacion,
                audiencia_relacion.victima_representante_legal,
                audiencia_relacion.denunciado_representante_legal,
                audiencia_relacion.denunciante_representante_legal,
                id_relacion
            ))
            await conexion.commit()

    async def delete_audiencia_preparatoria_relacion(self, id_relacion):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                DELETE FROM audiencia_preparatoria_relaciones WHERE id_audencia_preparatoria_relaciones = ?
                ''', (id_relacion,)
            )
            await conexion.commit()

    async def existe_audiencia_preparatoria_relacion(self, id_involucrado):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM audiencia_preparatoria_relaciones WHERE id_audencia_preparatoria_relaciones = ?",
                (id_involucrado,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

    # Crud: Medicas cautelares de audencia preparatoria

    async def add_medida_cautelar_preparatoria(self, id_audiencia, medida_cautelar: MedidaCautelar):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                    INSERT INTO medidas_cautelares_preparatoria (
                        id_audiencia_preparatoria, tipo_medida, respuesta, plazo
                    ) VALUES (?, ?, ?, ?)
                    ''', (
                id_audiencia,
                medida_cautelar.tipo_medida,
                medida_cautelar.respuesta,
                medida_cautelar.plazo
            ))
            await conexion.commit()

    async def update_medida_cautelar_preparatoria(self, id_medida_cautelar, medida_cautelar: MedidaCautelar):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                    UPDATE medidas_cautelares_preparatoria SET 
                        id_audiencia_preparatoria = ?, tipo_medida = ?, respuesta = ?,plazo = ?
                    WHERE id_medida_cautelar = ?
                    ''', (
                medida_cautelar.id_evento,
                medida_cautelar.tipo_medida,
                medida_cautelar.plazo,
                id_medida_cautelar
            ))
            await conexion.commit()

    async def delete_medida_cautelar_preparatoria(self, id_medida_cautelar):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                    DELETE FROM medidas_cautelares_preparatoria WHERE id_medida_cautelar = ?
                    ''', (id_medida_cautelar,))
            await conexion.commit()

    async def existe_medida_preparatoria(self, id_medida_preparatoria):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM medidas_cautelares_preparatoria WHERE id_medida_cautelar = ?",
                (id_medida_preparatoria,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

    # Crud: Audencia Antecendentes del jucio

    async def add_audiencia_juicio(self, id_causa: int, audiencia_juicio: AudienciaJuicioAntecedentes):

        async with aiosqlite.connect(self.db_name) as conexion:

            await conexion.execute('''
            INSERT INTO audiencia_juicio (
                id_causa, 
                fecha_citacion,
                fecha_realizacion,
                cambio_composicion_hogar,
                suspendido,
                resolucion,
                sentencia,
                salida_colaborativa,
                carabineros_informa_cese_medidas,
                recurso_procesal,
                recurso_procesal_otro,
                abre_causa_cumplimiento,
                causa_cumplimiento_rol_rit,
                solicitan_informes_oficios,
                informes_solicitados_a_quien,
                informes_entregados,
                informes_entregados_cuales,
                informes_pendientes,
                demora_informes,
                suspension_condicional,
                otro_acuerdo_cual,
                pericia_solicitada,
                pericia_cual,
                pericia_solicitante,
                pericia_resultado,
                pericia_evaluado,
                medidas_cautelares,
                medidas_recurso
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
            id_causa,
            audiencia_juicio.fecha_citacion,
            audiencia_juicio.fecha_realizacion,
            audiencia_juicio.cambio_composicion_hogar,
            audiencia_juicio.suspendido,
            audiencia_juicio.resolucion,
            audiencia_juicio.sentencia,
            audiencia_juicio.salida_colaborativa,
            audiencia_juicio.carabineros_informa_cese_medidas,
            audiencia_juicio.recurso_procesal,
            audiencia_juicio.recurso_procesal_otro,
            audiencia_juicio.abre_causa_cumplimiento,
            audiencia_juicio.causa_cumplimiento_rol_rit,
            audiencia_juicio.solicitan_informes_oficios,
            audiencia_juicio.informes_solicitados_a_quien,
            audiencia_juicio.informes_entregados,
            audiencia_juicio.informes_entregados_cuales,
            audiencia_juicio.informes_pendientes,
            audiencia_juicio.demora_informes,
            audiencia_juicio.suspension_condicional,
            audiencia_juicio.otro_acuerdo_cual,
            audiencia_juicio.pericia_solicitada,
            audiencia_juicio.pericia_cual,
            audiencia_juicio.pericia_solicitante,
            audiencia_juicio.pericia_resultado,
            audiencia_juicio.pericia_evaluado,
            audiencia_juicio.medidas_cautelares,
            audiencia_juicio.medidas_recurso
            ))
            await conexion.commit()

    async def update_audiencia_juicio(self, id_audiencia_juicio, audiencia_juicio: AudienciaJuicioAntecedentes):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
            UPDATE audiencia_juicio SET
                id_causa = ?,
                fecha_citacion = ?,
                fecha_realizacion = ?,
                cambio_composicion_hogar = ?,
                suspendido = ?, 
                resolucion = ?,
                sentencia = ?,
                salida_colaborativa = ?,
                carabineros_informa_cese_medidas = ?,
                recurso_procesal = ?,
                recurso_procesal_otro = ?,
                abre_causa_cumplimiento = ?,
                causa_cumplimiento_rol_rit = ?,
                solicitan_informes_oficios = ?,
                informes_solicitados_a_quien = ?,
                informes_entregados = ?,
                informes_entregados_cuales = ?,
                informes_pendientes = ?,
                demora_informes = ?,
                suspension_condicional = ?,
                otro_acuerdo_cual = ?,
                pericia_solicitada = ?,
                pericia_cual = ?,
                pericia_solicitante = ?,
                pericia_resultado = ?,
                pericia_evaluado = ?,
                medidas_cautelares = ?,
                medidas_recurso = ?
            WHERE id_audiencia_juicio = ?
            ''', (
            audiencia_juicio.id_causa,
            audiencia_juicio.fecha_citacion,
            audiencia_juicio.fecha_realizacion,  
            audiencia_juicio.cambio_composicion_hogar,
            audiencia_juicio.suspendido,
            audiencia_juicio.resolucion,
            audiencia_juicio.sentencia,
            audiencia_juicio.salida_colaborativa,
            audiencia_juicio.carabineros_informa_cese_medidas,
            audiencia_juicio.recurso_procesal,
            audiencia_juicio.recurso_procesal_otro,
            audiencia_juicio.abre_causa_cumplimiento,
            audiencia_juicio.causa_cumplimiento_rol_rit,
            audiencia_juicio.solicitan_informes_oficios,
            audiencia_juicio.informes_solicitados_a_quien,
            audiencia_juicio.informes_entregados,
            audiencia_juicio.informes_entregados_cuales,
            audiencia_juicio.informes_pendientes,
            audiencia_juicio.demora_informes,
            audiencia_juicio.suspension_condicional,
            audiencia_juicio.otro_acuerdo_cual,
            audiencia_juicio.pericia_solicitada,
            audiencia_juicio.pericia_cual,
            audiencia_juicio.pericia_solicitante,
            audiencia_juicio.pericia_resultado,
            audiencia_juicio.pericia_evaluado,
            audiencia_juicio.medidas_cautelares,
            audiencia_juicio.medidas_recurso,
            id_audiencia_juicio
            )
            )
            await conexion.commit()



    async def delete_audiencia_juicio(self, id_audiencia_juicio):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                DELETE FROM audiencia_juicio WHERE id_audiencia_juicio = ?
                ''', (id_audiencia_juicio,))
            await conexion.commit()

    # En tu clase de base de datos
    async def existe_audiencia_juicio(self, id_audiencia_juicio):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM audiencia_juicio WHERE id_audiencia_juicio = ?",
                (id_audiencia_juicio,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

    # CRUD: Relaciones de los antecedentes del jucio
    async def add_audiencia_juicio_relacion(self, id_audiencia, audiencia_juicio_relacion: AudienciaRelaciones):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                INSERT INTO audiencia_juicio_relaciones (
                    id_audiencia_juicio, id_victima, id_denunciado, tipo_relacion,
                    victima_representante_legal, denunciado_representante_legal, Denunciante_RepresentanteLegal
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                id_audiencia,
                audiencia_juicio_relacion.id_victima,
                audiencia_juicio_relacion.id_denunciado,
                audiencia_juicio_relacion.tipo_relacion,
                audiencia_juicio_relacion.victima_representante_legal,
                audiencia_juicio_relacion.denunciado_representante_legal,
                audiencia_juicio_relacion.denunciante_representante_legal
            ))
            await conexion.commit()

    async def update_audiencia_juicio_relacion(self, id_relacion, audiencia_juicio_relacion: AudienciaRelaciones):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                UPDATE audiencia_juicio_relaciones SET 
                    id_audiencia_juicio = ?, id_victima = ?, id_denunciado = ?, tipo_relacion = ?,
                    victima_representante_legal = ?, denunciado_representante_legal = ?, Denunciante_RepresentanteLegal = ?
                WHERE id_audenciaJuicio_relaciones = ?
                ''', (
                audiencia_juicio_relacion.id_audiencia,
                audiencia_juicio_relacion.id_victima,
                audiencia_juicio_relacion.id_denunciado,
                audiencia_juicio_relacion.tipo_relacion,
                audiencia_juicio_relacion.victima_representante_legal,
                audiencia_juicio_relacion.denunciado_representante_legal,
                audiencia_juicio_relacion.denunciante_representante_legal,
                id_relacion
            ))
            await conexion.commit()

    async def delete_audiencia_juicio_relacion(self, id_relacion):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                DELETE FROM audiencia_juicio_relaciones WHERE id_audenciaJuicio_relaciones = ?
                ''', (id_relacion,))
            await conexion.commit()

    async def existe_audiencia_juicio_relacion(self, id_audiencia_juicio):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM audiencia_juicio_relaciones WHERE id_audenciaJuicio_relaciones = ?",
                (id_audiencia_juicio,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None
    # CRUD: composición del hogar en el jucio

    async def add_composicion_hogar_en_juicio(self, id_juicio: int, composicion: ComposicionHogarEnJuicio):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                INSERT INTO composicion_hogar_en_juicio (
                    id_audiencia_juicio, id_victima, tipo_relacion, respuesta, cantidad
                ) VALUES (?, ?, ?,? ,?)
                ''', (
                id_juicio,  # Usando el ID de juicio pasado como parámetro
                composicion.id_victima,
                composicion.tipo_relacion,
                composicion.respuesta,
                composicion.cantidad
            ))
            await conexion.commit()

    async def update_composicion_hogar_en_juicio(self, id_composicion, composicion: ComposicionHogarEnJuicio):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                UPDATE composicion_hogar_en_juicio SET 
                    id_audiencia_juicio = ?, id_victima = ?, tipo_relacion = ?, respuesta = ?, cantidad = ?
                WHERE id_composicion_actual = ?
                ''', (
                composicion.id_composicion,  # Asegúrate de que este es el nombre correcto de la columna
                composicion.id_victima,
                composicion.tipo_relacion,
                composicion.respuesta,
                composicion.cantidad,
                id_composicion
            ))
            await conexion.commit()

    async def delete_composicion_hogar_en_juicio(self, id_composicion):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                DELETE FROM composicion_hogar_en_juicio WHERE id_composicion_actual = ?
                ''', (id_composicion,))
            await conexion.commit()

    async def existe_composicion_hogar_cambio(self, id_audiencia_juicio):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM composicion_hogar_en_juicio WHERE id_audiencia_juicio = ?",
                (id_audiencia_juicio,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

    # CRUD: MEDIDAS PROVISORIAS DEL JUICIO SENTENCIA

    async def add_medida_provisoria_juicio(self, id_jucio, medida_provisoria: MedidaCautelar):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                INSERT INTO medidas_provisorias_juicio (
                    id_jucio, tipo_medida, respuesta, plazo
                ) VALUES (?, ?, ?, ?)
                ''', (
                id_jucio,
                medida_provisoria.tipo_medida,
                medida_provisoria.respuesta,
                medida_provisoria.plazo
            ))
            await conexion.commit()

    async def update_medida_provisoria_juicio(self, id_medida_sentencia, medida_provisoria: MedidaCautelar):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                UPDATE medidas_provisorias_juicio SET 
                    id_jucio = ?, tipo_medida = ?, respuesta = ?,plazo = ?
                WHERE id_medida_sentencia = ?
                ''', (
                medida_provisoria.id_evento,
                medida_provisoria.tipo_medida,
                medida_provisoria.respuesta,
                medida_provisoria.plazo,
                id_medida_sentencia
            ))
            await conexion.commit()

    async def delete_medida_provisoria_juicio(self, id_medida_sentencia):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                DELETE FROM medidas_provisorias_juicio WHERE id_medida_sentencia = ?
                ''', (id_medida_sentencia,))
            await conexion.commit()

    async def existe_medida_juicio(self, id_medida):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM medidas_provisorias_juicio WHERE id_medida_sentencia = ?",
                (id_medida,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

    # CRUD: Antencedente policiales

    async def add_antecedente_policial(self, id_causa, antecedente: AntecedentePolicial):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                INSERT INTO antecedentes_delito (
                    id_causa, codigo_delito, fecha_delito, hora_delito, lugar_ocurrencia, 
                    lugar_ocurrencia_otro, comuna, unidad, cuadrante
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                id_causa,
                antecedente.codigo_delito,
                antecedente.fecha_delito,
                antecedente.hora_delito,
                antecedente.lugar_ocurrencia,
                antecedente.lugar_ocurrencia_otro,
                antecedente.comuna,
                antecedente.unidad,
                antecedente.cuadrante
            ))
            await conexion.commit()

    async def update_antecedente_policial(self, id_antecedente_delito, antecedente: AntecedentePolicial):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                UPDATE antecedentes_delito SET 
                    id_causa = ?, codigo_delito = ?, fecha_delito = ?, hora_delito = ?, 
                    lugar_ocurrencia = ?, lugar_ocurrencia_otro = ?, comuna = ?, unidad = ?, 
                    cuadrante = ?
                WHERE id_antecedentes_delito = ?
                ''', (
                antecedente.id_causa,
                antecedente.codigo_delito,
                antecedente.fecha_delito,
                antecedente.hora_delito,
                antecedente.lugar_ocurrencia,
                antecedente.lugar_ocurrencia_otro,
                antecedente.comuna,
                antecedente.unidad,
                antecedente.cuadrante,
                id_antecedente_delito
            ))
            await conexion.commit()

    async def delete_antecedente_policial(self, id_antecedente_delito):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                DELETE FROM antecedentes_delito WHERE id_antecedentes_delito = ?
                ''', (id_antecedente_delito,))
            await conexion.commit()

    async def existe_antecedente_delito(self, id_antecedente_delito):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM antecedentes_delito WHERE id_antecedentes_delito = ?",
                (id_antecedente_delito,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None

    # CRUD: Medida policial

    async def add_medida_policial(self, id_antecedentes_policial, medida_policial: MedidaCautelarEspecial):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
            INSERT INTO medidas_policiales (id_antecedentes_delito, tipo_medida, respuesta, plazo, interpone_recurso, demanda_reconvencional)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
            id_antecedentes_policial,
            medida_policial.tipo_medida,
            medida_policial.respuesta,
            medida_policial.plazo,
            medida_policial.interpone_recurso,  
            medida_policial.demanda_reconvencional
            ))
            await conexion.commit()

    async def update_medida_policial(self, id_medida_policial, medida_policial: MedidaCautelarEspecial):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
            UPDATE medidas_policiales SET
                id_antecedentes_delito = ?,
                tipo_medida = ?,
                respuesta = ?,
                plazo = ?,
                interpone_recurso = ?,
                demanda_reconvencional = ?
            WHERE id_medida_policial = ?
            ''', (
            medida_policial.id_evento,  # Agregar el id_evento en la posición adecuada
            medida_policial.tipo_medida,
            medida_policial.respuesta,
            medida_policial.plazo,
            medida_policial.interpone_recurso,
            medida_policial.demanda_reconvencional,
            id_medida_policial
            ))
            await conexion.commit()

    async def delete_medida_policial(self, id_medida_policial):
        async with aiosqlite.connect(self.db_name) as conexion:
            await conexion.execute('''
                DELETE FROM medidas_policiales WHERE id_medida_policial = ?
                ''', (id_medida_policial,))
            await conexion.commit()

    async def existe_medida_policial(self, id_medida_policial):
        async with aiosqlite.connect(self.db_name) as conexion:
            cursor = await conexion.execute(
                "SELECT 1 FROM medidas_policiales WHERE id_medida_policial = ?",
                (id_medida_policial,)
            )
            resultado = await cursor.fetchone()
            return resultado is not None


# Visualización
    # Causas

    async def get_causas_by_columns(self, columns: list):
        try:
            if not columns:  # Si la lista está vacía, devuelve todo
                query = "SELECT * FROM CAUSA"
            else:
                selected_columns = ", ".join(columns)
                query = f"SELECT {selected_columns} FROM CAUSA"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query)
                causas = await cursor.fetchall()
            return causas
        except Exception as e:
            print(f"Error al obtener causas por columnas: {e}")
            return []   # Devuelve una lista vacía

    async def get_causa_by_id(self, id_causa: int):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute("SELECT * FROM CAUSA WHERE ID_Causa=?", (id_causa,))
                causa = await cursor.fetchone()  # Obtiene una sola fila ya que el ID es único
            return causa
        except Exception as e:  # Captura cualquier excepción genérica
            # Puedes cambiar el print por un logging o cualquier otra forma de reporte que prefieras.
            print(f"Error al obtener la causa por ID: {e}")
            return None  # Devuelve None si no se encontró la causa o hubo un error
    # Victimas

    async def get_victimas_by_causa(self, columns: list, id_causa: int):
        try:
            selected_columns = ", ".join(columns)
            query = f"SELECT {selected_columns} FROM VICTIMA WHERE id_causa = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_causa,))
                victimas = await cursor.fetchall()
            return victimas
        except Exception as e:
            print(f"Error al obtener víctimas por causa: {e}")
            return []

    async def get_victima_by_id(self, id_victima: int):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute("SELECT * FROM VICTIMA WHERE id_victima=?", (id_victima,))
                victima = await cursor.fetchone()  # Obtiene una sola fila ya que el ID es único
            return victima
        except Exception as e:  # Captura cualquier excepción genérica
            print(f"Error al obtener la víctima por ID: {e}")
            return None  # Devuelve None si no se encontró la víctima o hubo un error
        
    # Composición familiar

    async def get_family_composition_by_id(self, id_family_composition: int):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = '''
                    SELECT id_composicion, id_victima, tipo_relacion, respuesta, cantidad
                    FROM composicion_hogar
                    WHERE id_composicion=?
                '''
                cursor = await conexion.execute(query, (id_family_composition,))
                composicion = await cursor.fetchone()  # Obtiene una sola fila
                return composicion
        except Exception as e:
            print(f"Error al obtener la composición familiar por ID: {e}")
            return None

    async def get_composicion_familiar_por_victima(self, id_victima: int):
        try:
            query = """
                SELECT id_composicion, tipo_relacion, respuesta ,cantidad
                FROM composicion_hogar
                WHERE id_victima = ?
            """
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_victima,))
                composicion_familiar = await cursor.fetchall()
            return composicion_familiar
        except Exception as e:
            print(f"Error al obtener la composición familiar por víctima: {e}")
            return []
    # Denunciado

    async def get_denunciado_by_id(self, id_denunciado: int):
        try:
            query = "SELECT * FROM denunciado WHERE id_denunciado = ?"
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_denunciado,))
                denunciado = await cursor.fetchone()
            return denunciado
        except Exception as e:
            print(f"Error al obtener denunciado por ID: {e}")
            return None

    async def get_denunciados_by_causa(self, columns: list, id_causa: int):
        try:
            if not columns:  # Si la lista está vacía, devuelve todo
                query = "SELECT * FROM denunciado WHERE id_causa = ?"
            else:
                selected_columns = ", ".join(columns)
                query = f"SELECT {selected_columns} FROM denunciado WHERE id_causa = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_causa,))
                denunciados = await cursor.fetchall()
            return denunciados
        except Exception as e:
            print(f"Error al obtener denunciados por causa: {e}")
            return []  # Devuelve una lista vacía

    # indicadores de riesgo denunciado

    async def get_indicador_riesgo_vif_by_id(self, id_riesgo_vif: int):
        try:
            query = "SELECT * FROM denunciado_indicadores_riesgo_vif WHERE id_riesgo_vif = ?"
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_riesgo_vif,))
                indicador_riesgo_vif = await cursor.fetchone()
            return indicador_riesgo_vif
        except Exception as e:
            print(f"Error al obtener el indicador de riesgo VIF por ID: {e}")
            return None

    async def get_indicadores_riesgo_vif_by_denunciado_id(self, columns: list, id_denunciado: int):
        try:
            if not columns:  # Si la lista está vacía, devuelve todas las columnas
                selected_columns = "*"
            else:
                selected_columns = ", ".join(columns)

            query = f"SELECT {selected_columns} FROM denunciado_indicadores_riesgo_vif WHERE id_denunciado = ?"
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_denunciado,))
                indicadores_riesgo_vif = await cursor.fetchall()
            return indicadores_riesgo_vif
        except Exception as e:
            print(
                f"Error al obtener indicadores de riesgo VIF por ID de denunciado: {e}")
            return []

    # Antecedentes del denunciado

    async def get_antecedente_by_id(self, id_antecedente: int):
        try:
            query = "SELECT * FROM denunciado_antecedentes WHERE id_antecedente = ?"
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_antecedente,))
                antecedente = await cursor.fetchone()
            return antecedente
        except Exception as e:
            print(f"Error al obtener el antecedente por ID: {e}")
            return None

    async def get_antecedentes_by_denunciado_id(self, columns: list, id_denunciado: int):
        try:
            if not columns:  # Si la lista está vacía, devuelve todas las columnas
                selected_columns = "*"
            else:
                selected_columns = ", ".join(columns)

            query = f"SELECT {selected_columns} FROM denunciado_antecedentes WHERE id_denunciado = ?"
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_denunciado,))
                antecedentes = await cursor.fetchall()
            return antecedentes
        except Exception as e:
            print(f"Error al obtener antecedentes por ID de denunciado: {e}")
            return []

    # Denunciastes

    async def get_denunciantes_by_id(self, tipo_relacion: int):
        try:
            query = "SELECT * FROM Denunciantes WHERE tipo_relacion = ?"
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (tipo_relacion,))
                denunciante = await cursor.fetchone()
            return denunciante
        except Exception as e:
            print(f"Error al obtener el denunciante por ID: {e}")
            return None

    async def get_denunciantes_by_causa(self, columns: list, id_causa: int):
        try:
            selected_columns = ", ".join(columns)
            query = f"SELECT {selected_columns} FROM Denunciantes WHERE ID_Causa = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_causa,))
                denunciantes = await cursor.fetchall()
            return denunciantes
        except Exception as e:
            print(f"Error al obtener denunciantes por causa: {e}")
            return []

    # Audencia de jucio:
    async def get_audiencia_juicio_by_causa(self, columns: list, id_causa: int):
        try:
            selected_columns = ", ".join(columns)
            query = f"SELECT {selected_columns} FROM audiencia_juicio WHERE ID_Causa = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_causa,))
                audiencias = await cursor.fetchall()
            return audiencias
        except Exception as e:
            print(f"Error al obtener audiencias de juicio por causa: {e}")
            return []

    async def get_audiencia_juicio_by_id(self, id_audiencia: int):
        try:
            query = "SELECT * FROM audiencia_juicio WHERE id_audiencia_juicio = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_audiencia,))
                audiencia = await cursor.fetchone()
            return audiencia
        except Exception as e:
            print(f"Error al obtener la audiencia de juicio por ID: {e}")
            return None

    # Audencia Preparatoria:

    async def get_audiencia_preparatoria_by_causa(self, columns: list, id_causa: int):
        try:
            selected_columns = ", ".join(columns)
            query = f"SELECT {selected_columns} FROM audiencia_preparatoria WHERE ID_Causa = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_causa,))
                audiencias = await cursor.fetchall()
            return audiencias
        except Exception as e:
            print(f"Error al obtener audiencias preparatorias por causa: {e}")
            return []

    async def get_audiencia_preparatoria_by_id(self, id_audiencia: int):
        try:
            query = "SELECT * FROM audiencia_preparatoria WHERE id_audiencia_preparatoria = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_audiencia,))
                audiencia = await cursor.fetchone()
            return audiencia
        except Exception as e:
            print(f"Error al obtener la audiencia preparatoria por ID: {e}")
            return None

    # Victimas y denunciados involucrados en la audencia preparatoria
    async def get_audiencia_preparatoria_relaciones_by_audiencia(self, columns: list, id_audiencia: int):
        try:
            selected_columns = ", ".join(columns)
            query = f"SELECT {selected_columns} FROM audiencia_preparatoria_relaciones WHERE id_audiencia_preparatoria = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_audiencia,))
                relaciones = await cursor.fetchall()
            return relaciones
        except Exception as e:
            print(
                f"Error al obtener relaciones de audiencia preparatoria por ID de audiencia: {e}")
            return []

    async def get_audiencia_preparatoria_relacion_by_id(self, id_relacion: int):
        try:
            query = "SELECT * FROM audiencia_preparatoria_relaciones WHERE id_audencia_preparatoria_relaciones = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_relacion,))
                relacion = await cursor.fetchone()
            return relacion
        except Exception as e:
            print(
                f"Error al obtener relación de audiencia preparatoria por ID: {e}")
            return None

    # Medidas cautelares de audencia preparatoria

    async def get_medidas_cautelares_by_audiencia_preparatoria(self, columns: list, id_audiencia_preparatoria: int):
        try:
            selected_columns = ", ".join(columns)
            query = f"SELECT {selected_columns} FROM medidas_cautelares_preparatoria WHERE id_audiencia_preparatoria = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_audiencia_preparatoria,))
                medidas = await cursor.fetchall()
            return medidas
        except Exception as e:
            print(
                f"Error al obtener medidas cautelares por audiencia preparatoria: {e}")
            return []

    async def get_medida_cautelar_preparatoria_by_id(self, id_medida_cautelar: int):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute("SELECT * FROM medidas_cautelares_preparatoria WHERE id_medida_cautelar = ?", (id_medida_cautelar,))
                medida = await cursor.fetchone()
            return medida
        except Exception as e:
            print(f"Error al obtener la medida cautelar por ID: {e}")
            return None

    async def get_audiencia_juicio_relaciones_by_audiencia(self, columns: list, id_audiencia_juicio: int):
        try:
            selected_columns = ", ".join(columns)
            query = f"SELECT {selected_columns} FROM audiencia_juicio_relaciones WHERE id_audiencia_juicio = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_audiencia_juicio,))
                relaciones = await cursor.fetchall()
            return relaciones
        except Exception as e:
            print(
                f"Error al obtener relaciones de audiencia de juicio por ID de audiencia: {e}")
            return []

    async def get_audiencia_juicio_relacion_by_id(self, id_relacion: int):
        try:
            query = "SELECT * FROM audiencia_juicio_relaciones WHERE id_audenciaJuicio_relaciones = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_relacion,))
                relacion = await cursor.fetchone()
            return relacion
        except Exception as e:
            print(
                f"Error al obtener la relación de audiencia de juicio por ID: {e}")
            return None

    # Composicion del hogar en el juicio

    async def get_composicion_hogar_en_juicio_by_audiencia(self, columns: list, id_audiencia_juicio: int):
        selected_columns = ", ".join(columns)
        query = f"SELECT {selected_columns} FROM composicion_hogar_en_juicio WHERE id_audiencia_juicio = ?"
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                async with conexion.execute(query, (id_audiencia_juicio,)) as cursor:
                    composiciones = await cursor.fetchall()
                    return composiciones
        except Exception as e:
            print(
                f"Error al obtener composiciones de hogar en juicio por ID de audiencia: {e}")
            # Considera retornar None o lanzar una excepción personalizada.
            return []

    async def get_composicion_hogar_en_juicio_by_id(self, id_composicion: int):
        try:
            query = "SELECT * FROM composicion_hogar_en_juicio WHERE id_composicion_actual = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_composicion,))
                composicion = await cursor.fetchone()
            return composicion
        except Exception as e:
            print(
                f"Error al obtener la composición de hogar en juicio por ID: {e}")
            return None
    # Obtener medidas provisorias del juicio

    async def get_medidas_provisorias_by_sentencia(self, columns: list, id_jucio: int):
        try:
            selected_columns = ", ".join(columns)
            query = f"SELECT {selected_columns} FROM medidas_provisorias_juicio WHERE id_jucio = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_jucio,))
                medidas = await cursor.fetchall()
            return medidas
        except Exception as e:
            print(f"Error al obtener medidas provisionales por sentencia: {e}")
            return []

    async def get_medida_provisoria_by_id(self, id_medida_sentencia: int):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute("SELECT * FROM medidas_provisorias_juicio WHERE id_medida_sentencia = ?", (id_medida_sentencia,))
                medida = await cursor.fetchone()
            return medida
        except Exception as e:
            print(f"Error al obtener la medida provisional por ID: {e}")
            return None

    # Obterner actecedentes de la causa

    async def get_antecedentes_delito_by_causa(self, columns: list, id_causa: int):
        try:
            selected_columns = ", ".join(columns)
            query = f"SELECT {selected_columns} FROM antecedentes_delito WHERE ID_Causa = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_causa,))
                antecedentes = await cursor.fetchall()
            return antecedentes
        except Exception as e:
            print(f"Error al obtener antecedentes del delito por causa: {e}")
            return []

    async def get_antecedente_delito_by_id(self, id_antecedente_delito: int):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute("SELECT * FROM antecedentes_delito WHERE id_antecedentes_delito = ?", (id_antecedente_delito,))
                antecedente = await cursor.fetchone()
            return antecedente
        except Exception as e:
            print(f"Error al obtener el antecedente del delito por ID: {e}")
            return None
    # Obtener medidas policiales

    async def get_medidas_policiales_by_antecedente_delito(self, columns: list, id_antecedente_delito: int):
        try:
            selected_columns = ", ".join(columns)
            query = f"SELECT {selected_columns} FROM medidas_policiales WHERE id_antecedentes_delito = ?"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query, (id_antecedente_delito,))
                medidas = await cursor.fetchall()
            return medidas
        except Exception as e:
            print(
                f"Error al obtener medidas policiales por antecedente del delito: {e}")
            return []

    async def get_medida_policial_by_id(self, id_medida_policial: int):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute("SELECT * FROM medidas_policiales WHERE id_medida_policial = ?", (id_medida_policial,))
                medida = await cursor.fetchone()
            return medida
        except Exception as e:
            print(f"Error al obtener la medida policial por ID: {e}")
            return None

    # KPI

    async def get_total_causas(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = '''
                    SELECT COUNT(*) FROM CAUSA;
                '''
                cursor = await conexion.execute(query)
                total_causas = await cursor.fetchone()
                return total_causas[0]
        except Exception as e:
            print(f"Error al obtener el total de causas: {e}")
            return None

    async def get_total_victimas(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = '''
                    SELECT 
                        (SELECT COUNT(*) FROM victima) +
                        (SELECT COUNT(*) FROM Denunciantes WHERE es_denunciante_victima = 'si') AS total_victimas;
                '''
                cursor = await conexion.execute(query)
                total_victimas = await cursor.fetchone()
                return total_victimas[0]
        except Exception as e:
            print(f"Error al obtener el total de víctimas: {e}")
            return None

    async def get_promedio_edad_denunciados(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = '''
                    SELECT AVG(Edad) FROM denunciado WHERE Edad > 0;
                '''
                cursor = await conexion.execute(query)
                resultado = await cursor.fetchone()
                return round(resultado[0], 1) if resultado[0] is not None else None
        except Exception as e:
            print(f"Error al obtener el promedio de edad de los denunciados: {e}")
            return None
    async def get_cantidad_denunciados(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = '''
                    SELECT COUNT(Edad) FROM denunciado WHERE Edad > 0;
                '''
                cursor = await conexion.execute(query)
                resultado = await cursor.fetchone()
                return resultado[0] if resultado[0] is not None else None
        except Exception as e:
            print(f"Error al obtener la cantidad de denunciados: {e}")
            return None

    async def get_desviacion_estandar_edad_denunciados(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                # Obtener el promedio
                query_promedio = '''
                    SELECT AVG(Edad) FROM denunciado WHERE Edad > 0;
                '''
                cursor = await conexion.execute(query_promedio)
                promedio = (await cursor.fetchone())[0]
                
                # Calcular la desviación estándar
                query_varianza = '''
                    SELECT Edad FROM denunciado WHERE Edad > 0;
                '''
                cursor = await conexion.execute(query_varianza)
                edades = await cursor.fetchall()
                varianza = sum([(edad[0] - promedio) ** 2 for edad in edades]) / len(edades)
                desviacion_estandar = math.sqrt(varianza)

                return round(desviacion_estandar, 1)
        except Exception as e:
            print(f"Error al obtener la desviación estándar de la edad de los denunciados: {e}")
            return None

    async def get_total_denunciados(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = '''
                    SELECT COUNT(*) FROM denunciado;
                '''
                cursor = await conexion.execute(query)
                total_denunciados = await cursor.fetchone()
                return total_denunciados[0]
        except Exception as e:
            print(f"Error al obtener el total de denunciados: {e}")
            return None

    async def get_porcentaje_adultos_mayores_victimas(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                # Calcula el total de víctimas
                query_total_victimas = 'SELECT COUNT(*) FROM victima;'
                cursor_total = await conexion.execute(query_total_victimas)
                total_victimas = await cursor_total.fetchone()
                total_victimas = total_victimas[0]

                # Calcula el total de denunciantes que son víctimas
                query_denunciantes_victimas = 'SELECT COUNT(*) FROM denunciantes WHERE es_denunciante_victima = "si";'
                cursor_denunciantes_victimas = await conexion.execute(query_denunciantes_victimas)
                total_denunciantes_victimas = await cursor_denunciantes_victimas.fetchone()
                total_denunciantes_victimas = total_denunciantes_victimas[0]

                # Suma los totales para obtener el total de víctimas incluyendo denunciantes que son víctimas
                total_victimas += total_denunciantes_victimas

                # Calcula el total de víctimas que son adultos mayores
                query_adultos_mayores = '''
                    SELECT COUNT(*) 
                    FROM (
                        SELECT Edad FROM victima WHERE Edad >= 60
                        UNION ALL
                        SELECT edad_denunciante FROM denunciantes WHERE es_denunciante_victima = "si" AND edad_denunciante >= 60
                    );
                '''
                cursor_adultos_mayores = await conexion.execute(query_adultos_mayores)
                total_adultos_mayores = await cursor_adultos_mayores.fetchone()
                total_adultos_mayores = total_adultos_mayores[0]

                if total_victimas > 0:
                    # Calcula el porcentaje
                    porcentaje_adultos_mayores = round(
                        (total_adultos_mayores / total_victimas) * 100, 2)
                    return porcentaje_adultos_mayores
                else:
                    return 0
        except Exception as e:
            print(
                f"Error al obtener el porcentaje de adultos mayores víctimas: {e}")
            return None


 # Actualizar opciones

    async def obtener_composicion_hogar_existentes(self, id_victima):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = f"SELECT tipo_relacion FROM composicion_hogar WHERE id_victima = {id_victima}"
                cursor = await conexion.execute(query)
                relaciones_existentes = [row[0] for row in await cursor.fetchall()]
                return relaciones_existentes
        except Exception as e:
            print(f"Error al obtener relaciones existentes: {e}")
            return []

    async def obtener_antecedentes_denunciado(self, id_denunciado):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = f"SELECT tipo_antecedente FROM denunciado_antecedentes WHERE id_denunciado = {id_denunciado}"
                cursor = await conexion.execute(query)
                antecedentes = await cursor.fetchall()
                # Devuelve solo los tipos de antecedentes como una lista de strings
                return [row[0] for row in antecedentes]
        except Exception as e:
            print(f"Error al obtener antecedentes: {e}")
            return []

    async def obtener_descripciones_indicadores_riesgo(self, id_denunciado):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = f"SELECT descripcion_indicador FROM denunciado_indicadores_riesgo_vif WHERE id_denunciado = {id_denunciado}"
                cursor = await conexion.execute(query)
                descripciones = await cursor.fetchall()
                # Devuelve solo las descripciones como una lista de strings
                return [row[0] for row in descripciones]
        except Exception as e:
            print(
                f"Error al obtener descripciones de indicadores de riesgo: {e}")
            return []

    async def obtener_tipos_medidas_cautelares_por_audiencia(self, id_audiencia):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = f"SELECT tipo_medida FROM medidas_cautelares_preparatoria WHERE id_audiencia_preparatoria = {id_audiencia}"
                cursor = await conexion.execute(query)
                tipos_medidas = [row[0] for row in await cursor.fetchall()]
                return tipos_medidas
        except Exception as e:
            print(
                f"Error al obtener tipos de medidas cautelares por audiencia: {e}")
            return []

    async def obtener_tipos_medidas_provisorias_por_juicio(self, id_juicio):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = f"SELECT tipo_medida FROM medidas_provisorias_juicio WHERE id_jucio = {id_juicio}"
                cursor = await conexion.execute(query)
                tipos_medidas = [row[0] for row in await cursor.fetchall()]
                return tipos_medidas
        except Exception as e:
            print(
                f"Error al obtener tipos de medidas provisorias por juicio: {e}")
            return []

    async def obtener_tipos_medidas_policiales_por_antecedente(self, id_antecedente):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = f"SELECT tipo_medida FROM medidas_policiales WHERE id_antecedentes_delito = {id_antecedente}"
                cursor = await conexion.execute(query)
                tipos_medidas = [row[0] for row in await cursor.fetchall()]
                return tipos_medidas
        except Exception as e:
            print(
                f"Error al obtener tipos de medidas policiales por antecedente: {e}")
            return []

    async def obtener_tipos_relacion_composicion_hogar_por_juicio(self, id_victima, id_juicio):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = f"""
                SELECT tipo_relacion 
                FROM composicion_hogar_en_juicio 
                WHERE id_audiencia_juicio  = {id_juicio} AND id_victima = {id_victima}
                """
                cursor = await conexion.execute(query)
                tipos_relacion = [row[0] for row in await cursor.fetchall()]
                return tipos_relacion
        except Exception as e:
            print(
                f"Error al obtener tipos de relación de la composición del hogar por juicio y víctima: {e}")
            return []

    async def obtener_ids_victimas_por_causa(self, id_causa):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = f"SELECT id_victima FROM victima WHERE id_causa = {id_causa}"
                cursor = await conexion.execute(query)
                ids_victimas = [row[0] for row in await cursor.fetchall()]
                return ids_victimas
        except Exception as e:
            print(f"Error al obtener IDs de víctimas: {e}")
            return []

    async def obtener_ids_denunciados_por_causa(self, id_causa):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = f"SELECT id_denunciado FROM denunciado WHERE id_causa = {id_causa}"
                cursor = await conexion.execute(query)
                ids_denunciados = [row[0] for row in await cursor.fetchall()]
                return ids_denunciados
        except Exception as e:
            print(f"Error al obtener IDs de denunciados: {e}")
            return []

    async def obtener_ids_denunciantes_por_causa(self, id_causa):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = f"SELECT tipo_relacion FROM denunciantes WHERE id_causa = {id_causa}"
                cursor = await conexion.execute(query)
                ids_denunciantes = [row[0] for row in await cursor.fetchall()]
                return ids_denunciantes
        except Exception as e:
            print(f"Error al obtener IDs de denunciantes: {e}")
            return []



#Este es especifico para la secccion de graficos
        

    async def get_all_denunciados(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                consulta = """
                SELECT 
                    d.id_causa,
                    CASE
                        WHEN d.edad BETWEEN 1 AND 17 THEN '1-17'
                        WHEN d.edad BETWEEN 19 AND 59 THEN '18-59'
                        WHEN d.edad >= 60 THEN '60+'
                        ELSE 'desconocido'
                    END AS grupo_edad,
                    d.sexo,
                    d.nacionalidad,
                    d.nacionalidad_Extranjera,
                    d.profesion_oficio,
                    d.estudios,
                    d.caracter_lesion,
                    d.lesiones_descripcion,
                    d.estado_temperancia,
                    d.temperancia_otro,
                    d.temperancia_descripcion,
                    d.otros_antecedentes,
                    d.comuna,
                    d.estado_civil,
                    d.nivel_riesgo,
                    SUBSTR(c.fecha_ingreso, -4) AS año_ingreso  -- Extraer el año desde el final
                FROM denunciado d
                JOIN causa c ON d.id_causa = c.id_causa;
                """
                cursor = await conexion.execute(consulta)
                denunciados = await cursor.fetchall()
                columnas = [descripcion[0] for descripcion in cursor.description]
                return denunciados, columnas
        except Exception as e:
            print(f"Error al obtener todos los denunciados: {e}")
            return None, []
        
    async def get_all_denunciado_antecedentes(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                consulta = """
                SELECT da.*, d.id_causa
                FROM denunciado_antecedentes da
                JOIN denunciado d ON da.id_denunciado = d.id_denunciado;
                """
                cursor = await conexion.execute(consulta)
                antecedentes = await cursor.fetchall()
                columnas = [descripcion[0] for descripcion in cursor.description]
                return antecedentes, columnas
        except Exception as e:
            print(f"Error al obtener antecedentes del denunciado: {e}")
            return None, []
        
    async def get_all_denunciado_riesgo_vif(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                consulta = """
                SELECT drv.*, d.id_causa
                FROM denunciado_indicadores_riesgo_vif drv
                JOIN denunciado d ON drv.id_denunciado = d.id_denunciado;
                """
                cursor = await conexion.execute(consulta)
                riesgo_vif = await cursor.fetchall()
                columnas = [descripcion[0] for descripcion in cursor.description]
                return riesgo_vif, columnas
        except Exception as e:
            print(f"Error al obtener indicadores de riesgo VIF del denunciado: {e}")
            return None, []

            
    async def get_all_denunciantes(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                consulta = """
                SELECT 
                    d.id_causa,
                    CASE
                        WHEN d.edad_denunciante BETWEEN 1 AND 17 THEN '1-17'
                        WHEN d.edad_denunciante BETWEEN 18 AND 59 THEN '18-59'
                        WHEN d.edad_denunciante >= 60 THEN '60+'
                        ELSE 'desconocido'
                    END AS grupo_edad,
                    d.es_denunciante_victima,
                    d.es_denunciante_persona_juridica,
                    d.nombre_persona_juridica,
                    d.sexo_denunciante AS sexo,
                    d.nacionalidad_denunciante AS nacionalidad,
                    d.nacionalidad_extranjera_denunciante AS nacionalidad_extranjera,
                    d.profesion_oficio_denunciante AS profesion_oficio,
                    d.estudios_denunciante AS estudios,
                    d.parentesco_acusado AS parentesco_acusado,
                    d.parentesco_acusado_otro AS parentesco_acusado_otro,
                    d.caracter_lesion_denunciante AS caracter_lesion,
                    d.descripcion_lesion_denunciante AS descripcion_lesion,
                    d.estado_temperancia_denunciante AS estado_temperancia,
                    d.estado_temperancia_denunciante_otro AS estado_temperancia_otro, 
                    d.descripcion_temperancia_denunciante AS descripcion_temperancia,
                    d.comuna AS comuna,
                    d.estado_civil AS estado_civil,
                    SUBSTR(c.fecha_ingreso, -4) AS año_ingreso
                FROM Denunciantes d
                JOIN causa c ON d.id_causa = c.id_causa;
                """
                cursor = await conexion.execute(consulta)
                denunciantes = await cursor.fetchall()
                columnas = [descripcion[0] for descripcion in cursor.description]
                return denunciantes, columnas
        except Exception as e:
            print(f"Error al obtener todos los denunciantes: {e}")
            return None, []

    async def get_all_victimas(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                consulta = """
                SELECT
                    v.id_causa,
                    CASE
                        WHEN v.edad BETWEEN 1 AND 17 THEN '1-17'
                        WHEN v.edad BETWEEN 19 AND 59 THEN '18-59'
                        WHEN v.edad >= 60 THEN '60+'
                        ELSE 'desconocido'
                    END AS grupo_edad,
                    v.sexo,
                    v.nacionalidad,
                    v.nacionalidad_extranjera,
                    v.profesion_oficio,
                    v.estudios,
                    v.parentesco_acusado,
                    v.parentesco_acusado_otro,
                    v.caracter_lesion,
                    v.descripcion_lesion,
                    v.estado_temperancia,
                    v.estado_temperancia_otro,
                    v.descripcion_temperancia,
                    v.comuna,
                    v.tiempo_relacion,
                    v.estado_civil,
                    v.parentesco_denunciante,
                    v.parentesco_denunciante_otro,
                    SUBSTR(c.fecha_ingreso, -4) AS año_ingreso
                FROM victima v
                JOIN causa c ON v.id_causa = c.id_causa;
                """
                cursor = await conexion.execute(consulta)
                victimas = await cursor.fetchall()
                columnas = [descripcion[0] for descripcion in cursor.description]
                await cursor.close()
                    
                return victimas, columnas
        except Exception as e:
            print(f"Error al obtener todas las víctimas: {e}")
            return None, []

    async def get_all_audiencias(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                consulta = """
                SELECT 
                    c.id_causa,
                    ap.fecha_citacion AS fecha_citacion_preparatoria,
                    ap.fecha_realizacion AS fecha_realizacion_preparatoria,
                    ap.suspension_anterior AS suspension_anterior_preparatoria,
                    ap.solicita_informes_oficios AS solicita_informes_oficios_preparatoria,
                    ap.resolucion AS resolucion_preparatoria,
                    ap.salida_colaborativa AS salida_colaborativa_preparatoria,
                    ap.otras_observaciones AS otras_observaciones_preparatoria,
                    aja.fecha_citacion AS fecha_citacion_juicio,
                    aja.fecha_realizacion AS fecha_realizacion_juicio,
                    aja.cambio_composicion_hogar AS cambio_composicion_hogar_juicio,
                    aja.suspendido AS suspendido_juicio,
                    aja.resolucion AS resolucion_juicio,
                    aja.sentencia AS sentencia_juicio,
                    aja.salida_colaborativa AS salida_colaborativa_juicio,
                    aja.carabineros_informa_cese_medidas AS carabineros_informa_cese_medidas_juicio,
                    aja.recurso_procesal AS recurso_procesal_juicio,
                    aja.recurso_procesal_otro AS recurso_procesal_otro_juicio,
                    aja.abre_causa_cumplimiento AS abre_causa_cumplimiento_juicio
                FROM causa c
                LEFT JOIN audiencia_preparatoria ap ON c.id_causa = ap.id_causa
                LEFT JOIN audiencia_juicio aja ON c.id_causa = aja.id_causa;
                """
                cursor = await conexion.execute(consulta)
                audiencias = await cursor.fetchall()
                columnas = [descripcion[0] for descripcion in cursor.description]
                return audiencias, columnas
        except Exception as e:
            print(f"Error al obtener datos de audiencias: {e}")
            return None, []



    async def get_all_antecedentes_delito(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                consulta = '''
                SELECT ad.*
                FROM antecedentes_delito ad;
                '''
                cursor = await conexion.execute(consulta)
                antecedentes_delito = await cursor.fetchall()
                columnas = [descripcion[0] for descripcion in cursor.description]
                return antecedentes_delito, columnas
        except Exception as e:
            print(f"Error al obtener antecedentes del delito: {e}")
            return None, []

        
    async def get_all_medidas_policiales(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                consulta = '''
                SELECT mp.*, ad.id_causa
                FROM medidas_policiales mp
                JOIN antecedentes_delito ad ON mp.id_antecedentes_delito = ad.id_antecedentes_delito;
                '''
                cursor = await conexion.execute(consulta)
                medidas_policiales = await cursor.fetchall()
                columnas = [descripcion[0] for descripcion in cursor.description]
                return medidas_policiales, columnas
        except Exception as e:
            print(f"Error al obtener medidas policiales: {e}")
            return None, []
        
    async def get_all_medidas_cautelares_preparatorias(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                consulta = '''
                SELECT mcp.*, ap.id_causa
                FROM medidas_cautelares_preparatoria mcp
                JOIN audiencia_preparatoria ap ON mcp.id_audiencia_preparatoria = ap.id_audiencia_preparatoria;
                '''
                cursor = await conexion.execute(consulta)
                medidas_cautelares = await cursor.fetchall()
                columnas = [descripcion[0] for descripcion in cursor.description]
                return medidas_cautelares, columnas
        except Exception as e:
            print(f"Error al obtener medidas cautelares preparatorias: {e}")
            return None, []
        
    async def get_all_medidas_provisorias_juicio(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                consulta = '''
                SELECT mpj.*, aj.id_causa
                FROM medidas_provisorias_juicio mpj
                JOIN audiencia_juicio aj ON mpj.id_jucio = aj.id_audiencia_juicio;
                '''
                cursor = await conexion.execute(consulta)
                medidas_provisorias = await cursor.fetchall()
                columnas = [descripcion[0] for descripcion in cursor.description]
                return medidas_provisorias, columnas
        except Exception as e:
            print(f"Error al obtener medidas provisorias de juicio: {e}")
            return None, []


    async def get_causas_by_columns_new(self, columns: list, pagina, filas_por_pagina=50):
        offset = (pagina - 1) * filas_por_pagina
        try:
            if not columns:  # Si la lista está vacía, devuelve todo
                query = f"SELECT * FROM CAUSA LIMIT {filas_por_pagina} OFFSET {offset}"
            else:
                selected_columns = ", ".join(columns)
                query = f"SELECT {selected_columns} FROM CAUSA LIMIT {filas_por_pagina} OFFSET {offset}"

            async with aiosqlite.connect(self.db_name) as conexion:
                cursor = await conexion.execute(query)
                causas = await cursor.fetchall()
            return causas
        except Exception as e:
            print(f"Error al obtener causas por columnas: {e}")
            return []   # Devuelve una lista vacía


    # En tu clase de base de datos
    async def get_total_causas_count(self):
        try:
            async with aiosqlite.connect(self.db_name) as conexion:
                query = "SELECT COUNT(*) FROM CAUSA"
                cursor = await conexion.execute(query)
                (total_causas_count,) = await cursor.fetchone()
                return total_causas_count
        except Exception as e:
            print(f"Error al obtener el conteo total de causas: {e}")
            return 0