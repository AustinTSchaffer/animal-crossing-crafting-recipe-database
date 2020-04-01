FROM python:3-alpine

EXPOSE 8000

RUN pip install 'gunicorn>=20,<21'

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app.py app.py

COPY data data

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "app:app" ]
