from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv   
import os                       

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Войдите в систему'
login_manager.login_message_category = 'warning'

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    load_dotenv()

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-2025')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # URL to Metabase (optional). If set, templates can show a link to Metabase UI.
    # Default opens the databases view for the local Postgres datasource.
    app.config['METABASE_URL'] = os.getenv('METABASE_URL', 'http://localhost:3000/browse/databases/2-postgres')

    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)

    # ← ВОТ СЮДА ПЕРЕНОСИМ ВСЕ ИМПОРТЫ:
    from .routes.auth import auth_bp
    from .routes.documents import docs_bp
    from .routes.people import people_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(people_bp)

    from .models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # expose some config to templates (e.g. METABASE_URL)
    @app.context_processor
    def inject_config():
        return {
            'metabase_url': app.config.get('METABASE_URL')
        }

    return app