FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser \
    && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "-u", "main.py"]