FROM python:3

COPY ./flask_app/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENV FLASK_RUN_HOST="0.0.0.0"
ENV FLASK_RUN_PORT=8080
ENV REDIS_HOST="0.0.0.0"
ENV REDIS_PORT=8081

ENTRYPOINT [ "flask" , "--app", "flask_app/app.py", "run"]

