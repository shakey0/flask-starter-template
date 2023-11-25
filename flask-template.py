import os
import subprocess
import platform

def is_valid_name(name, illegal_chars, uppercase=True):
    for char in name:
        if char in illegal_chars or (not uppercase and char.isupper()):
            print(f"Illegal character '{char}' in name!")
            return False
    return True

illegal_chars = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|", "'", "\x00", ".", ",", " "]

def get_valid_name(prompt, illegal_chars, uppercase=True):
    while True:
        name = input(prompt)
        if not name:
            print("Name cannot be empty.")
            continue
        if is_valid_name(name, illegal_chars, uppercase):
            return name

project_name = get_valid_name("\nEnter your project name: ", illegal_chars)
app_name = get_valid_name("\nEnter the name of your Flask app: ", illegal_chars)
database_name = get_valid_name("\nEnter the name of your database: ", illegal_chars, uppercase=False)

os_names = ["Windows", "Linux", "Darwin"]
os_name = platform.system()

if os_name not in os_names:
    print("\nUnable to detect OS.")
    while True:
        os_option = input("\nChoose your OS:\n1. Windows\n2. Linux\n3. MacOS\n\nEnter your choice: ")
        if os_option == "1":
            os_name = "Windows"
            break
        elif os_option == "2":
            os_name = "Linux"
            break
        elif os_option == "3":
            os_name = "Darwin"
            break
        else:
            print("\nInvalid choice.")

if os_name == "Windows":
    print("\nWindows OS detected.")
    input('\nSQLite will be used for the database. Press Enter to continue... ')
    database_uri = f"sqlite:///{database_name}.db"

elif os_name == "Linux":
    print("\nLinux OS detected.")
    input('\nSQLite will be used for the database. Press Enter to continue... ')
    database_uri = f"sqlite:///{database_name}.db"

elif os_name == "Darwin":
    print("\nMacOS detected.")
    print('\nYou can choose between SQLite and PostgreSQL for the database.')
    while True:
        choice = input('\nPress P + Enter to use PostgreSQL or simply press Enter to use SQLite... ')
        if choice == "":
            f_choice = input('\nYou have chosen SQLite. Press Enter to confirm or B + Enter to go back... ')
            if f_choice.lower() != "b":
                database_uri = f"sqlite:///{database_name}.db"
                break
        elif choice.lower() == "p":
            print('\nYou have chosen PostgreSQL. Make sure you have it installed and running on your system.')
            f_choice = input('\nPress Enter to confirm or B + Enter to go back... ')
            if f_choice.lower() != "b":
                database_uri = f"postgresql://localhost/{database_name}"
                break

else:
    database_uri = f"sqlite:///{database_name}.db"

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
    os.path.join(app_name, "static", "css"),
    os.path.join(app_name, "static", "images"),
    os.path.join(app_name, "templates"),
    os.path.join(app_name, "models"),
    os.path.join(app_name, "views"),
    os.path.join(app_name, "forms"),
    "migrations",
    "tests",
    "venv"
]

app_init_content = f'''from flask import Flask
from {app_name}.extensions import db, migrate
from .config import load_config
import os

def create_app():
    app = Flask(__name__)

    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(load_config(env))

    db.init_app(app)
    migrate.init_app(app, db)

    from .views.main import main as main_blueprint
    # from .views.auth import auth as auth_blueprint
    # from .views.api import api as api_blueprint

    app.register_blueprint(main_blueprint)
    # app.register_blueprint(auth_blueprint)
    # app.register_blueprint(api_blueprint)

    return app
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
    WTF_CSRF_ENABLED = True

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

conftest_content = f'''import pytest, sys, py, os
from flask import Flask
from {app_name} import db
from {app_name}.config import TestingConfig
from {app_name}.models.test_table import RunTable
from tests.seed_data import init_user
from playwright.sync_api import sync_playwright
from xprocess import ProcessStarter

@pytest.fixture(scope='function')
def test_app():
    app = Flask(__name__)
    app.config.from_object(TestingConfig)
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def test_client(test_app):
    with test_app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def seed_test_database_for_test(test_app):
    with test_app.app_context():
        db.session.add(RunTable(name='first_record'))
        db.session.commit()

@pytest.fixture(scope='function')
def seed_test_database(test_app):
    with test_app.app_context():
        init_user(db)

@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()
''' + '''
@pytest.fixture(scope='session')
def flask_server(xprocess):
    python_executable = sys.executable
    app_file = py.path.local(__file__).dirpath("../run.py").realpath()
    class Starter(ProcessStarter):
        pattern = "Running on http://127.0.0.1:5000"
        env = {"PORT": str(5000), "FLASK_ENV": "testing", **os.environ}
        args = [python_executable, app_file]

    xprocess.ensure('flask_app', Starter)

    yield f"http://localhost:5000/"

    xprocess.getinfo('flask_app').terminate()
