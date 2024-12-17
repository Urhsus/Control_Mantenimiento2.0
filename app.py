from flask import Flask, render_template, redirect, url_for
from extensions import db, login_manager
from routes.auth import auth_bp
from routes.main import main_bp
from routes.repairs import repairs_bp
from routes.admin import admin_bp
from routes.parts import parts_bp
from models import User
from config import Config
import os
import logging
from datetime import datetime

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configurar logging más detallado
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Asegurar que el directorio de la base de datos existe
    db_dir = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        app.logger.info(f'Directorio de base de datos creado: {db_dir}')
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(repairs_bp, url_prefix='/repairs')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(parts_bp, url_prefix='/parts')

    # Agregar la variable 'now' a todas las plantillas
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Manejadores de error
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Inicializar la base de datos
    with app.app_context():
        try:
            app.logger.info('Intentando crear las tablas de la base de datos...')
            db.create_all()
            app.logger.info('Base de datos inicializada correctamente')
            
            # Verificar si hay un usuario admin
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                app.logger.info('Creando usuario admin por defecto...')
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                app.logger.info('Usuario admin creado exitosamente')
        except Exception as e:
            app.logger.error(f'Error al inicializar la base de datos: {str(e)}')
            app.logger.error('Detalles del error:', exc_info=True)
            raise

    return app

# Crear la instancia de la aplicación para Gunicorn
app = create_app()

# Crear directorios necesarios
for directory in [app.config['UPLOAD_FOLDER']]:
    if not os.path.exists(directory):
        os.makedirs(directory)
        app.logger.info(f'Directorio creado: {directory}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
