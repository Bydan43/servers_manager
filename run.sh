#!/bin/bash

if [[ "${MIGRATE}" == "true" ]]; then
  echo "Migrate status = ${MIGRATE}"
  CURENT_DATE=$(date +"%d-%m-%Y__%H-%M")
  flask db init
  flask db migrate -m "Migrate $CURENT_DATE"
  flask db upgrade
fi
gunicorn  --bind :5000 --workers 3 run:app

