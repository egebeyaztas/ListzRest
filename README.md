
# Listz Movie API

Movie and Watchlist API for public use will be available soon.

App has not deployed yet.


## Installation 

Clone the project

```bash
git clone https://github.com/egebeyaztas/ListzRest.git
```

Install the requirements

```bash 
  pip install -r requirements.txt
  cd ListzRest
```

Configure the database with your Postgres Credentials

```bash
  DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Make migrations and migrate to db

```bash
  python manage.py makemigrations
  python manage.py migrate
```

You can dump some dummy data to test the api at the moment

```bash
  python manage.py createsuperuser
  python manage.py runserver
```
### API Usage Examples

#### Get all movies from database

```http
  GET /api/v1/get_movie_list
```

| Parameter | Type     | Statement                |
| :-------- | :------- | :------------------------- |
| `` | `list` | All movies |

#### Get all watchlists from a specific user

```http
  GET /api/v1/get_watchlist/${user}
```

| Parameter | Type     | Statement                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. User watchlists



  
## Api Doc Screenshot

![Screenshot](https://user-images.githubusercontent.com/77864932/229279125-9b971e43-a3c3-49c5-87a6-a72c258321f9.png)

  
### Associated Projects

Here is the restricted codebase of the Project's MVT version with frontend implementations.

[Listz Public Code](https://github.com/egebeyaztas/Listz-public)

  
##



[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

  