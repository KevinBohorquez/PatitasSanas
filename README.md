# 🐾 Patitas Sanas

**Sistema de gestión para clínicas veterinarias.** Administra el ciclo completo de atención:
recepción de clientes y mascotas, triaje, consultas médicas, historial clínico, citas con
recordatorios automáticos por correo, flujo de caja y reportes — con paneles diferenciados por rol.

> Proyecto académico. Anteriormente llamado *Colitas Felices*.

---

## ✨ Características principales

### 👩‍⚕️ Por rol
- **Administrador** — CRUD de usuarios y roles (administradores, veterinarios, recepcionistas),
  gestión de servicios y catálogos, dashboard con insights y reportes de calidad.
- **Recepcionista** — gestión de clientes y mascotas, registro de solicitudes de atención,
  programación de citas y dashboard operativo.
- **Veterinario** — triaje, consultas médicas (diagnósticos y tratamientos), historial clínico,
  atención de citas y visualización de solicitudes asignadas.

### 🧩 Módulos transversales
- 🔐 **Autenticación** por rol (Administrador / Veterinario / Recepcionista).
- 📅 **Recordatorios de cita** automáticos por correo (24 h y 4 h antes) mediante un *scheduler* en segundo plano.
- 💰 **Flujo de caja** con registro automático de ingresos al atender una cita.
- 📄 **Reportes en PDF** (citas diarias, historial clínico) con la identidad visual de la clínica.
- 📊 **Dashboard** con métricas y gráficos.
- 🔔 **Sistema de notificaciones UX** — toasts, diálogos de confirmación, indicador de carga y
  estados vacíos, con la identidad de mascotas de Patitas Sanas (sin dependencias externas).
- ✅ **Calidad** integrada con SonarQube y pruebas unitarias (backend y frontend).

---

## 🛠️ Stack tecnológico

| Capa | Tecnologías |
|------|-------------|
| **Backend** | Python · FastAPI · SQLAlchemy 2 · Pydantic v2 · PyMySQL · APScheduler · ReportLab · Uvicorn/Gunicorn |
| **Frontend** | React 19 · Vite 6 · React Router 7 · Recharts |
| **Base de datos** | MySQL 8 |
| **Correo** | SMTP (configurable por variables de entorno) |
| **Calidad / Pruebas** | SonarQube · Pytest · Vitest |
| **Despliegue** | Railway (backend) · Vercel (frontend) |

---

## 📁 Estructura del repositorio

```
PatitasSanas/
├── Backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/v1/endpoints/ # Rutas (auth, consultas, triaje, citas, reportes, ...)
│   │   ├── crud/             # Operaciones de base de datos
│   │   ├── models/           # Modelos SQLAlchemy
│   │   ├── schemas/          # Esquemas Pydantic
│   │   ├── services/         # Recordatorios, correo, PDFs
│   │   └── config/           # Configuración y conexión a BD
│   ├── migrations/
│   ├── main.py
│   └── requirements.txt
├── Frontend/                # SPA React + Vite
│   └── src/
│       ├── components/       # Vistas por rol + comunes (Toast, Loader, ConfirmDialog, EmptyState)
│       ├── context/          # AuthProvider, ToastProvider, ConfirmProvider
│       ├── pages/
│       └── utils/
├── docs/                    # SRS, manuales, documentación de calidad
├── VeterinariaDump.sql      # Esquema + datos de ejemplo de la base de datos
└── CHANGELOG.md
```

---

## 🚀 Puesta en marcha (desarrollo local)

### Requisitos previos
- **Python 3.11+**
- **Node.js 18+**
- **MySQL 8**

### 1) Base de datos
```bash
# Crea la base y carga el esquema + datos de ejemplo
mysql -u root -p < VeterinariaDump.sql
```
Esto crea la base `veterinaria_db` con sus tablas, *triggers* y datos de prueba.

### 2) Backend
```bash
cd Backend
python -m venv .venv
# Windows:  .venv\Scripts\activate     |  Linux/Mac:  source .venv/bin/activate
pip install -r requirements.txt

# Copia el ejemplo de variables de entorno y ajústalo
cp .env.example .env

uvicorn main:app --reload --port 8000
```
API disponible en `http://localhost:8000` · documentación interactiva en `http://localhost:8000/docs`.

### 3) Frontend
```bash
cd Frontend
npm install
npm run dev
```
App disponible en `http://localhost:5173`.

> El proxy de desarrollo (`vite.config.js`) apunta al backend desplegado. Para usar tu backend
> local, cambia el `target` del proxy `/api` a `http://localhost:8000`.

---

## 🔑 Variables de entorno (Backend `.env`)

```env
DATABASE_URL=mysql+pymysql://usuario:password@host:3306/veterinaria_db

SECRET_KEY=una_clave_larga_y_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

ENVIRONMENT=development
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Recordatorios de cita por correo
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=tu_contraseña_de_aplicacion
SMTP_FROM=tu_correo@gmail.com
```

---

## 🧪 Pruebas y calidad

```bash
# Backend
cd Backend && pytest

# Frontend
cd Frontend && npm run test
npm run test:coverage   # cobertura para SonarQube
```

El análisis de calidad se ejecuta con SonarQube (ver `sonar-project.properties` y `docs/calidad/`).

---

## ☁️ Despliegue

- **Backend** → Railway (usa el `Procfile`: `gunicorn` con *workers* Uvicorn).
- **Frontend** → Vercel (`npm run build` genera `dist/`).
- **Base de datos** → MySQL gestionado (Railway).

Consulta **`docs/Manual de despliegue.docx.pdf`** para el detalle completo.

---

## 📚 Documentación

En la carpeta [`docs/`](docs/):
- 📄 **Documentación de Requerimientos del Software (SRS)**
- 🛠️ **Manual de Despliegue**
- 👤 **Manual de Usuario**
- 🗂️ **Plan de Gestión de Configuración**
- 📈 **Documentación de calidad (SonarQube)**

El historial de versiones está en [`CHANGELOG.md`](CHANGELOG.md).

---

## 🌿 Flujo de trabajo (Gitflow)

- `master` — rama estable de producción.
- `develop` — rama de integración.
- `feature/*`, `bugfix/*`, `fix/*` — ramas de trabajo que se integran a `develop` vía Pull Request.
