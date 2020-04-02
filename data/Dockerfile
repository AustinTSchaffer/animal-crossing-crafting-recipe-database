FROM python:3-buster

LABEL maintainer="Austin Schaffer <schaffer.austin.t@gmail.com>"

RUN \
    apt update -y \
    && apt install -y firefox-esr \
    && rm -rf /var/lib/apt/lists/*

RUN \
    wget "https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz" \
    && tar -xvzf geckodriver* \
    && chown root:root geckodriver \
    && chmod 777 geckodriver \
    && mv geckodriver /bin/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY app.py app.py

CMD [ "python", "app.py" ]
