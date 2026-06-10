# Documentación: Configuración del Servicio de Email y Variables de Entorno

**Proyecto:** Patitas Sanas — Sistema Veterinario  
**Módulo:** Notificaciones por correo electrónico  
**Archivo relevante:** `Backend/app/services/notifications/email_service.py`  
**Ubicación de este documento:** `docs/email-service-config.md`

---

## 1. Qué servicio de email se usa

El sistema utiliza **Gmail SMTP** (Simple Mail Transfer Protocol) como proveedor de correo saliente. Se eligió Gmail por las siguientes razones:

- Capa gratuita generosa: hasta 500 correos diarios desde una cuenta personal.
- Compatible con cualquier librería SMTP estándar de Python (se usa `smtplib` de la biblioteca estándar, sin dependencias externas adicionales).
- Ampliamente documentado y sin necesidad de registrar un dominio propio.

El envío se realiza con cifrado **TLS** en el puerto **587**, que es el estándar para envío autenticado seguro.

---

## 2. Variables de entorno requeridas

Todas las credenciales y parámetros de conexión se leen desde variables de entorno, nunca están escritas directamente en el código. El archivo `.env.example` en la raíz de `Backend/` contiene la plantilla con los nombres exactos.

### Tabla de variables

| Variable | Descripción | Ejemplo |
|---|---|---|
| `SMTP_HOST` | Servidor de correo saliente | `smtp.gmail.com` |
| `SMTP_PORT` | Puerto del servidor | `587` |
| `SMTP_USER` | Correo remitente (cuenta Gmail que envía) | `patitassanas@gmail.com` |
| `SMTP_PASSWORD` | Contraseña de aplicación de Gmail (ver sección 3) | `xxxx xxxx xxxx xxxx` |
| `SMTP_FROM` | Nombre o dirección visible del remitente | `patitassanas@gmail.com` |

> Si `SMTP_FROM` no está definida, el sistema usa automáticamente el valor de `SMTP_USER`.

### Fragmento del `.env.example`

```
# Configuración SMTP para recordatorios de citas
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=tu_contraseña_de_aplicacion
SMTP_FROM=tu_correo@gmail.com
```

---

## 3. Cómo configurarlo localmente (paso a paso)

### Paso 1 - Copiar el archivo de ejemplo

Desde la carpeta `Backend/`, ejecutar:

```bash
cp .env.example .env
```

Abrir el `.env` recién creado con cualquier editor de texto.

### Paso 2 - Crear una contraseña de aplicación en Gmail

Gmail **no permite** usar la contraseña normal de tu cuenta para enviar correos desde código. Es obligatorio generar una **contraseña de aplicación** específica. Estos son los pasos:

