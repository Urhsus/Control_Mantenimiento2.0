# Sistema de Registro de Mantenimiento ROV

Sistema web para gestionar y registrar reparaciones de equipos ROV.

## Características

- Registro de usuarios (técnicos y supervisores)
- Gestión de reparaciones
- Registro de partes y repuestos
- Exportación de datos a Excel
- Informes y estadísticas

## Tecnologías

- Python 3.12
- Flask
- SQLAlchemy
- Bootstrap 5

## Instalación Local

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd control-mantenimiento-rov
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
Crear archivo `.env` con:
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/mantenimiento.db
FLASK_ENV=development
```

5. Inicializar la base de datos:
```bash
python init_db.py
```

6. Ejecutar la aplicación:
```bash
python app.py
```

## Despliegue

La aplicación está configurada para ser desplegada en Render.com.

## Licencia

Este proyecto está bajo la Licencia MIT.
