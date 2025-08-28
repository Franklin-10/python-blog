#!/bin/sh

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo " Waiting for Postgres Databse Startup ($POSTGRES_HOST $POSTGRES_PORT) ..."
  sleep 2
done

echo "Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"