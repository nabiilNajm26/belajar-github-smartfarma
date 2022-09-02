# REST API With Flask & SQL Alchemy

> Smartfarma API using Python Flask, SQL Alchemy and Marshmallow

## Quick Start Using virtualenv

```bash
# Activate venv
$ python3 -m venv virtualenv
$ source virtualenv/bin/activate

# Install libraries
$ pip3 install flask
$ pip3 install mysql
$ pip3 install flask-mysql-connector
$ pip3 install flask_sqlalchemy
$ pip3 install flask_marshmallow
$ pip3 install flask_migrate
$ pip3 install bcrypt
$ pip3 install pyjwt
$ pip3 install python-dotenv
$ pip3 install marshmallow-sqlalchemy

# Migration DB
$ flask db upgrade

# Run Server (http://localhst:5000)
python app.py
```