'''

test_database_content = f'''from {app_name}.models.test_table import RunTable, db

def test_database_connection(test_app, test_client, seed_test_database_for_test):
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

seed_data_content = f'''from {app_name}.models.user import User

def init_user(db):

    test_user = User(
        username='john_doe',
        email='john@example.com'
    )
    db.session.add(test_user)
    db.session.commit()
'''

test_user_content = f'''from {app_name}.models.user import User

def test_user_creation(test_app, test_client, seed_test_database):
    user = User.query.filter_by(username='john_doe').first()
    assert user is not None
    assert user.username == 'john_doe'
    assert user.email == 'john@example.com'
'''

test_homepage_content = f'''from playwright.sync_api import expect

def test_homepage_navbar(page, test_app, test_client, seed_test_database, flask_server):
    test_url = "http://localhost:5000/"
    page.goto(test_url)
    logo = page.locator('h1')
    expect(logo).to_have_text('Hello world!')
'''

main_content = f'''from flask import Blueprint
from {app_name}.extensions import db
from {app_name}.models.user import User
from flask import render_template
import random
import string

main = Blueprint('main', __name__)
''' + '''
@main.route('/')
def index():
    # { }
    random_username = ''.join(random.choices(string.ascii_lowercase, k=10))
    random_email = '{}@example.com'.format(random_username)

    new_user = User(username=random_username, email=random_email)

    db.session.add(new_user)
    db.session.commit()

    users = User.query.order_by(User.id.desc()).all()

    hello_message = '<h1>Hello world!</h1>'

    for user in users:
        hello_message += '<p>User {}: {}<br>Email: {}</p>'.format(user.id, user.username, user.email)

    return hello_message
'''

user_model_content = f'''from {app_name} import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
''' + '''
    # { }
    def __repr__(self):
        return '<User {}>'.format(self.username)
'''

# Files with their default contents
files = {
    # Basic app setup
    os.path.join(base_path, f"{app_name}", "__init__.py"): f"{app_init_content}",
    os.path.join(base_path, f"{app_name}", "config.py"): f"{config_content}",
    os.path.join(base_path, f"{app_name}", "utils.py"): "# Utility functions\n",
    os.path.join(base_path, f"{app_name}", "static", "script.js"): "// JavaScript file",
    os.path.join(base_path, f"{app_name}", "extensions.py"): "from flask_sqlalchemy import SQLAlchemy\nfrom flask_migrate import Migrate\n\n# Initialize extensions\n\ndb = SQLAlchemy()\nmigrate = Migrate()\n",
    os.path.join(base_path, "run.py"): f"from dotenv import load_dotenv\nload_dotenv()\n\nfrom {app_name} import create_app\n\napp = create_app()\n\nif __name__ == '__main__':\n    app.run(debug=True)\n",
    os.path.join(base_path, "tests", "__init__.py"): "# Initialize tests module",
    os.path.join(base_path, "tests", "conftest.py"): f"{conftest_content}",
    os.path.join(base_path, "tests", "test_database.py"): f"{test_database_content}",
    os.path.join(base_path, "tests", "seed_data.py"): f"{seed_data_content}",
    os.path.join(base_path, "tests", "test_user.py"): f"{test_user_content}",
    os.path.join(base_path, "tests", "test_homepage.py"): f"{test_homepage_content}",
    os.path.join(base_path, "requirements.txt"): "python-dotenv\npsycopg2-binary\nsqlalchemy\nflask\nFlask-Migrate\nflask_sqlalchemy\nflask-wtf\nflask-login\nflask-migrate\nflask-bcrypt\nflask-cors\nflask-restful\nflask-jwt-extended\nflask-mail\npytest\npytest-xprocess\nplaywright\n",
    os.path.join(base_path, ".env"): f"{env_content}",
    os.path.join(base_path, ".gitignore"): "venv/\n*.pyc\n.env\n",

    # Templates
    os.path.join(base_path, f"{app_name}", "templates", "layout.html"): "<!DOCTYPE html>\n<html>\n<head>\n    <!-- Head contents -->\n</head>\n<body>\n    {% block content %}{% endblock %}\n</body>\n</html>",
    os.path.join(base_path, f"{app_name}", "templates", "index.html"): "{% extends 'layout.html' %}\n{% block content %}\n<h1>Homepage</h1>\n{% endblock %}",
    os.path.join(base_path, f"{app_name}", "templates", "login.html"): "<!-- Login page template -->",
    os.path.join(base_path, f"{app_name}", "templates", "register.html"): "<!-- Registration page template -->",

    # Models
    os.path.join(base_path, f"{app_name}", "models", "__init__.py"): "# Initialize models module",
    os.path.join(base_path, f"{app_name}", "models", "test_table.py"): f"{test_table_content}",
    os.path.join(base_path, f"{app_name}", "models", "user.py"): f"{user_model_content}",
    os.path.join(base_path, f"{app_name}", "models", "post.py"): f"from {app_name} import db\n\nclass Post(db.Model):\n    pass",

    # Views
    os.path.join(base_path, f"{app_name}", "views", "__init__.py"): "# Initialize views module",
    os.path.join(base_path, f"{app_name}", "views", "main.py"): f"{main_content}",
    os.path.join(base_path, f"{app_name}", "views", "auth.py"): "# Authentication views",
    os.path.join(base_path, f"{app_name}", "views", "api.py"): "# API views",

    # Forms
    os.path.join(base_path, f"{app_name}", "forms", "__init__.py"): "# Initialize forms module",
    os.path.join(base_path, f"{app_name}", "forms", "login_form.py"): "from flask_wtf import FlaskForm\n\n# Login form",
    os.path.join(base_path, f"{app_name}", "forms", "register_form.py"): "from flask_wtf import FlaskForm\n\n# Registration form",
    os.path.join(base_path, f"{app_name}", "forms", "post_form.py"): "from flask_wtf import FlaskForm\n\n# Post form",
}

