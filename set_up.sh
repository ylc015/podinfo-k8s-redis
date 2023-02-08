#! /usr/bin/env bash

docker build -t flask_app:2.4 .
docker-compose down
docker-compose up -d
