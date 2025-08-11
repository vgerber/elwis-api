# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies with uv
RUN uv pip install --system --requirement <(uv pip compile pyproject.toml)

# Copy app code
COPY . .

# Expose port (adjust if your FastAPI app uses a different port)
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "elwis_api.__main__:app", "--host", "0.0.0.0", "--port", "8000"]
