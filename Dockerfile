FROM python:3.11-slim

WORKDIR /app
COPY manage.py pyproject.toml poetry.lock ./

# configure Poetry
ENV POETRY_VERSION=1.6.1

# installing Poetry
RUN pip install poetry==${POETRY_VERSION} && poetry install --no-root --no-directory
COPY toktik_backend/ ./toktik_backend/
COPY authentication/ ./authentication/
COPY video/ ./video/
RUN poetry install --only main

# run the application
CMD ["poetry", "run", "gunicorn", "toktik_backend.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
