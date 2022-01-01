#!/bin/bash

echo Choisissez entre les environements: dev ou prod
read env

if [ $env != "dev" ] && [ $env != "prod" ]
then
  echo "choisissez correctement dev ou prod!"
else
  cp ./config/$env/docker/docker-compose.yml ./
  cp ./config/$env/docker/Dockerfile ./
fi
docker-compose up -d --build
echo "Super, l'environnement $env est prêt"