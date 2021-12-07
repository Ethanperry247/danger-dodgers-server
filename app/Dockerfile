# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
FROM python:3.9

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY ./app /app

# RUN uvicorn app.main:app --proxy-headers --host 0.0.0.0 --port ${PORT:-5000}

# CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", ${PORT:-5000}]

COPY ./start.sh /start.sh

RUN chmod +x /start.sh

CMD ["./start.sh"]