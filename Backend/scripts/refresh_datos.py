"""
Reemplazo de datos transaccionales legacy por un set nuevo, coherente y ya atendido.
Borra 13 tablas en orden de dependencia (en una conexión aislada) y conserva
usuarios/vets/admins/recepcionistas y catálogos. Genera ~30 clientes, ~45 mascotas
y ~25 casos con la cadena clínica completa cerrada, más solicitudes pendientes.
También reinicia y siembra el cronograma (horario recurrente + excepciones).

Nota: el borrado usa ALTER TABLE (commit implícito en MySQL); se hace en su propia
conexión y la generación en una sesión ORM nueva para evitar corromper la unit-of-work.

Uso (destructivo): se conecta a la BD de DATABASE_URL (Backend/.env). Antes de correr
en producción, aplicar las migraciones 011 (razas) y 012 (trigger corregido) y hacer
backup. Depende de que el trigger before_diagnostico_insert ya cree el Tratamiento.
    cd Backend && python scripts/refresh_datos.py
"""
import sys, os, random
from datetime import datetime, timedelta
# Backend/ (dos niveles arriba de este archivo) para importar `app`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import SessionLocal, engine
from sqlalchemy import text
from app.models.clientes import Cliente
from app.models.mascota import Mascota
from app.models.cliente_mascota import ClienteMascota
from app.models.solicitud_atencion import SolicitudAtencion
from app.models.triaje import Triaje
from app.models.consulta import Consulta
from app.models.diagnostico import Diagnostico
from app.models.servicio_solicitado import ServicioSolicitado
from app.models.cita import Cita
from app.models.resultado_servicio import ResultadoServicio
from app.models.historial_clinico import HistorialClinico
from app.models.movimiento_financiero import MovimientoFinanciero
from app.models.horario_veterinario import HorarioVeterinario
from app.models.horario_excepcion import HorarioExcepcion
from app.models.horario_recepcionista import HorarioRecepcionista
from app.models.horario_excepcion_recep import HorarioExcepcionRecep

random.seed(2026)

# ============================================================
# 1) BORRADO en conexión aislada (evita mezclar DDL con el ORM)
# ============================================================
orden_borrado = [
    "Historial_clinico", "Movimiento_financiero", "Resultado_servicio",
    "Diagnostico", "Tratamiento", "Cita", "Servicio_Solicitado",
    "Consulta", "Triaje", "Solicitud_atencion", "Cliente_Mascota",
    "Mascota", "Cliente",
]
with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    for t in orden_borrado:
        conn.execute(text(f"DELETE FROM `{t}`"))
        conn.execute(text(f"ALTER TABLE `{t}` AUTO_INCREMENT = 1"))
    # Limpieza de las patologías sin nombre (basura acumulada por el trigger viejo).
    conn.execute(text("DELETE FROM Patologia WHERE nombre_patologia IS NULL OR nombre_patologia = ''"))
    conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

# ============================================================
# 2) GENERACIÓN en una sesión ORM nueva y limpia
# ============================================================
db = SessionLocal()

# --- IDs de referencia (se conservan) ---
vet_ids = [r[0] for r in db.execute(text("SELECT id_veterinario FROM Veterinario")).fetchall()]
recep_ids = [r[0] for r in db.execute(text("SELECT id_recepcionista FROM Recepcionista")).fetchall()]
admin_ids = [r[0] for r in db.execute(text("SELECT id_administrador FROM Administrador")).fetchall()]
servicios = db.execute(text("SELECT id_servicio, nombre_servicio, precio FROM Servicio WHERE activo=1")).fetchall()
patologias = [r[0] for r in db.execute(text("SELECT id_patologia FROM Patologia")).fetchall()]
razas = db.execute(text("SELECT r.id_raza, ta.descripcion FROM Raza r JOIN Tipo_animal ta ON ta.id_raza = r.id_raza")).fetchall()
razas_perro = [r[0] for r in razas if r[1] == 'Perro']
razas_gato = [r[0] for r in razas if r[1] == 'Gato']

