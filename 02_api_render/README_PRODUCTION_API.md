# ZENOV Production API

Upload the contents of this folder to the production API repository.

Recommended GitHub repository:

```text
zenov-api
```

Render start command:

```bash
python3 -m uvicorn render_api.main:app --host 0.0.0.0 --port $PORT
```

This API stores Partner Folder submissions in PostgreSQL through `DATABASE_URL`.

