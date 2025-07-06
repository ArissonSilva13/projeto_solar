from sqlalchemy import Column, Integer, Float, DateTime, String
from datetime import datetime
from database import Base

class DadoEnergia(Base):
    __tablename__ = "dados_energia"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    gerado_kwh = Column(Float)
    consumido_kwh = Column(Float)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)