nombres_m = ["José","Luis","Carlos","Juan","Miguel","Jorge","Pedro","Manuel","Fernando","Ricardo","Andrés","Sergio","Raúl","Óscar","Iván"]
nombres_f = ["María","Ana","Rosa","Carmen","Lucía","Elena","Patricia","Sofía","Valeria","Camila","Daniela","Gabriela","Andrea","Paula","Claudia"]
apellidos = ["García","Rodríguez","Martínez","López","González","Pérez","Sánchez","Ramírez","Torres","Flores","Rivera","Gómez","Díaz","Vargas","Castro","Romero","Mendoza","Ruiz","Herrera","Chávez"]
nombres_perro = ["Rocky","Max","Toby","Zeus","Simba","Bruno","Thor","Duke","Rex","Bobby","Firulais","Pancho","Coco","Lucas","Benji"]
nombres_gato = ["Luna","Nina","Kira","Maya","Chloe","Mia","Sasha","Pelusa","Michi","Manchas","Nala","Tom","Lola","Bella","Copito"]
colores = ["Marrón","Negro","Blanco","Dorado","Gris","Atigrado","Tricolor","Canela","Crema","Negro y Blanco"]
condicion_gen = ['Excelente','Buena','Regular','Mala','Critica']
cond_corporal = ['Muy delgado','Delgado','Ideal','Sobrepeso','Obeso']
urgencias = ['No urgente','Poco urgente','Urgente','Muy urgente','Critico']
tipos_diag = ['Presuntivo','Confirmado','Descartado']
estados_pat = ['Activa','Controlada','Curada','En seguimiento']
tipos_trat = ['Medicamentoso','Quirurgico','Terapeutico','Preventivo']
eficacias = ['Muy buena','Buena','Regular','Mala']

def dni(i): return f"{40000000 + i:08d}"
def quita_tildes(s):
    for a, b in [("é","e"),("í","i"),("ó","o"),("á","a"),("ú","u")]:
        s = s.replace(a, b)
    return s

# --- Clientes (15) ---
N_CLIENTES = 30
clientes = []
for i in range(N_CLIENTES):
    genero = random.choice(['M', 'F'])
    nom = random.choice(nombres_m if genero == 'M' else nombres_f)
    ap, am = random.choice(apellidos), random.choice(apellidos)
    c = Cliente(
        nombre=nom, apellido_paterno=ap, apellido_materno=am,
        dni=dni(i), telefono=f"9{10000000 + i*13 % 89999999:08d}",
        email=quita_tildes(f"{nom.lower()}.{ap.lower()}{i}@example.com"),
        direccion=f"Av. Los Álamos {100 + i*7}, Lima",
        estado='Activo', genero=genero,
    )
    db.add(c); clientes.append(c)
db.flush()

# --- Mascotas (20) + vínculo a un cliente ---
N_MASCOTAS = 45
mascotas = []
for i in range(N_MASCOTAS):
    es_perro = random.random() < 0.6
    m = Mascota(
        id_raza=random.choice(razas_perro if es_perro else razas_gato),
        nombre=random.choice(nombres_perro if es_perro else nombres_gato),
        sexo=random.choice(['Macho', 'Hembra']),
        color=random.choice(colores),
        edad_anios=random.randint(0, 14), edad_meses=random.randint(0, 11),
        esterilizado=random.choice([True, False]),
    )
    db.add(m); mascotas.append(m)
db.flush()
for m in mascotas:
    db.add(ClienteMascota(id_cliente=random.choice(clientes).id_cliente, id_mascota=m.id_mascota))
db.flush()

# --- Casos clínicos: 12 atendidos + 3 pendientes ---
N_ATENDIDOS, N_PENDIENTES = 25, 8
hoy = datetime(2026, 7, 13)

