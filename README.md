# Yatube
### The description:
The source code of [Yatube project](https://19serge94.pythonanywhere.com/).

This is a blog with basic social network features. Authorised users can create, comment posts.
The posts can be organised to the groups according thier topic. 
The users can follow each other and subscribe to the post's topics.
Guests can only watch the content.

Stack:
 - Python 3.7
 - Django 2.2.19

### Local deployment (development mode)
- Clone the repo, create and activate the virtual Python enviroment.
```sh
python3 -m venv venv
source ./venv/bin/activate
```
- Install the requirements
```sh
pip install -r requirements.txt
``` 
- Write the Django Key to enviroment variable
```sh
export DJANGO_KEY=SECRET_KEY_VALUE
```
- Run the server:
```sh
python3 yatube/manage.py runserver
```
