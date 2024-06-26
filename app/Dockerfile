FROM python:3.12-alpine

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./app/ /app/

WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
