// utils/apiError.js
// Convierte cualquier error del backend (o de red) en un mensaje CORTO y amigable
// para mostrar en un toast, evitando volcar el error crudo de la BD o el array
// gigante de validación de Pydantic (422).
//
// Uso típico en un handler:
//   const body = await response.json().catch(() => null);
//   toast.error(formatApiError(body, 'No se pudo registrar la cita'));

// Etiquetas amigables para los campos más comunes (loc de Pydantic / columnas).
const FIELD_LABELS = {
  nombre: 'Nombre',
  apellido_paterno: 'Apellido paterno',
  apellido_materno: 'Apellido materno',
  dni: 'DNI',
  telefono: 'Teléfono',
  email: 'Correo electrónico',
  direccion: 'Dirección',
  genero: 'Género',
  fecha_nacimiento: 'Fecha de nacimiento',
  precio: 'Precio',
  nombre_servicio: 'Nombre del servicio',
  id_tipo_servicio: 'Tipo de servicio',
  fecha_hora_programada: 'Fecha y hora',
  fecha_hora_solicitud: 'Fecha y hora',
  id_mascota: 'Mascota',
  id_cliente: 'Cliente',
  id_servicio: 'Servicio',
  id_servicio_solicitado: 'Servicio solicitado',
  id_veterinario: 'Veterinario',
  id_recepcionista: 'Recepcionista',
  id_raza: 'Raza',
  id_especialidad: 'Especialidad',
  tipo_solicitud: 'Tipo de solicitud',
  tipo_consulta: 'Tipo de consulta',
  motivo_consulta: 'Motivo de la consulta',
  condicion_general: 'Condición general',
  peso_mascota: 'Peso',
  temperatura: 'Temperatura',
  latido_por_minuto: 'Latidos por minuto',
  frecuencia_respiratoria_rpm: 'Frecuencia respiratoria',
  frecuencia_pulso: 'Frecuencia de pulso',
  clasificacion_urgencia: 'Clasificación de urgencia',
  edad_anios: 'Edad (años)',
  edad_meses: 'Edad (meses)',
  sexo: 'Sexo',
  color: 'Color',
  observaciones: 'Observaciones',
  codigo_CMVP: 'Código CMVP',
  turno: 'Turno',
  monto: 'Monto',
  concepto: 'Concepto',
  categoria: 'Categoría',
};

const MAX_LEN = 160;

// Detecta mensajes técnicos que no deben mostrarse al usuario (errores de BD,
// trazas, drivers, etc.). En esos casos se usa el texto de respaldo genérico.
function looksTechnical(msg) {
  if (!msg) return false;
  if (msg.length > MAX_LEN) return true;
  return /base de datos|pymysql|sqlalchemy|traceback|integrityerror|operationalerror|programmingerror|foreign key|constraint|1064|1054|1452|\bSQL\b|str\(e\)|<class|at 0x/i.test(msg);
}

function cleanMsg(s) {
  return String(s).replace(/^Value error,\s*/i, '').trim();
}

export function truncate(s, n = 180) {
  const str = String(s ?? '').replace(/\s+/g, ' ').trim();
  return str.length > n ? `${str.slice(0, n - 1)}…` : str;
}

/**
 * Devuelve un mensaje corto y humano a partir del cuerpo de error del backend.
 * @param {any} body  Cuerpo JSON ya parseado, un Error, o un string.
 * @param {string} fallback  Mensaje a mostrar si el error es técnico/desconocido.
 */
export function formatApiError(
  body,
  fallback = 'No se pudo completar la operación. Revisa los datos e intenta de nuevo.'
) {
  try {
    if (body == null) return fallback;
    if (body instanceof Error) body = { detail: body.message };
    if (typeof body === 'string') body = { detail: body };

    const detail = body.detail !== undefined ? body.detail : body;

    // 422 de FastAPI/Pydantic: detail es un array de errores por campo.
    if (Array.isArray(detail)) {
      const faltan = [];
      const revisar = [];
      for (const e of detail) {
        const field = Array.isArray(e.loc) ? e.loc[e.loc.length - 1] : e.loc;
        const label = FIELD_LABELS[field] || field || 'un campo';
        if (e.type === 'missing' || /field required/i.test(e.msg || '')) {
          if (!faltan.includes(label)) faltan.push(label);
        } else if (!revisar.includes(label)) {
          revisar.push(label);
        }
      }
      const partes = [];
      if (faltan.length) partes.push(`Te faltó completar: ${faltan.join(', ')}`);
      if (revisar.length) partes.push(`Revisa: ${revisar.join(', ')}`);
      return truncate(partes.join('. ') || fallback);
    }

    // detail como texto: mensajes limpios del backend (ej. "Ya existe un cliente
    // con ese DNI") se muestran tal cual; los técnicos se reemplazan por fallback.
    if (typeof detail === 'string' && detail.trim()) {
      const msg = cleanMsg(detail);
      return looksTechnical(msg) ? fallback : truncate(msg);
    }

    return fallback;
  } catch {
    return fallback;
  }
}

export default formatApiError;
