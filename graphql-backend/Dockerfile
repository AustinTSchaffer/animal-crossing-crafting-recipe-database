FROM python:3-alpine

LABEL maintainer="Austin Schaffer <schaffer.austin.t@gmail.com>"

EXPOSE 8000
RUN pip install 'gunicorn>=20,<21'

RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv install --deploy --system

COPY app.py app.py
COPY data data

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "app:app" ]
