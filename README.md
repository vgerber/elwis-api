# elwis-api

### Build and Run with Docker (PostgreSQL)

1. **Build the Docker image:**

   ```
   docker build -t vgerber/elwis-server:latest .
   ```

2. **Set up secrets for cache update authentication:**

   Create the `secrets` directory and the required files:

   ```bash
   mkdir -p secrets
   echo "your-username" > secrets/cache_update_user
   echo "your-password" > secrets/cache_update_password
   ```

   Replace `your-username` and `your-password` with your desired credentials.

3. **Run with Docker Compose:**
   ```
   docker compose up
   ```

This will start both the FastAPI server and a PostgreSQL database. The database data will be stored in the `./pgdata` directory.

- The app will be available at `http://localhost:8000` (adjust the port as needed).
- Database connection details are set via environment variables in `docker-compose.yml`.
- You can customize the database user, password, and name in the compose file as needed.
- The `/cache/update` endpoint is protected with HTTP Basic Auth using the credentials from the secrets files.

### Manual Run (Advanced)

If you want to run the server container and connect to an external Postgres instance, set the following environment variables:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

Example:

```
docker run -d -p 8000:8000 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=postgres \
  -e POSTGRES_HOST=localhost \
  -e POSTGRES_PORT=5432 \
  vgerber/elwis-server:latest
```

---
