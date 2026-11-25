
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

from pydantic import BaseModel

from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, Float, DateTime, desc

from database import Base, engine, get_db


# ==========================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ==========================================

app = FastAPI(
    title="Smart Irrigation API",
    description="API para controlar un sistema de riego automático",
    version="1.0.0"
)


# ==========================================
# CONFIGURACIÓN DE RUTAS Y ARCHIVOS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

print("BASE_DIR:", BASE_DIR)
print(
    "RUTA CSS:",
    BASE_DIR / "frontend" / "static" / "css" / "style.css"
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "frontend" / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "frontend" / "templates"
)


# ==========================================
# ESTADO DE LA BOMBA (SIMULACIÓN)
# ==========================================

app.state.pump_on = False


# ==========================================
# MODELO PARA CONTROLAR LA BOMBA
# ==========================================

class PumpCommand(BaseModel):
    state: Literal["on", "off"]


# ==========================================
# MODELO DE LA BASE DE DATOS
# ==========================================

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)

    humidity = Column(Float, nullable=False)

    soil_raw = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


# ==========================================
# CREAR LAS TABLAS
# ==========================================

Base.metadata.create_all(bind=engine)


# ==========================================
# DASHBOARD
# ==========================================

@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html"
    )


# ==========================================
# RUTA PRINCIPAL
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Bienvenido a Smart Irrigation",
        "status": "API funcionando"
    }


# ==========================================
# ESTADO DEL SERVIDOR Y SENSOR
# ==========================================

@app.get("/api/status")
def status(db: Session = Depends(get_db)):

    last_reading = (
        db.query(SensorReading)
        .order_by(desc(SensorReading.id))
        .first()
    )

    online = False

    if last_reading:
        reading_date = last_reading.created_at

        if reading_date.tzinfo is None:
            reading_date = reading_date.replace(
                tzinfo=timezone.utc
            )

        online = (
            datetime.now(timezone.utc) - reading_date
        ).total_seconds() < 60

    return {
        "device_online": online,
        "last_humidity": (
            last_reading.humidity
            if last_reading else None
        )
    }


# ==========================================
# RECIBIR MEDICIONES DEL ESP32
# ==========================================

@app.post("/api/readings")
def create_reading(
    humidity: float,
    soil_raw: int = None,
    db: Session = Depends(get_db)
):

    reading = SensorReading(
        humidity=humidity,
        soil_raw=soil_raw
    )

    db.add(reading)
    db.commit()
    db.refresh(reading)

    return {
        "message": "Medicion guardada correctamente",
        "id": reading.id,
        "humidity": reading.humidity
    }


# ==========================================
# CONSULTAR HISTORIAL DE MEDICIONES
# ==========================================

@app.get("/api/readings")
def get_readings(db: Session = Depends(get_db)):

    readings = (
        db.query(SensorReading)
        .order_by(desc(SensorReading.id))
        .limit(20)
        .all()
    )

    return [
        {
            "id": reading.id,
            "humidity": reading.humidity,
            "soil_raw": reading.soil_raw,
            "created_at": reading.created_at
        }
        for reading in readings
    ]


# ==========================================
# SERVICE WORKER
# ==========================================

@app.get("/sw.js")
def service_worker():

    return FileResponse(
        BASE_DIR / "frontend" / "static" / "sw.js",
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"}
    )


# ==========================================
# CONSULTAR ESTADO DE LA BOMBA
# ==========================================

@app.get("/api/pump")
def get_pump_status():

    return {
        "pump_on": app.state.pump_on,
        "mode": "simulation"
    }


# ==========================================
# ENCENDER Y APAGAR LA BOMBA
# ==========================================

@app.post("/api/pump")
def control_pump(command: PumpCommand):

    app.state.pump_on = command.state == "on"

    return {
        "success": True,
        "pump_on": app.state.pump_on,
        "message": (
            "Bomba encendida (simulación)"
            if app.state.pump_on
            else "Bomba apagada (simulación)"
        )
    }