for idx in range(N_ATENDIDOS):
    m = mascotas[idx]
    vet = random.choice(vet_ids)
    f_sol = hoy - timedelta(days=random.randint(20, 400), hours=random.randint(0, 8))
    edad_meses_tot = (m.edad_anios or 0) * 12 + (m.edad_meses or 0)

    sol = SolicitudAtencion(id_mascota=m.id_mascota, id_recepcionista=random.choice(recep_ids),
        fecha_hora_solicitud=f_sol,
        tipo_solicitud=random.choice(['Consulta urgente','Consulta normal','Servicio programado']),
        estado='Completada')
    db.add(sol); db.flush()

    tri = Triaje(id_solicitud=sol.id_solicitud, id_veterinario=vet,
        fecha_hora_triaje=f_sol + timedelta(minutes=20),
        peso_mascota=round(random.uniform(2,45),2), latido_por_minuto=random.randint(70,160),
        frecuencia_respiratoria_rpm=random.randint(15,40), temperatura=round(random.uniform(37.5,39.5),2),
        talla=round(random.uniform(20,70),2), tiempo_capilar="< 2 seg", color_mucosas="Rosadas",
        frecuencia_pulso=random.randint(70,160), porce_deshidratacion=round(random.uniform(0,6),2),
        condicion_corporal=random.choice(cond_corporal), clasificacion_urgencia=random.choice(urgencias))
    db.add(tri); db.flush()
    peso_triaje = float(tri.peso_mascota)

    cons = Consulta(id_triaje=tri.id_triaje, id_veterinario=vet,
        tipo_consulta=random.choice(['Consulta general','Consulta especializada','Consulta de control']),
        fecha_consulta=f_sol + timedelta(minutes=45),
        motivo_consulta="Control y evaluación general de la mascota",
        sintomas_observados="Sin síntomas de alarma al momento de la evaluación",
        diagnostico_preliminar="Paciente en condiciones clínicas dentro de lo esperado",
        observaciones="Continuar con controles periódicos",
        condicion_general=random.choice(condicion_gen), es_seguimiento=random.choice([True, False]))
    db.add(cons); db.flush()

    pat = random.choice(patologias)
    # El trigger before_diagnostico_insert (corregido, SC-064) crea el Tratamiento
    # asociado con esta misma patología, por eso NO se inserta aquí manualmente.
    diag = Diagnostico(id_consulta=cons.id_consulta, id_patologia=pat,
        tipo_diagnostico=random.choice(tipos_diag), fecha_diagnostico=cons.fecha_consulta,
        estado_patologia=random.choice(estados_pat),
        diagnostico="Hallazgos compatibles con la patología registrada; se indica manejo.")
    db.add(diag); db.flush()

    serv = random.choice(servicios)
    # Estado de la cita: mayoría atendida, algunas canceladas o programadas (futuras).
    outcome = random.choices(['Atendida', 'Cancelada', 'Programada'], weights=[68, 18, 14])[0]
    estado_examen = {'Atendida': 'Completado', 'Cancelada': 'Citado', 'Programada': 'Citado'}[outcome]
    if outcome == 'Programada':
        fecha_cita = hoy + timedelta(days=random.randint(1, 20))
        obs_cita = "Cita programada, pendiente de atención."
    elif outcome == 'Cancelada':
        fecha_cita = cons.fecha_consulta + timedelta(days=random.randint(1, 5))
        obs_cita = "Cita cancelada por el cliente."
    else:
        fecha_cita = cons.fecha_consulta + timedelta(days=random.randint(1, 5))
        obs_cita = "Cita atendida correctamente."

    ss = ServicioSolicitado(id_consulta=cons.id_consulta, id_servicio=serv[0],
        fecha_solicitado=cons.fecha_consulta, prioridad=random.choice(['Urgente','Normal','Programable']),
        estado_examen=estado_examen, comentario_opcional="Servicio registrado en la consulta.")
    db.add(ss); db.flush()

    cita = Cita(id_mascota=m.id_mascota, id_servicio_solicitado=ss.id_servicio_solicitado, id_veterinario=vet,
        fecha_hora_programada=fecha_cita, estado_cita=outcome,
        requiere_ayuno=random.choice([True, False]), observaciones=obs_cita)
    db.add(cita); db.flush()

    # La consulta ocurrió: siempre se registra en el historial.
    db.add(HistorialClinico(id_mascota=m.id_mascota, id_consulta=cons.id_consulta, id_veterinario=vet,
        fecha_evento=cons.fecha_consulta, tipo_evento="Consulta médica", edad_meses=edad_meses_tot,
        descripcion_evento="Consulta general con evaluación clínica completa.",
        peso_momento=round(peso_triaje,2), observaciones="Evolución favorable."))
    db.add(HistorialClinico(id_mascota=m.id_mascota, id_diagnostico=diag.id_diagnostico, id_veterinario=vet,
        fecha_evento=cons.fecha_consulta, tipo_evento="Diagnóstico",
        descripcion_evento="Registro de diagnóstico y plan terapéutico."))

    # Solo las citas atendidas generan resultado del servicio e ingreso.
    if outcome == 'Atendida':
        db.add(ResultadoServicio(id_cita=cita.id_cita, id_veterinario=vet,
            resultado=f"Resultado del servicio {serv[1]}: dentro de parámetros normales.",
            interpretacion="Sin hallazgos que requieran intervención adicional.",
            fecha_realizacion=cita.fecha_hora_programada))
        db.add(MovimientoFinanciero(tipo='Ingreso', categoria='Servicio', monto=serv[2],
            concepto=f"Pago del servicio {serv[1]}", fecha_movimiento=cita.fecha_hora_programada,
            id_cita=cita.id_cita, id_administrador=random.choice(admin_ids)))
    db.flush()

for idx in range(N_ATENDIDOS, N_ATENDIDOS + N_PENDIENTES):
    m = mascotas[idx]
    db.add(SolicitudAtencion(id_mascota=m.id_mascota, id_recepcionista=random.choice(recep_ids),
        fecha_hora_solicitud=hoy - timedelta(days=random.randint(0,4)),
        tipo_solicitud=random.choice(['Consulta urgente','Consulta normal']), estado='Pendiente'))

