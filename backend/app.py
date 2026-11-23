from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, Float, DateTime, desc

from database import Base, engine, get_db
from fastapi.responses import FileResponse


# Crear la aplicación
app = FastAPI(
    title="Smart Irrigation API",
    description="API para controlar un sistema de riego automático",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent
print("BASE_DIR:", BASE_DIR)
print("RUTA CSS:", BASE_DIR / "frontend" / "static" / "css" / "style.css")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "frontend" / "static"),
    name="static"
)

templates = Jinja2Templates(directory=BASE_DIR / "frontend" / "templates")


@app.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse(request, "index.html")


# Modelo de la base de datos
class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    humidity = Column(Float, nullable=False)
    soil_raw = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


# Crear las tablas
Base.metadata.create_all(bind=engine)


# Ruta principal
@app.get("/")
def home():
    return {
        "message": "Bienvenido a Smart Irrigation",
        "status": "API funcionando"
    }


# Estado del servidor
@app.get("/api/status")
def status(db: Session = Depends(get_db)):
    last_reading = (
        db.query(SensorReading)
        .order_by(desc(SensorReading.id))
        .first()
    )

    online = False

    if last_reading:
        online = (
            datetime.now(timezone.utc)
            - last_reading.created_at.replace(tzinfo=timezone.utc)
        ).total_seconds() < 60

    return {
        "device_online": online,
        "last_humidity": (
            last_reading.humidity if last_reading else None
        )
    }


# Recibir mediciones del ESP32
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


# Consultar las últimas mediciones
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
            "id": r.id,
            "humidity": r.humidity,
            "soil_raw": r.soil_raw,
            "created_at": r.created_at
        }
        for r in readings
    ]
@app.get("/sw.js")
def service_worker():
    return FileResponse(
        BASE_DIR / "frontend" / "static" / "sw.js",
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"}
    )
