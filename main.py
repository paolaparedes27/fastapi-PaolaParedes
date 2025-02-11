from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from difflib import get_close_matches

app = FastAPI()

# Base de conocimiento (almacenada en memoria)
knowledge_base = [
    {"pregunta": "¿Cómo cambio mi contraseña?", "respuesta": "Puedes cambiar tu contraseña en la sección de configuración de tu perfil."},
    {"pregunta": "¿Cuál es el horario de atención?", "respuesta": "Nuestro horario es de lunes a viernes de 8 am a 5 pm."}
]

# Historial en memoria (Persistencia temporal)
history = []

class QueryModel(BaseModel):
    query: str

class KnowledgeEntry(BaseModel):
    pregunta: str
    respuesta: str

@app.post("/suggest", summary="Obtiene una sugerencia basada en la consulta del usuario.")
def suggest(query: QueryModel):
    pregunta = query.query.strip()

    if not pregunta:
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía.")

    matches = get_close_matches(pregunta, [item["pregunta"] for item in knowledge_base], n=1, cutoff=0.4)
    
    if matches:
        respuesta = next((item["respuesta"] for item in knowledge_base if item["pregunta"] == matches[0]), "No se encontró una respuesta.")
    else:
        respuesta = "No se encontró una respuesta."

    # Evitar duplicados en el historial
    if not any(h["query"] == pregunta for h in history):
        history.append({"query": pregunta, "suggestion": respuesta})
    
    return {"suggestion": respuesta}

@app.get("/history", summary="Devuelve el historial de consultas y sugerencias.")
def get_history():
    if not history:
        return {"message": "No hay historial disponible."}
    return history

@app.post("/add_question", summary="Agrega una nueva pregunta y respuesta a la base de conocimiento.")
def add_question(entry: KnowledgeEntry):
    if any(item["pregunta"] == entry.pregunta for item in knowledge_base):
        raise HTTPException(status_code=400, detail="La pregunta ya existe en la base de conocimiento.")
    
    knowledge_base.append({"pregunta": entry.pregunta, "respuesta": entry.respuesta})
    return {"message": "Pregunta añadida exitosamente."}

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}


