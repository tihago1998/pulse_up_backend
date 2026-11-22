from tests.helpers import cabeceras, usuario_con_token


def _h(client):
    return cabeceras(usuario_con_token(client)[1])


def test_catalogo_requiere_token(client):
    assert client.get("/api/ejercicios/").status_code == 401


def test_listar_devuelve_catalogo_sin_instrucciones(client):
    r = client.get("/api/ejercicios/", headers=_h(client))
    assert r.status_code == 200
    ejercicios = r.get_json()["ejercicios"]
    assert len(ejercicios) >= 40
    assert "instrucciones" not in ejercicios[0]


def test_filtrar_por_musculo_y_equipo(client):
    h = _h(client)
    r = client.get("/api/ejercicios/?musculo=pecho&equipo=mancuernas", headers=h)
    ejercicios = r.get_json()["ejercicios"]
    assert ejercicios
    assert all(e["grupo_muscular"] == "pecho" and e["equipo"] == "mancuernas" for e in ejercicios)


def test_buscar_por_texto(client):
    r = client.get("/api/ejercicios/?q=sentadilla", headers=_h(client))
    nombres = [e["nombre"] for e in r.get_json()["ejercicios"]]
    assert nombres and all("sentadilla" in n.lower() for n in nombres)


def test_nivel_invalido(client):
    assert client.get("/api/ejercicios/?nivel=dios", headers=_h(client)).status_code == 400


def test_filtros_disponibles(client):
    r = client.get("/api/ejercicios/filtros", headers=_h(client))
    datos = r.get_json()
    assert "pecho" in datos["musculos"]
    assert "mancuernas" in datos["equipos"]
    assert datos["niveles"] == ["principiante", "intermedio", "avanzado"]


def test_detalle_incluye_instrucciones(client):
    h = _h(client)
    id_ej = client.get("/api/ejercicios/?q=Plancha", headers=h).get_json()["ejercicios"][0]["id"]
    r = client.get(f"/api/ejercicios/{id_ej}", headers=h)
    assert r.status_code == 200
    assert r.get_json()["ejercicio"]["instrucciones"]


def test_detalle_inexistente(client):
    assert client.get("/api/ejercicios/99999", headers=_h(client)).status_code == 404


def test_sembrar_dos_veces_no_duplica(app, client):
    from pulseup import inicializar_base_de_datos

    h = _h(client)
    antes = len(client.get("/api/ejercicios/", headers=h).get_json()["ejercicios"])
    inicializar_base_de_datos(app.config["DB_NAME"])
    despues = len(client.get("/api/ejercicios/", headers=h).get_json()["ejercicios"])
    rutinas = client.get("/api/rutinas/", headers=h).get_json()["rutinas"]
    assert antes == despues
    assert len(rutinas) == 7
