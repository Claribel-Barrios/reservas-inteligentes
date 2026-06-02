# 📅 Sistema de Reservas Inteligente

**Proyecto académico** | Python + Flask  
**Integrantes:** Danna Sánchez, Claribel Barrios

---

## 🚀 Instalación y ejecución

### 1. Requisitos previos
- Python 3.10+
- pip

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación
```bash
python run.py
```

Abre tu navegador en: **http://localhost:5000**

---

## 🔑 Cuentas de acceso (demo)

| Rol | Correo | Contraseña |
|-----|--------|------------|
| Administrador | admin@reservas.com | admin1234 |
| Usuario | usuario@demo.com | usuario123 |

---

## 🧩 Funcionalidades implementadas

### RF1 — Gestión de Usuarios
- ✅ RF1.1 Registro de nuevos usuarios (nombre, correo, teléfono, contraseña)
- ✅ RF1.2 Inicio de sesión con correo y contraseña
- ✅ RF1.3 Recuperación de contraseña por correo
- ✅ RF1.4 El administrador puede activar/desactivar y cambiar roles

### RF2 — Gestión de Reservas
- ✅ RF2.1 Listado de servicios y horarios disponibles
- ✅ RF2.2 Reservar y cancelar turnos
- ✅ RF2.3 Actualización automática de cupos disponibles
- ✅ RF2.4 Notificaciones automáticas (correo + sistema interno)

### RF3 — Pagos en Línea (arquitectura lista)
- ✅ RF3.1 Modelo Pago listo para integrar Stripe/PayU/PayPal
- ✅ RF3.2 Registro de transacciones en base de datos
- ✅ RF3.3 Estructura para comprobantes PDF
- ✅ RF3.4 Control de duplicados de transacciones

### RF4 — Gestión Administrativa
- ✅ RF4.1 Panel para crear/editar/eliminar servicios, horarios y usuarios
- ✅ RF4.2 Estadísticas: reservas, usuarios activos, cancelaciones
- ✅ RF4.3 Notificaciones internas configurables

### RF5 — Notificaciones Inteligentes
- ✅ RF5.1 Notificaciones automáticas por correo al reservar/cancelar
- ✅ RF5.2 Sistema de recordatorios
- ✅ RF5.3 Notificaciones al administrador sobre actividad

---

## 🏗 Estructura del proyecto

```
reservas/
├── run.py                  # Punto de entrada
├── config.py               # Configuración (BD, correo, sesión)
├── requirements.txt
└── app/
    ├── __init__.py         # App factory (Flask)
    ├── models.py           # Modelos: Usuario, Servicio, Horario, Reserva, Pago, Notificacion
    ├── routes/
    │   ├── auth.py         # Registro, login, logout, recuperación, perfil
    │   ├── main.py         # Inicio, catálogo de servicios
    │   ├── reservas.py     # Crear, cancelar, ver reservas
    │   └── admin.py        # Panel admin completo
    ├── utils/
    │   ├── email.py        # Envío de correos (confirmación, cancelación, recuperación)
    │   └── seed.py         # Datos iniciales de demostración
    └── templates/
        ├── base.html       # Layout base con nav y flash messages
        ├── main/           # index.html, servicios.html
        ├── auth/           # login, registro, perfil, recuperar, reset
        ├── reservas/       # mis_reservas, nueva, confirmar, detalle
        └── admin/          # dashboard, servicios, horarios, usuarios, reservas, reportes
```

---

## 🔒 Requerimientos No Funcionales aplicados

| RNF | Implementación |
|-----|----------------|
| RNF3.1 Contraseñas cifradas | Flask-Bcrypt (bcrypt) |
| RNF3.2 Conexiones seguras | Configurable con SSL/HTTPS en producción |
| RNF4.1 Interfaz responsiva | CSS Grid/Flexbox adaptable |
| RNF6.1 Código modular | Blueprints, principios SOLID |
| RNF6.3 Control de versiones | Estructura lista para Git |

---

## 🗄 Base de datos

SQLite en desarrollo. Para producción cambiar en `config.py`:
```python
SQLALCHEMY_DATABASE_URI = "postgresql://user:password@host/dbname"
```

---

## 📦 Tecnologías

- **Backend:** Python 3 + Flask 3
- **ORM:** SQLAlchemy + Flask-SQLAlchemy
- **Auth:** Flask-Login + Flask-Bcrypt
- **Email:** Flask-Mail
- **BD:** SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend:** HTML5 + CSS3 puro (sin dependencias externas)
