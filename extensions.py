from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

# Configuración de Flask-Login
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'
login_manager.session_protection = 'strong'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
