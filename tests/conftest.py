import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("PULSEUP_SECRET_KEY", "clave-de-pruebas-de-al-menos-32-bytes!!")

from pulseup import create_app  # noqa: E402


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "pulseup.db")


@pytest.fixture
def app(db_path):
    return create_app(
        {
            "SECRET_KEY": "clave-de-pruebas-de-al-menos-32-bytes!!",
            "DB_NAME": db_path,
            "TESTING": True,
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()
