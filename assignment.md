Create a REST API JSON Python microservice which allows users to browse a product catalog and which automatically updates prices from the offer service, provided by us:
    Swagger
    Redoc

Requirements

    Provide an API to create, update and delete products
    Periodically query the provided microservice for offers
    Provide an API to get product offers

Data model

Products - each product corresponds to a real world product you can buy.
    id - UUID
    name - string
    description - string

A product has many offers.

Offers - each offer represents a product offer being sold for a price.

    id - UUID
    price - integer
    items_in_stock - integer

Each offer belongs to one product.
Specification

Must haves:

- [x] Use an SQL database as an internal data store; the library for the API layer is up to you
- [x] Use an access token from sign-up to access the offers microservice - this should be done only once, all your registered products are tied to this token
- [x] To authenticate your requests, use a Bearer: <access-token> header
- [x] Create CRUD for products
- [x] Once a new product is created, call the offers microservice to register it
- [x] Your API does not need authentication
- [x] Create a background service which periodically calls the offers microservice to request offers for your products
- [x] Price in the offers microservice updates every minute, and offers sell out
- [x] Once an offer sells out, it is replaced by another one
- [x] Create a read-only API for product offers
- [x] Base URL for the offers microservice should be configurable via an environment variable
- [x] Write basic tests with pytest
- [ ] Add a README with information on how to start & use your service
- [x] Push your code into git repository and send us access (our preference is gitlab.com)

You can earn extra points for:

- [ ] JSON REST API simple authentication (e.g. access-token)
- [ ] Consider adding some reasonable error handling to the API layer
- [ ] Provide a working Dockerfile and docker-compose.yml for your application for easy testing
- [x] Use reasonable dependency management (requirements.txt, Pipenv, Poetry, ...)
- [ ] Deploy your application to Heroku
- [ ] Track the history of offer prices and create an endpoint which returns the trend in offer prices and compute the percentual rise / fall in price for a chosen period of time