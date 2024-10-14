# Qoop Technical Interview: Backend API Service

This project is the API backend service developed to complete a technical interview for the **qoop.ai company.**

To develop this project, I will use the following technologies:

- Python will be the programming language.
- FastAPI will be the backend framework to build the APIs.
- PostgreSQL will be the relational database, using the SQLAlchemy ORM.
- Python and FastAPI libraries.

Although this project was designed for a specific purpose, its code is under an **open-source software license.**

_All information presented in this project is fictitious and does not represent real (**valid**) data._

## API Functionality

This API allows users to sign up and subscribe to the platform (for a complete experience) to use a project management backend service to create projects, add team members, assign tasks, and track progress.

Full use of the platform is available _only_ to users with an active subscription. Non-subscribed users can register but cannot create or manage projects.

## Build/CLI Instructions

Before installing and running the application, you **should create** a Python virtual environment. The official documentation can provide help if you need it.

To run the FastAPI service, run the following CLI command:

```cli
fastapi dev app/main.py
```

To build the FastAPI service for production, run the following command:

```cli
fastapi build app/main.py
```

To test, run the following command:

```cli
pytest
```

### Configuration and Environment Variables

This project uses different **environment variables** to configure the application functionality. The following list shows each variable along its definition.

_You need to pass the variables so the application can run._

The following list are the environment variables used on this project:

- DEBUG
- ALLOWED_ORIGINS
- STRIPE_SECRET_KEY
- STRIPE_MONTHLY_PRICE_ID
- STRIPE_ANNUAL_PRICE_ID
- STRIPE_SUCCESS_URL
- STRIPE_CANCEL_URL
