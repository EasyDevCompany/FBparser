FROM python:3.10.4 
 
WORKDIR /code 
RUN echo "deb http://deb.debian.org/debian/ unstable main contrib non-free" >> /etc/apt/sources.list.d/debian.list 
RUN apt-get update 
RUN apt-get install -y --no-install-recommends firefox 
COPY requirements.txt requirements.txt 
RUN pip install -r requirements.txt 
COPY . . 
CMD celery -A celery_conf worker -l INFO -P eventlet -c 2