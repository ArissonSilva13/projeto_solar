@echo off
echo =======================
echo Ativando ambiente...
call venv\Scripts\activate

echo =======================
echo Iniciando API (porta 8000)...
start cmd /k "cd backend && uvicorn main:app --reload"
timeout /t 2 > nul

echo =======================
echo Iniciando Painel Administrativo (porta 8501)...
start cmd /k "cd painel_admin && streamlit run Home.py"
timeout /t 2 > nul

echo =======================
echo ✅ Tudo rodando! Acesse:
echo - http://localhost:8000/docs       → Backend API
echo - http://localhost:8501            → Painel com páginas (inclui simulador)
pause
