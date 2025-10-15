# Backend — TCG Universe (MVP)

## Avvio locale
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
uvicorn app.main:app --reload
```
Apri http://127.0.0.1:8000/docs

## Avvio con Docker
```bash
docker build -t tcg-universe-api .
docker run -p 8080:8080 --env-file .env tcg-universe-api
```
Apri http://127.0.0.1:8080/docs
