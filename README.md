# Sistema de Control de Mantenimiento ROV

Sistema web para la gestión y seguimiento de mantenimientos de equipos ROV.

## Características

- Gestión de reparaciones y mantenimientos
- Control de repuestos
- Informes y estadísticas
- Sistema de roles (Admin, Supervisor, Técnico)
- Exportación de datos a Excel

## Tecnologías

- Python 3.9+
- Flask
- SQLAlchemy
- PostgreSQL
- Bootstrap 5

## Instalación Local

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd control-mantenimiento
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Inicializar la base de datos:
```bash
python init_db.py
```

6. Ejecutar la aplicación:
```bash
flask run
```

## Despliegue

La aplicación está configurada para ser desplegada en Render.com.

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
