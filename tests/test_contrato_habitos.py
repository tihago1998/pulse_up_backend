"""Contrato de /api/habitos: hábitos por fecha, completado y resumen para el calendario."""
from tests.helpers import cabeceras, usuario_con_token


def _crear(client, token, descripcion="Beber agua", **extra):
    return client.post("/api/habitos/", headers=cabeceras(token), json={"descripcion": descripcion, **extra})


def test_habitos_exigen_token(client):
    assert client.get("/api/habitos/").status_code == 401
    r = client.get("/api/habitos/", headers={"Authorization": "Token abc"})
    assert r.status_code == 401
    assert r.get_json()["error"] == "Token no proporcionado"


def test_crear_habito_con_categoria_por_defecto(client):
    _, token = usuario_con_token(client)
    r = _crear(client, token, fecha="2026-11-10")
    assert r.status_code == 201
    assert r.get_json()["message"] == "Hábito registrado"
    habitos = client.get("/api/habitos/", headers=cabeceras(token)).get_json()["habitos"]
    assert habitos == [{"id": r.get_json()["id"], "descripcion": "Beber agua", "categoria": "General",
                        "fecha": "2026-11-10", "completado": False}]


def test_crear_habito_sin_descripcion(client):
    _, token = usuario_con_token(client)
    r = _crear(client, token, descripcion="   ")
    assert r.status_code == 400
    assert r.get_json()["error"] == "La descripción es obligatoria"


def test_crear_habito_con_fecha_invalida(client):
    _, token = usuario_con_token(client)
    assert _crear(client, token, fecha="10/11/2026").status_code == 400


def test_listar_filtrando_por_fecha(client):
    _, token = usuario_con_token(client)
    _crear(client, token, "A", fecha="2026-11-10")
    _crear(client, token, "B", fecha="2026-11-11")
    r = client.get("/api/habitos/?fecha=2026-11-11", headers=cabeceras(token))
    assert [h["descripcion"] for h in r.get_json()["habitos"]] == ["B"]
    assert client.get("/api/habitos/?fecha=ayer", headers=cabeceras(token)).status_code == 400


def test_marcar_completado(client):
    _, token = usuario_con_token(client)
    id_habito = _crear(client, token, fecha="2026-11-10").get_json()["id"]
    r = client.patch(f"/api/habitos/{id_habito}/completado", headers=cabeceras(token), json={"completado": True})
    assert r.status_code == 200
    habito = client.get("/api/habitos/", headers=cabeceras(token)).get_json()["habitos"][0]
    assert habito["completado"] is True


def test_marcar_completado_sin_campo(client):
    _, token = usuario_con_token(client)
    id_habito = _crear(client, token).get_json()["id"]
    r = client.patch(f"/api/habitos/{id_habito}/completado", headers=cabeceras(token), json={})
    assert r.status_code == 400


def test_cada_usuario_ve_y_modifica_solo_lo_suyo(client):
    _, token_ana = usuario_con_token(client, "Ana", "ana@test.com")
    _, token_luis = usuario_con_token(client, "Luis", "luis@test.com")
    id_habito = _crear(client, token_ana).get_json()["id"]
    assert client.get("/api/habitos/", headers=cabeceras(token_luis)).get_json()["habitos"] == []
    r = client.patch(f"/api/habitos/{id_habito}/completado", headers=cabeceras(token_luis), json={"completado": True})
    assert r.status_code == 404
    assert r.get_json()["error"] == "Hábito no encontrado"


def test_resumen_por_dias(client):
    _, token = usuario_con_token(client)
    a = _crear(client, token, "A", fecha="2026-11-10").get_json()["id"]
    _crear(client, token, "B", fecha="2026-11-10")
    _crear(client, token, "C", fecha="2026-11-12")
    client.patch(f"/api/habitos/{a}/completado", headers=cabeceras(token), json={"completado": True})
    r = client.get("/api/habitos/resumen?desde=2026-11-01&hasta=2026-11-30", headers=cabeceras(token))
    assert r.status_code == 200
    assert r.get_json()["dias"] == [
        {"fecha": "2026-11-10", "total": 2, "completados": 1},
        {"fecha": "2026-11-12", "total": 1, "completados": 0},
    ]


def test_resumen_con_fechas_invalidas(client):
    _, token = usuario_con_token(client)
    assert client.get("/api/habitos/resumen?desde=x&hasta=y", headers=cabeceras(token)).status_code == 400
    assert client.get("/api/habitos/resumen", headers=cabeceras(token)).status_code == 400
