import os

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

DJANGO_API_URL = os.environ.get("DJANGO_API_URL", "http://127.0.0.1:8000/api")
DJANGO_TOKEN_URL = f"{DJANGO_API_URL}/token/"
DJANGO_USERNAME = os.environ.get("DJANGO_USERNAME", "riane")
DJANGO_PASSWORD = os.environ.get("DJANGO_PASSWORD", "")

app = FastAPI(title="Servicio de Notificaciones")


class NotificacionRequest(BaseModel):
    tramite_id: int
    destinatario: str
    mensaje: str


class NotificacionResponse(BaseModel):
    id: str
    estado: str
    tramite_id: int
    otro_campo: str


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/notificaciones", response_model=NotificacionResponse)
def crear_notificacion(payload: NotificacionRequest) -> NotificacionResponse:
    return NotificacionResponse(
        id="notif-001",
        estado="enviada",
        tramite_id=payload.tramite_id,
        otro_campo="valor adicional agregado por rianeiro",
    )

@app.get("/tramites/{tramite_id}/resumen")
async def resumen_tramite(tramite_id: int) -> dict[str, object]:
    token = await obtener_token_django()

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/tramites/{tramite_id}/",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        data = response.json()

    return {
        "tramite_id": data["id"],
        "nombre": data["nombre"],
        "estado": data["estado"],
        "total_comentarios": len(data["comentarios"]),
    }

async def obtener_token_django() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            DJANGO_TOKEN_URL,
            json={"username": DJANGO_USERNAME, "password": DJANGO_PASSWORD},
        )
        response.raise_for_status()
        return str(response.json()["access"])