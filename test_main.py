from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_suggest():
    response = client.post("/suggest", json={"query": "¿Cómo cambio mi contraseña?"})
    assert response.status_code == 200
    assert response.json()["suggestion"] == "Puedes cambiar tu contraseña en la sección de configuración de tu perfil."

def test_empty_query():
    response = client.post("/suggest", json={"query": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "La consulta no puede estar vacía."}

def test_no_match():
    response = client.post("/suggest", json={"query": "¿Cómo vuelo a la luna?"})
    assert response.status_code == 200
    assert response.json() == {"suggestion": "No se encontró una respuesta."}

def test_history():
    response = client.get("/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list) or "message" in response.json()

def test_add_question():
    new_question = {
        "pregunta": "¿Dónde puedo ver mi factura?",
        "respuesta": "Puedes ver tu factura en la sección de facturación de tu perfil."
    }
    response = client.post("/add_question", json=new_question)
    assert response.status_code == 200
    assert response.json() == {"message": "Pregunta añadida exitosamente."}

    # Verificar que la nueva pregunta se pueda buscar
    response = client.post("/suggest", json={"query": "¿Dónde puedo ver mi factura?"})
    assert response.status_code == 200
    assert response.json()["suggestion"] == new_question["respuesta"]