for directory in directories:
    create_directory(os.path.join(base_path, directory))

for file_path, content in files.items():
    create_file(file_path, content)

print("\nFlask project scaffolding with additional files created successfully.")

def change_directory(path):
    os.chdir(path)
    print(f"Changed working directory to {path}")

def run_shell_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Successfully executed: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Error in executing command: {command}\n{e}")
        exit()
    
change_directory(base_path)

try:
    run_shell_command("pipenv install")
except:
    print("\nUnable to install pipenv for the project. Would you like to install it globally?")
    choice = input("Press Y + Enter to install globally or simply press Enter to exit... ")
    if choice.lower() == "y":
        if os_name == "Windows":
            try:
                run_shell_command("pip install pipenv")
                run_shell_command("pipenv install")
            except:
                print("\nUnable to install pipenv. Exiting...")
                print("\nYou can also try installing pipenv manually using the following commands and then run this file again: ")
                print("pip install pipenv")
                print("\nIf you will run this file again, to create the same project, you will need to delete the files and directories created by this script.")
                exit()
        elif os_name == "Linux":
            try:
                run_shell_command("sudo apt install pipenv")
                run_shell_command("pip install --user --upgrade pip")
                run_shell_command("pipenv install")
            except:
                print("\nUnable to install pipenv. Exiting...")
                print("\nYou can also try installing pipenv manually using the following commands and then run this file again: ")
                print("sudo apt install pipenv")
                print("pip install --user --upgrade pip")
                print("\nIf you will run this file again, to create the same project, you will need to delete the files and directories created by this script.")
                exit()
        elif os_name == "Darwin":
            try:
                run_shell_command("brew install pipenv")
                run_shell_command("pipenv install")
            except:
                print("\nUnable to install pipenv. Exiting...")
                print("\nYou can also try installing pipenv manually using the following commands and then run this file again: ")
                print("brew install pipenv")
                print("\nIf you will run this file again, to create the same project, you will need to delete the files and directories created by this script.")
                exit()
    else:
        print("\nUnable to install pipenv. Exiting...")
        print("\nThe files and directories created can be used with any other virtual environment manager.")
        print("You can also use the requirements.txt file to install the dependencies manually.")
        print("You will also need to create your databases manually.")
        exit()
run_shell_command("pipenv run flask db init")
if "sqlite" in database_uri:
    for db_name in [f"{database_name}.db", f"{database_name}_test.db", f"{database_name}_prod.db"]:
        open(db_name, 'a').close()
else:
    run_shell_command(f"createdb {database_name}")
    run_shell_command(f"createdb {database_name}_test")
    run_shell_command(f"createdb {database_name}_prod")
run_shell_command("pipenv run flask db migrate")
run_shell_command("pipenv run flask db upgrade")
run_shell_command("pipenv run playwright install")
run_shell_command("pipenv run pytest")

print("\n\nYour project is ready!")
print("\nRun the following commands to start the server:\n")
print(f"~ cd {project_name}/")
print("~ pipenv shell")
print("~ python run.py\n")