# Egresos (gastos operativos y de nómina) para tener también salidas de dinero.
EGRESOS = [
    ("Compra de insumos médicos", 'Operativo', (300, 1500)),
    ("Alquiler del local", 'Operativo', (1800, 2500)),
    ("Servicios: luz, agua e internet", 'Operativo', (400, 900)),
    ("Mantenimiento de equipos", 'Operativo', (200, 800)),
    ("Compra de alimento y accesorios", 'Operativo', (500, 2000)),
    ("Pago de planilla de veterinarios", 'Nomina', (4000, 9000)),
    ("Pago de planilla de recepcionistas", 'Nomina', (2500, 5000)),
    ("Publicidad y marketing", 'Operativo', (150, 700)),
]
for _ in range(18):
    concepto, cat, (lo, hi) = random.choice(EGRESOS)
    db.add(MovimientoFinanciero(tipo='Egreso', categoria=cat, monto=round(random.uniform(lo, hi), 2),
        concepto=concepto, fecha_movimiento=hoy - timedelta(days=random.randint(0, 180)),
        id_cita=None, id_administrador=random.choice(admin_ids)))
db.commit()
db.close()

# ============================================================
# 3) CRONOGRAMA: horario recurrente semanal + algunas excepciones
# ============================================================
with engine.begin() as conn:
    conn.execute(text("DELETE FROM Horario_excepcion"))
    conn.execute(text("DELETE FROM Horario_veterinario"))
    conn.execute(text("ALTER TABLE Horario_excepcion AUTO_INCREMENT = 1"))
    conn.execute(text("ALTER TABLE Horario_veterinario AUTO_INCREMENT = 1"))

hdb = SessionLocal()
vets_turno = hdb.execute(text("SELECT id_veterinario, turno FROM Veterinario")).fetchall()
DIAS_SEM = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
# Recurrente: cada vet trabaja su turno de Lunes a Viernes; ~40% también Sábado.
for vid, turno in vets_turno:
    dias = DIAS_SEM[:5] + (['Sabado'] if random.random() < 0.4 else [])
    for d in dias:
        hdb.add(HorarioVeterinario(id_veterinario=vid, dia_semana=d, turno=turno))
hdb.flush()

# Excepciones: días libres / turnos extra en fechas cercanas a hoy.
turnos_all = ['Mañana', 'Tarde', 'Noche', 'Madrugada']
usados, creadas, intentos = set(), 0, 0
while creadas < 12 and intentos < 80:
    intentos += 1
    vid = random.choice(vets_turno)[0]
    fecha = (hoy + timedelta(days=random.randint(-3, 14))).date()
    if (vid, fecha) in usados:
        continue
    usados.add((vid, fecha))
    trabaja = random.random() < 0.5
    hdb.add(HorarioExcepcion(id_veterinario=vid, fecha=fecha,
                             turno=random.choice(turnos_all) if trabaja else None, trabaja=trabaja))
    creadas += 1
hdb.commit()
hdb.close()

# Cronograma de recepcionistas (mismo patrón).
with engine.begin() as conn:
    conn.execute(text("DELETE FROM Horario_excepcion_recep"))
    conn.execute(text("DELETE FROM Horario_recepcionista"))
    conn.execute(text("ALTER TABLE Horario_excepcion_recep AUTO_INCREMENT = 1"))
    conn.execute(text("ALTER TABLE Horario_recepcionista AUTO_INCREMENT = 1"))

rdb = SessionLocal()
recep_turno = rdb.execute(text("SELECT id_recepcionista, COALESCE(turno,'Mañana') FROM Recepcionista")).fetchall()
for rid, turno in recep_turno:
    dias = DIAS_SEM[:5] + (['Sabado'] if random.random() < 0.4 else [])
    for d in dias:
        rdb.add(HorarioRecepcionista(id_recepcionista=rid, dia_semana=d, turno=turno))
rdb.flush()
usados, creadas, intentos = set(), 0, 0
while creadas < 8 and intentos < 60:
    intentos += 1
    rid = random.choice(recep_turno)[0]
    fecha = (hoy + timedelta(days=random.randint(-3, 14))).date()
    if (rid, fecha) in usados:
        continue
    usados.add((rid, fecha))
    trabaja = random.random() < 0.5
    rdb.add(HorarioExcepcionRecep(id_recepcionista=rid, fecha=fecha,
                                  turno=random.choice(turnos_all) if trabaja else None, trabaja=trabaja))
    creadas += 1
rdb.commit()
rdb.close()

# --- Verificación con sesión independiente ---
chk = SessionLocal()
print("REEMPLAZO COMPLETADO:")
for t in ["Cliente","Mascota","Cliente_Mascota","Solicitud_atencion","Triaje","Consulta",
          "Diagnostico","Tratamiento","Servicio_Solicitado","Cita","Resultado_servicio",
          "Historial_clinico","Movimiento_financiero","Horario_veterinario","Horario_excepcion",
          "Horario_recepcionista","Horario_excepcion_recep"]:
    print(f"  {t}: {chk.execute(text(f'SELECT COUNT(*) FROM {t}')).scalar()}")
chk.close()
