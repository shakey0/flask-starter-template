# Flask Project Template

This README provides instructions on how to use the `flask-template.py` script to create a new Flask project with a predefined directory structure and necessary files. This is a little project I undertook to save the hassle of having to individually create all the files, folders, testing config, etc. when starting a new project.
<br><br>NOTE: I am often updating this template, so please check for updates and download the latest version before using it.
<br><br>NOTE: It currently only runs smoothly on Mac OS. However, I am working on having an OS selection option and updating it to run on Windows and Ubuntu too.

## Quick Start

### Prerequisites

- Python 3.x installed on your system.
- Knowledge of command line operations.
- (If you select the PostgreSQL database option (currently only available on MacOS), you'll need PostgreSQL installed and running on your machine.)

### Using the Flask Template Script


1. **Download the Script**

    Download the `flask-template.py` script to your local machine.


2. **Run the Script**

    Open your command line tool and navigate to the directory where you want your new Flask project to be created.

    Run the script using Python:

    ```bash
    python path/to/flask-template.py
    ```
    (If for example you git cloned this repo into Documents, the path to run the file from any other directory would be: " python ~/Documents/FlaskProjectTemplate/flask-template.py ")
    <br><br>Upon running the file, enter the names of your project, app and database.
    <br><br>Once the tests have completed you'll see the message 'Your project is ready!'
    <br><br>If you've set up VS Code correctly, you'll be able to jump into your project by doing:

    ```bash
    cd YOUR_PROJECT_NAME/
    code .
    ```
    (You may need to open VS Code, close it, and open it again.)

    Once in your project in VS Code, open a terminal, and if the pipenv shell isn't already activated, do:
    ```bash
    pipenv shell
    ```

    Now you can run the tests by doing:
    ```bash
    pytest
    ```

    You can start the server by doing:
    ```bash
    python run.py
    ```

### Project Structure

The script will create a new directory with your project name and set up a basic Flask project structure inside it, including:

- Application directories (models, views, forms, tests, etc.)
- Configuration files
- A basic Flask application setup
- Initial pytests and playwright tests
