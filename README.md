# Foodrgam

 Food Assistant - Graduate work for the Yandex.Practicum Course on Django and DRF.

 This is an online service and its API.

 Here, users can:
- Publish recipes,
- Subscribe to other users' publications,
- Download a shopping list before heading to the store. :grinning:

## About the Project

- The project is wrapped in Docker containers;
- The project was deployed on the server: <http://158.160.80.191/>
  
## Tech Stack
- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker

## Dependencies
- Listed in the file backend/requirements.txt


## To Run Locally

1. Clone the repository to your GitHub.
2. From the `/infra/` directory, run the command: `docker-compose up -d --build`
3. Perform migrations: `python manage.py makemigrations`, `python manage.py migrate`
4. Create an administrator `python manage.py createsuperuser`
5. Collect static files `python manage.py collectstatic`
6. Load fixtures into the database `python recipes/utils.py`
