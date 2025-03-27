import sys
import pytest
import django
import os
from django.core.management import call_command
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megastation.settings')

# Database configuration from environment variables
TEST_DB_NAME = os.getenv('TEST_DB_NAME', 'megastation_test')
DB_USER = os.getenv('DB_USER', 'megastation_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'megapass')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
POSTGRES_USER = 'postgres'  # Superuser for PostgreSQL
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')  # Postgres password from .env


# Function to set up test database
def setup_test_database():
    try:
        # Debug output for connection parameters
        print(f"Connecting as {POSTGRES_USER} with password '{POSTGRES_PASSWORD}' to {DB_HOST}:{DB_PORT}")

        # Connect as postgres user
        conn = psycopg2.connect(
            dbname='postgres',
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD if POSTGRES_PASSWORD else None,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Drop test database if it exists
        cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")

        # Create test database
        cursor.execute(f"CREATE DATABASE {TEST_DB_NAME} OWNER {DB_USER}")

        # Grant privileges to the test user
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {TEST_DB_NAME} TO {DB_USER}")

        # Connect to test database and grant schema privileges
        conn.close()
        conn = psycopg2.connect(
            dbname=TEST_DB_NAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD if POSTGRES_PASSWORD else None,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(f"GRANT ALL ON SCHEMA public TO {DB_USER}")

        cursor.close()
        conn.close()
        print(f"Test database {TEST_DB_NAME} created and privileges granted to {DB_USER}")
    except OperationalError as e:
        print(f"OperationalError setting up test database: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


# Set up test database
setup_test_database()

# Configure Django to use test database
django.setup()
from django.conf import settings

settings.DATABASES['default']['NAME'] = TEST_DB_NAME
print("Database in use:", settings.DATABASES['default']['NAME'])

# Apply migrations to test database
call_command('migrate', '--database=default', '--noinput')

if __name__ == "__main__":
    # Run pytest with verbose output
    sys.exit(pytest.main(["-s", "-v"]))