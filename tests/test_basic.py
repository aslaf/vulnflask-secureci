from unittest.mock import MagicMock, patch

import pytest

from app.app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_index_route(client):
    with patch("sqlite3.connect", autospec=True) as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value.fetchall.return_value = []

        response = client.get("/")
        assert response.status_code == 200
