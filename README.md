
# AutoCommerce AI – Backend mínimo FastAPI

Proyecto base listo para desplegar en Render con FastAPI.

## Estructura

- `app/main.py` – crea la app de FastAPI y monta los routers.
- `app/routers/` – endpoints (`products`, `orders`, `health`).
- `app/services/` – lógica de negocio de ejemplo.
- `app/core/` – configuración y base de datos (esqueleto).
- `requirements.txt` – dependencias para Render.

## Ejecutar localmente

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visita: http://127.0.0.1:8000

## Configuración en Render

- **Build Command**

  ```bash
  pip install -r requirements.txt
  ```

- **Start Command**

  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
