FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Secrets are injected at runtime via env (docker run --env-file .env / compose env_file),
# not baked into the image. .env is excluded by .dockerignore.
CMD ["python", "run.py"]
