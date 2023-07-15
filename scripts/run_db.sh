
#! /env/bin/bash -e

docker run --name dev-postgres -e POSTGRES_PASSWORD=MySecretPassword123docker -p 5432:5432 -d postgres