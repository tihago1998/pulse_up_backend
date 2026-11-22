from tests.helpers import cabeceras, usuario_con_token


def _ids_ejercicios(client, h, n=2):
    return [e["id"] for e in client.get("/api/ejercicios/", headers=h).get_json()["ejercicios"][:n]]


def _rutina_valida(ids):
    return {
        "nombre": "Mi rutina",
        "objetivo": "fuerza",
        "nivel": "intermedio",
        "duracion_min": 50,
        "ejercicios": [
            {"id_ejercicio": ids[0], "series": 4, "repeticiones": "8-10", "descanso_seg": 90},
            {"id_ejercicio": ids[1], "series": 3, "repeticiones": "12"},
        ],
    }


def test_rutinas_requieren_token(client):
    assert client.get("/api/rutinas/").status_code == 401


def test_usuario_nuevo_ve_las_plantillas(client):
    h = cabeceras(usuario_con_token(client)[1])
    rutinas = client.get("/api/rutinas/", headers=h).get_json()["rutinas"]
    assert len(rutinas) == 7
    assert all(r["es_plantilla"] for r in rutinas)


def test_filtrar_por_objetivo(client):
    h = cabeceras(usuario_con_token(client)[1])
    rutinas = client.get("/api/rutinas/?objetivo=resistencia", headers=h).get_json()["rutinas"]
    assert rutinas and all(r["objetivo"] == "resistencia" for r in rutinas)


def test_detalle_de_plantilla_trae_ejercicios_en_orden(client):
    h = cabeceras(usuario_con_token(client)[1])
    primera = client.get("/api/rutinas/", headers=h).get_json()["rutinas"][0]
    rutina = client.get(f"/api/rutinas/{primera['id']}", headers=h).get_json()["rutina"]
    assert [e["orden"] for e in rutina["ejercicios"]] == list(range(1, len(rutina["ejercicios"]) + 1))
    assert rutina["ejercicios"][0]["ejercicio"]["instrucciones"]


def test_crear_rutina_propia(client):
    h = cabeceras(usuario_con_token(client)[1])
    ids = _ids_ejercicios(client, h)
    r = client.post("/api/rutinas/", json=_rutina_valida(ids), headers=h)
    assert r.status_code == 201
    detalle = client.get(f"/api/rutinas/{r.get_json()['id']}", headers=h).get_json()["rutina"]
    assert detalle["es_plantilla"] is False
    assert len(detalle["ejercicios"]) == 2
    assert detalle["ejercicios"][1]["descanso_seg"] == 60  # valor por defecto


def test_las_rutinas_propias_aparecen_primero(client):
    h = cabeceras(usuario_con_token(client)[1])
    client.post("/api/rutinas/", json=_rutina_valida(_ids_ejercicios(client, h)), headers=h)
    rutinas = client.get("/api/rutinas/", headers=h).get_json()["rutinas"]
    assert len(rutinas) == 8 and rutinas[0]["es_plantilla"] is False


def test_rutina_de_otro_usuario_no_es_visible(client):
    h1 = cabeceras(usuario_con_token(client, "Ana", "ana@test.com")[1])
    h2 = cabeceras(usuario_con_token(client, "Beto", "beto@test.com")[1])
    id_r = client.post("/api/rutinas/", json=_rutina_valida(_ids_ejercicios(client, h1)), headers=h1).get_json()["id"]
    assert client.get(f"/api/rutinas/{id_r}", headers=h2).status_code == 404
    assert client.delete(f"/api/rutinas/{id_r}", headers=h2).status_code == 404
    assert len(client.get("/api/rutinas/", headers=h2).get_json()["rutinas"]) == 7


def test_crear_rutina_validaciones(client):
    h = cabeceras(usuario_con_token(client)[1])
    ids = _ids_ejercicios(client, h)
    base = _rutina_valida(ids)
    casos = [
        {**base, "nombre": "  "},
        {**base, "objetivo": "volar"},
        {**base, "nivel": "dios"},
        {**base, "duracion_min": 0},
        {**base, "ejercicios": []},
        {**base, "ejercicios": [{"id_ejercicio": 99999, "series": 3, "repeticiones": "10"}]},
        {**base, "ejercicios": [{"id_ejercicio": ids[0], "series": 0, "repeticiones": "10"}]},
        {**base, "ejercicios": [{"id_ejercicio": ids[0], "series": 3, "repeticiones": ""}]},
    ]
    for cuerpo in casos:
        assert client.post("/api/rutinas/", json=cuerpo, headers=h).status_code == 400, cuerpo


def test_eliminar_rutina_propia(client):
    h = cabeceras(usuario_con_token(client)[1])
    id_r = client.post("/api/rutinas/", json=_rutina_valida(_ids_ejercicios(client, h)), headers=h).get_json()["id"]
    assert client.delete(f"/api/rutinas/{id_r}", headers=h).status_code == 200
    assert client.get(f"/api/rutinas/{id_r}", headers=h).status_code == 404


def test_no_se_pueden_eliminar_plantillas(client):
    h = cabeceras(usuario_con_token(client)[1])
    plantilla = client.get("/api/rutinas/", headers=h).get_json()["rutinas"][0]
    assert client.delete(f"/api/rutinas/{plantilla['id']}", headers=h).status_code == 403


def test_eliminar_usuario_borra_sus_rutinas(client, db_path):
    import sqlite3

    from tests.helpers import usuario_con_rol

    id_u, token = usuario_con_token(client, "Ana", "ana@test.com")
    h = cabeceras(token)
    client.post("/api/rutinas/", json=_rutina_valida(_ids_ejercicios(client, h)), headers=h)
    _, token_super = usuario_con_rol(client, db_path, [3], "Root", "root@test.com")
    assert client.delete(f"/api/users/{id_u}", headers=cabeceras(token_super)).status_code == 200
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM rutina WHERE id_usuario = ?", (id_u,)).fetchone()[0] == 0
    conn.close()
