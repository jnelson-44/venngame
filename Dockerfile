FROM python:3.14-slim

RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000

CMD ["fastapi", "run", "--port", "8000"]