1. Ingresar a [myaccount.google.com](https://myaccount.google.com).
2. Ir a **Seguridad** → **Verificación en dos pasos** y activarla si no está activa (requisito previo obligatorio).
3. Volver a **Seguridad** → buscar **"Contraseñas de aplicaciones"** (puede aparecer como "App passwords").
4. En el selector, elegir "Correo" y "Otro (nombre personalizado)" → escribir `Patitas Sanas`.
5. Hacer clic en **Generar**. Gmail mostrará una clave de 16 caracteres con espacios, por ejemplo: `abcd efgh ijkl mnop`.
6. Copiar esa clave completa (con o sin espacios, ambas formas funcionan).

### Paso 3 - Completar las variables en el `.env`

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=mi_cuenta@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_FROM=mi_cuenta@gmail.com
```

Reemplazar `mi_cuenta@gmail.com` con la cuenta Gmail que generó la contraseña de aplicación.

### Paso 4 - Verificar que el sistema lee las variables

El archivo `Backend/app/config/database.py` ya carga el `.env` automáticamente con `python-dotenv`. El servicio de email también lo hace:

```python
# Backend/app/services/notifications/email_service.py
smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
smtp_port = int(os.getenv("SMTP_PORT", 587))
smtp_user = os.getenv("SMTP_USER")
smtp_password = os.getenv("SMTP_PASSWORD")
smtp_from = os.getenv("SMTP_FROM", smtp_user)
```

Si `SMTP_USER` o `SMTP_PASSWORD` están vacíos, el sistema registra un error en los logs y no intenta enviar el correo (retorna `False`), sin que la aplicación se caiga.

### Paso 5 - Probar el envío (opcional pero recomendado)

Levantar el backend normalmente y verificar en los logs de la consola que el scheduler inicia correctamente:

```
INFO  Scheduler de recordatorios iniciado (cada 30 min)
```

Para forzar un envío de prueba inmediato, se puede llamar directamente desde una sesión de Python:

```python
from app.services.notifications.email_service import send_reminder_email
from datetime import datetime

resultado = send_reminder_email(
    to_email="destinatario@gmail.com",
    cliente_nombre="Juan Pérez",
    mascota_nombre="Toby",
    fecha_hora=datetime(2026, 6, 15, 10, 0),
    horas_antes=24,
)
print("Enviado:", resultado)  # True si fue exitoso
```

---

## 4. Cómo funciona el sistema de recordatorios

El módulo de notificaciones tiene tres componentes principales:

**`email_service.py`** - Construye y envía el correo usando `smtplib`. Lee las variables de entorno en cada llamada.

**`email_template.py`** - Genera el HTML del correo con el diseño visual de Patitas Sanas (logotipo, tabla de datos de la cita, pie de página).

**`reminder_scheduler.py`** - Tarea programada (APScheduler) que se ejecuta cada 30 minutos. En cada ejecución:
1. Busca citas con `estado_cita = 'Programada'` cuya fecha esté dentro de 24 h ± 1 h (o 4 h ± 1 h).
2. Verifica que el recordatorio correspondiente no haya sido enviado ya (flags `recordatorio_24h_enviado` y `recordatorio_4h_enviado` en la tabla `Cita`).
3. Obtiene el email del cliente mediante JOIN: `Cita → Mascota → Cliente_Mascota → Cliente`.
4. Llama a `send_reminder_email()` y, si el envío es exitoso, marca el flag en base de datos para no reenviar.

El scheduler se inicia automáticamente al levantar el servidor (`startup_event` en `main.py`) y se detiene limpiamente al apagarlo (`shutdown_event`).

---

## 5. Consideraciones de seguridad

- El archivo `.env` está incluido en `.gitignore` y **nunca debe subirse al repositorio**.
- La contraseña de aplicación de Gmail es diferente a la contraseña real de la cuenta y puede revocarse desde Google sin afectar el acceso normal.
- En producción (Railway), las variables de entorno se configuran desde el panel de la plataforma, no desde un archivo `.env`.
- El sistema no almacena ni registra las contraseñas en ningún log.

---

## 6. Errores comunes y soluciones

| Error en logs | Causa probable | Solución |
|---|---|---|
| `Credenciales SMTP no configuradas` | `SMTP_USER` o `SMTP_PASSWORD` vacíos en `.env` | Completar las variables y reiniciar el servidor |
| `SMTPAuthenticationError` | Contraseña incorrecta o verificación en dos pasos no activada | Regenerar la contraseña de aplicación (sección 3, Paso 2) |
| `SMTPConnectError` | Sin acceso a internet o puerto 587 bloqueado | Verificar conexión; en algunas redes universitarias el puerto 587 está bloqueado |
| El correo llega a Spam | Gmail marca correos enviados desde cuentas personales | Pedir al destinatario que marque el remitente como confiable; en producción usar dominio propio |
| `recordatorio_24h_enviado` ya es `True` | El recordatorio ya fue enviado en una ejecución anterior | Comportamiento esperado: el sistema no reenvía duplicados |

---

*Este documento corresponde a la versión v1.2.0 del proyecto (integración de notificaciones por email, junio 2026).*
