from flask import Blueprint

# Importar los blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.repairs import repairs_bp

# Exportar los blueprints
__all__ = ['auth_bp', 'main_bp', 'repairs_bp']
