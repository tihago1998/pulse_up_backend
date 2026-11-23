"""El módulo de hábitos se retiró: sus endpoints ya no existen, pero la tabla `habito` se conserva."""
import sqlite3

import pytest

from pulseup.core.roles import ID_SUPERADMINISTRADOR
from tests.helpers import cabeceras, usuario_con_rol, usuario_con_token


@pytest.mark.parametrize("url", ["/api/habitos/", "/api/habitos/resumen"])
def test_endpoints_de_habitos_responden_404(client, url):
    _, token = usuario_con_token(client)
    for headers in ({}, cabeceras(token)):
        r = client.get(url, headers=headers)
        assert r.status_code == 404
        assert r.get_json() == {"error": "Recurso no encontrado"}


def test_la_tabla_habito_se_conserva(app, db_path):
    conn = sqlite3.connect(db_path)
    columnas = [fila[1] for fila in conn.execute("PRAGMA table_info(habito)").fetchall()]
    conn.close()
    assert columnas == ["id", "id_usuario", "descripcion", "categoria", "fecha", "completado"]


def test_eliminar_usuario_borra_sus_habitos_antiguos(client, db_path):
    id_ana, _ = usuario_con_token(client)
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO habito (id_usuario, descripcion, categoria, fecha) VALUES (?, 'Tomar agua', 'General', '2026-11-01')",
        (id_ana,),
    )
    conn.commit()
    conn.close()

    _, token_super = usuario_con_rol(client, db_path, [ID_SUPERADMINISTRADOR], "Super", "super@test.com")
    assert client.delete(f"/api/users/{id_ana}", headers=cabeceras(token_super)).status_code == 200

    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM habito WHERE id_usuario = ?", (id_ana,)).fetchone()[0] == 0
    conn.close()
