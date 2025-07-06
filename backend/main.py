from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import database
import models
import auth
from pydantic import BaseModel

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# ✅ ROTA RAIZ PARA EVITAR 404 AO ACESSAR "/"
@app.get("/")
def root():
    return {"mensagem": "API Solar ativa!"}

class DadoEntrada(BaseModel):
    gerado_kwh: float
    consumido_kwh: float

def get_db():
    db = database.SessionLocal()
    try:
        yield db  # corrigido: estava "yield dbls", que causaria erro
    finally:
        db.close()

@app.post("/dados")
def receber_dado(dado: DadoEntrada, db: Session = Depends(get_db)):
    novo = models.DadoEnergia(**dado.dict())
    db.add(novo)
    db.commit()
    return {"mensagem": "Dado registrado com sucesso"}

@app.get("/dados")
def listar_dados(authorization: str = Header(None), db: Session = Depends(get_db)):
    token = authorization.split(" ")[1] if authorization else ""
    usuario = auth.verificar_token(token)
    if not usuario:
        raise HTTPException(status_code=401, detail="Token inválido")
    return db.query(models.DadoEnergia).all()

@app.post("/cadastrar")
def cadastrar(email: str, senha: str, db: Session = Depends(get_db)):
    if db.query(models.Usuario).filter(models.Usuario.email == email).first():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    user = models.Usuario(email=email, senha_hash=auth.gerar_hash_senha(senha))
    db.add(user)
    db.commit()
    return {"mensagem": "Usuário cadastrado"}

@app.post("/login")
def login(email: str, senha: str, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user or not auth.verificar_senha(senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = auth.criar_token({"sub": user.email})
    return {"access_token": token}