from fabric.api import local, task

from seed_data import create_csv_data, generate_table_data

@task
def compile_scss():
    # Currently just a single file - no need to walk directories.
    local("pyscss --output=app/static/css/main.css --no-compress "
          "app/static/css/scss/main.scss")

@task
def create_sqlite_test_database():
    # Generate the yaml and csv files.
    generate_table_data()
    create_csv_data()

    # Create the database by running alembic migrations.
    local("alembic upgrade head")

    # Load the csv data into the database file.
    local("sqlite3 -separator ',' app.db '.import stops.csv stops'")
