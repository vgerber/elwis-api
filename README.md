# elwis-api

### Run the server

```
docker run -d -p 8000:8000 -v database.db:/app/database.db vgerber/elwis-server:latest
```

- The app will be available at `http://localhost:8000` (adjust the port as needed).
- You can pass environment variables or mount volumes as needed for your configuration.

---
