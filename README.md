# Applifting microservice exercise

This is an exercise I did as an pre-interview task for Applifting. The task was to create a REST API JSON Python microservice which allows users to browse a product catalog and which automatically updates prices from a offer service.

More details about the task can be found in the [assignment.md](assignment.md) file or on their [website](https://python.exercise.applifting.cz).

## How to run the project

### Using Docker Compose

#### Prerequisites

You need to have Docker and Docker Compose installed on your machine. You can download and install them from the following links:

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

#### Steps

1. Clone the repository.

```bash
git clone https://github.com/gvarph/applifting_exercise.git
cd applifting_exercise
```

2. Edit the docker-compose.yml file.

While this is technically not necessary, it is greatly recommended to edit the environment variables in the [docker-compose.yml](docker-compose.yml) file. The following variables can be edited:

-   `DATABASE_URL`: Change the SAMPLEPASSWORD to a secure password. This is the password used for the PostgreSQL database. You can also point this to a different database if you want.
-   `TOKEN_SECRET`: This is the secret key got from applifting. The default one won't work.
-   `API_URL`: This is the url of the offers microservice. THe default value is the one provided by applifting.
-   `LOG_LEVEL`: This is the log level of the application. The default value is `INFO`. You can change it to `DEBUG` if you want to see more detailed logs.
-   `JWT_SECRET`: This is the secret key used for the JWT authentication. It is recommended to change this to a more secure key.

In the postgres service, you have to change SAMPLEPASSWORD to the same password you used in the `DATABASE_URL` environment variable.

If you want to use your own database, simply delete the postgres service and change the `DATABASE_URL` environment variable to point to your database.

3. Run the application using Docker Compose:

```bash
docker-compose up -d
```

This will run a single instance of the microservice, and will also run a PostgreSQL database instance.

It is also possible to edit the environment variables, port or database or event he url in the [docker-compose.yml](docker-compose.yml) file.

### On your local machine

Not sure if this is necessary, will update later.

## Coverage:

```
---------- coverage: platform linux, python 3.10.12-final-0 ----------
Name                      Stmts   Miss Branch BrPart  Cover
-----------------------------------------------------------
src/auth.py                  31     31      2      0     0%
src/background.py            28     28      6      0     0%
src/db.py                    20      0      0      0   100%
src/env.py                   20      3      6      3    77%
src/errors.py                28      8      0      0    71%
src/logger.py                11      0      0      0   100%
src/main.py                  18     18      0      0     0%
src/models.py                56      1     10      0    98%
src/offers.py               147     92     44      2    32%
src/schemas.py               41      2      0      0    95%
src/services/product.py      72     48     34      0    26%
src/util.py                  15     15      0      0     0%
-----------------------------------------------------------
TOTAL                       487    246    102      5    45%
```
