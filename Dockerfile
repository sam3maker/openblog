FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN curl -o /app/isrgrootx1.pem https://letsencrypt.org/certs/isrgrootx1.pem

COPY . .

EXPOSE 7860

CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:7860"]
