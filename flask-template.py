import os

def is_valid_name(name, illegal_chars):
    for char in name:
        if char in illegal_chars:
            print(f"Illegal character '{char}' in name!")
            return False
    return True

illegal_chars = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|", "'", "\x00", ".", ",", " "]

def get_valid_name(prompt, illegal_chars):
    while True:
        name = input(prompt)
        if not name:
            print("Name cannot be empty.")
            continue
        if is_valid_name(name, illegal_chars):
            return name

project_name = get_valid_name("Enter your project name: ", illegal_chars)
app_name = get_valid_name("Enter the name of your Flask app: ", illegal_chars)
database_name = get_valid_name("Enter the name of your database: ", illegal_chars)

base_path = os.path.join(os.getcwd(), project_name)

def create_directory(path):
    try:
        os.makedirs(path)
        print(f"Created directory: {path}")
    except FileExistsError:
        print(f"Directory already exists: {path}")

def create_file(path, content=""):
    with open(path, 'w') as file:
        file.write(content)
        print(f"Created file: {path}")

# Create the project directory
create_directory(base_path)

# Directories to create
directories = [
    f"{app_name}/static/css",
    f"{app_name}/static/images",
    f"{app_name}/templates",
    f"{app_name}/models",
    f"{app_name}/views",
    f"{app_name}/forms",
    "migrations",
    "tests",
    "venv"
]

database_uri = f"postgresql://localhost/{database_name}"

app_init_content = '''from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .views.main import main as main_blueprint
# from .views.auth import auth as auth_blueprint
# from .views.api import api as api_blueprint
from .config import load_config
import os

app = Flask(__name__)

env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(load_config(env))

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.register_blueprint(main_blueprint)
# app.register_blueprint(auth_blueprint)
# app.register_blueprint(api_blueprint)
'''

config_content = f'''import os

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', '{database_uri}')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_TEST_DATABASE_URI', '{database_uri}_test')
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', '{database_uri}_prod')
''' + '''
def load_config(config_name):
    configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    return configs.get(config_name, DevelopmentConfig)
'''

env_content = f'''FLASK_APP=run.py
SECRET_KEY=your_secret_key

SQLALCHEMY_DATABASE_URI={database_uri}
SQLALCHEMY_TEST_DATABASE_URI={database_uri}_test
SQLALCHEMY_DATABASE_URI_PROD={database_uri}_prod
'''

conftest_content = f'''import pytest
from flask import Flask
from {app_name} import db
from {app_name}.config import TestingConfig
from {app_name}.models.test_table import RunTable

@pytest.fixture(scope='module')
def test_app():
    app = Flask(__name__)
    app.config.from_object(TestingConfig)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    with test_app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def seed_database(test_app):
    with test_app.app_context():
        db.session.add(RunTable(name='first_record'))
        db.session.commit()
'''

test_database_content = f'''from {app_name}.models.test_table import RunTable, db

def test_database_connection(test_app, test_client, seed_database):
    db.session.add(RunTable(name='second_record'))
    db.session.commit()

    result = RunTable.query.all()

    assert len(result) == 2
    assert result[0].name == 'first_record'
    assert result[1].name == 'second_record'
'''

test_table_content = f'''from {app_name} import db

class RunTable(db.Model):
    __tablename__ = 'test_table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
'''

# Files with their default contents
files = {
    # Basic app setup
    os.path.join(base_path, f"{app_name}", "__init__.py"): f"{app_init_content}",
    os.path.join(base_path, f"{app_name}", "config.py"): f"{config_content}",
    os.path.join(base_path, f"{app_name}", "utils.py"): "# Utility functions\n",
    os.path.join(base_path, f"{app_name}/static", "script.js"): "// JavaScript file",
    os.path.join(base_path, "run.py"): f"from dotenv import load_dotenv\nload_dotenv()\n\nfrom {app_name} import app\n\nif __name__ == '__main__':\n    app.run(debug=True)\n",
    os.path.join(base_path, "tests", "__init__.py"): "# Initialize tests module",
    os.path.join(base_path, "tests", "conftest.py"): f"{conftest_content}",
    os.path.join(base_path, "tests", "test_database.py"): f"{test_database_content}",
    os.path.join(base_path, "requirements.txt"): "python-dotenv\npsycopg2-binary\nsqlalchemy\nflask\nFlask-Migrate\nflask_sqlalchemy\nflask-wtf\nflask-login\nflask-migrate\nflask-bcrypt\nflask-cors\nflask-restful\nflask-jwt-extended\nflask-mail\npytest\n",
    os.path.join(base_path, ".env"): f"{env_content}",
    os.path.join(base_path, ".gitignore"): "venv/\n*.pyc\n.env\n",

    # Templates
    os.path.join(base_path, f"{app_name}/templates", "layout.html"): "<!DOCTYPE html>\n<html>\n<head>\n    <!-- Head contents -->\n</head>\n<body>\n    {% block content %}{% endblock %}\n</body>\n</html>",
    os.path.join(base_path, f"{app_name}/templates", "index.html"): "{% extends 'layout.html' %}\n{% block content %}\n<h1>Homepage</h1>\n{% endblock %}",
    os.path.join(base_path, f"{app_name}/templates", "login.html"): "<!-- Login page template -->",
    os.path.join(base_path, f"{app_name}/templates", "register.html"): "<!-- Registration page template -->",

    # Models
    os.path.join(base_path, f"{app_name}/models", "__init__.py"): "# Initialize models module",
    os.path.join(base_path, f"{app_name}/models", "test_table.py"): f"{test_table_content}",
    os.path.join(base_path, f"{app_name}/models", "user.py"): f"from {app_name} import db\n\nclass User(db.Model):\n    # User model",
    os.path.join(base_path, f"{app_name}/models", "post.py"): f"from {app_name} import db\n\nclass Post(db.Model):\n    # Post model",

    # Views
    os.path.join(base_path, f"{app_name}/views", "__init__.py"): "# Initialize views module",
    os.path.join(base_path, f"{app_name}/views", "main.py"): "from flask import Blueprint\n\nmain = Blueprint('main', __name__)\n\n@main.route('/')\ndef index():\n    return 'Hello, World!'\n",
    os.path.join(base_path, f"{app_name}/views", "auth.py"): "# Authentication views",
    os.path.join(base_path, f"{app_name}/views", "api.py"): "# API views",

    # Forms
    os.path.join(base_path, f"{app_name}/forms", "__init__.py"): "# Initialize forms module",
    os.path.join(base_path, f"{app_name}/forms", "login_form.py"): "from flask_wtf import FlaskForm\n\n# Login form",
    os.path.join(base_path, f"{app_name}/forms", "register_form.py"): "from flask_wtf import FlaskForm\n\n# Registration form",
    os.path.join(base_path, f"{app_name}/forms", "post_form.py"): "from flask_wtf import FlaskForm\n\n# Post form",
}

for directory in directories:
    create_directory(os.path.join(base_path, directory))

for file_path, content in files.items():
    create_file(file_path, content)

print("\nFlask project scaffolding with additional files created successfully!")
