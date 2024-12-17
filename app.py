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

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Asegurar que la carpeta instance existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(repairs_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(parts_bp)

    # Configurar manejadores de error
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(401)
    def unauthorized_error(error):
        return redirect(url_for('auth.login'))

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
