# Flask Project Template

This README provides instructions on how to use the `flask-template.py` script to create a new Flask project with a predefined directory structure and necessary files.

## Quick Start

### Prerequisites

- Python 3.x installed on your system.
- Knowledge of command line operations.
- PostgreSQL database server (or modify the script for your database system).

### Using the Flask Template Script

1. **Download the Script**

Download the `flask-template.py` script to your local machine.

2. **Run the Script**

Open your command line tool and navigate to the directory where you want your new Flask project to be created.

Run the script using Python:

```bash
python path/to/flask-template.py
```

#### Project Structure

The script will create a new directory with your project name and set up a basic Flask project structure inside it, including:

- Application directories (models, views, forms, tests, etc.)
- Configuration files
- A basic Flask application setup

### Setting Up Your Environment

1. **Create a Virtual Environment (Recommended)**

Navigate to your project directory and create a virtual environment:

```bash
pipenv install
pipenv shell
```

Do Cmd+Shift+P and click 'Python: Select Interpreter'. Select the interpreter for your project.

### Database Setup

1. **Configure Database URIs**

Update the .env file in your project root with the correct URIs for your development and test databases if necessary. (You shouldn't need to do this.)

2. **Initialize and Migrate Database**

Run the following commands to set up your database:

```bash
flask db init
createdb THE_EXACT_DATABASE_NAME_YOU_CHOSE_EARLIER
createdb THE_EXACT_DATABASE_NAME_YOU_CHOSE_EARLIER_test
createdb THE_EXACT_DATABASE_NAME_YOU_CHOSE_EARLIER_prod
flask db migrate -m "Initial migration"
flask db upgrade
```

### Running the Application

1. **Start the Flask Server**

To run the Flask application:

```bash
flask run
```

### Running Tests

1. **Running Pytest**

To run the tests, simply use the pytest command in the project root:

```bash
pipenv run pytest
```
