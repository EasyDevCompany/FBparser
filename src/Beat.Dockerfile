FROM python:3.10.4

WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD celery -A celery_conf beat -l INFO