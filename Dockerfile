FROM python:3.10.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app

WORKDIR /app/

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2

# os의 core 개수에 따라 유동적으로 worker 설정(core_count * 2 + 1)
ENTRYPOINT  sh -c "python manage.py collectstatic --no-input && python manage.py migrate && gunicorn cancruit.wsgi --workers=$((2 * $(getconf _NPROCESSORS_ONLN) + 1)) -b 0.0.0.0:8000 --preload"
