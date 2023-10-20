#!/bin/bash

docker run -d -p 5433:5432 \
    --env POSTGRES_USER=postgres \
    --env POSTGRES_PASSWORD=password \
    --env POSTGRES_DB=postgres \
    postgres:alpine
