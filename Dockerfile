# syntax=docker/dockerfile:1

FROM python:3.12-slim-bookworm

WORKDIR /flask_led

COPY venv/requirements.txt venv/requirements.txt
RUN pip3 install -r venv/requirements.txt

COPY . .

CMD [ "python3", "-m", "flask", "--app" , "src", "run", "--host=0.0.0.0"]