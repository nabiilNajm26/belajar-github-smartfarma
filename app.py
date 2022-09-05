from flask import Flask, request, jsonify
from flask.helpers import make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from analyzer import *

import datetime
import time
import bcrypt
import jwt

from os import environ

# Init app
app = Flask(__name__)

# Database
DB_HOST = str(environ.get("DB_HOST", "localhost"))
DB_NAME = str(environ.get("DB_NAME", "smartfarma_db"))
DB_PORT = str(environ.get("DB_PORT", "3306"))
DB_USER = str(environ.get("DB_USER", "smartfarma"))
DB_PASSWORD = str(environ.get("DB_PASSWORD", "$m4rtF4rm4"))
JWT_SECRET_KEY = str(environ.get("JWT_SECRET_KEY", "smartfarma-8JKba4guibasd78213n"))

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://" + \
    DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST + ":" + DB_PORT + "/" + DB_NAME + "?collation=utf8mb4_general_ci"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init db
db = SQLAlchemy(app)

# Init ma
ma = Marshmallow(app)

# DB Migrate
migrate = Migrate(app, db)

# Users Class Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stra_number = db.Column(db.String(50))
    sipa_number = db.Column(db.String(50))
    name = db.Column(db.String(100))
    pharmacy_name = db.Column(db.String(50))
    pharmacy_address = db.Column(db.TEXT)
    email = db.Column(db.String(200))
    password = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __init__(self, stra_number, sipa_number, name, pharmacy_name, pharmacy_address, email, password):
        self.stra_number = stra_number
        self.sipa_number = sipa_number
        self.name = name
        self.pharmacy_name = pharmacy_name
        self.pharmacy_address = pharmacy_address
        self.email = email
        self.password = password


# Users Schema
class UsersSchema(ma.Schema):
    class Meta:
        fields = ('id', 'stra_number', 'sipa_number', 'name', 'pharmacy_name', 'pharmacy_address', 'email', 'password',
                  'created_at', 'updated_at')

# UserSessions Class Model
class UserSessions(db.Model):
    id = db.Column(db.TEXT(255), primary_key=True, default=time.time)
    user_id = db.Column(db.Integer())
    info = db.Column(db.TEXT())
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __init__(self, user_id):
        self.user_id = user_id

# UserSessions Schema
class UserSessionsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_id',
                  'created_at', 'updated_at')

# UserMessages Class Model
class UserMessages(db.Model):
    id = db.Column(db.String(255), primary_key=True, default=time.time)
    user_id = db.Column(db.Integer())
    user_session_id = db.Column(db.String(255))
    message = db.Column(db.String(255))
    bot_response = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __init__(self, user_id, user_session_id, message, bot_response):
        self.user_id = user_id
        self.user_session_id = user_session_id
        self.message = message
        self.bot_response = bot_response

# UserMessages Schema
class UserMessagesSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_id', 'user_session_id', 'message', 'bot_response',
                  'created_at', 'updated_at')


# Init schema
user_schema = UsersSchema()
users_schema = UsersSchema(many=True)

user_session_schema = UserSessionsSchema()
user_sessions_schema = UserSessionsSchema(many=True)

user_message_schema = UserMessagesSchema()
user_messages_schema = UserMessagesSchema(many=True)

# Register user

@app.route("/register", methods=["POST"])
def create_user():
    stra_number = request.json.get("stra_number", None) 
    sipa_number = request.json.get("sipa_number", None)
    pharmacy_name = request.json.get("pharmacy_name", None)
    pharmacy_address = request.json.get("pharmacy_address", None)
    name = request.json.get("name", None)
    email = request.json.get("email", None)
    password = request.json.get("password", None).encode("utf-8 ")

    # Payload validation
    if not stra_number:
        return make_response(
            jsonify({
                "err": "stra_number field cannot be empty",
            }), 400)

    if not sipa_number:
        return make_response(
            jsonify({
                "err": "sipa_number field cannot be empty",
            }), 400)

    if not name:
        return make_response(
            jsonify({
                "err": "name field cannot be empty",
            }), 400)

    if not pharmacy_name:
        return make_response(
            jsonify({
                "err": "pharmacy_name field cannot be empty",
            }), 400)

    if not pharmacy_address:
        return make_response(
            jsonify({
                "err": "pharmacy_address field cannot be empty",
            }), 400)

    if not email:
        return make_response(
            jsonify({
                "err": "email field cannot be empty",
            }), 400)

    if not password:
        return make_response(
            jsonify({
                "err": "password field cannot be empty",
            }), 400)

    getUser = Users.query.filter_by(email=email).first()

    if getUser:
        return make_response(
            jsonify({
                "err": "email address already registered",
            }), 500
        )

    # Store validated user payload to database
    hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt())
    registered_user = Users(stra_number, sipa_number, name, pharmacy_name, pharmacy_address, email, hashedPassword)
    db.session.add(registered_user)


    

    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        return make_response(
            jsonify({
                "err": "email address already registered",
            }), 500
        )

    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        return make_response(
            jsonify({
                "err": "failed to create new session",
            }), 500
        )

    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': registered_user.email,
        }

        jwt_token = jwt.encode(
            payload,
            JWT_SECRET_KEY,
            algorithm='HS256',
        )

        if isinstance(jwt_token, bytes):
            jwt_token = jwt_token.decode()

    except Exception as e:
        return make_response(jsonify({
            "message": e.args[0]
        }), 500)

    return make_response(
        jsonify({
            "err": None,
            "token": jwt_token,
        })
    )

# Update user
@app.route("/users", methods=["PUT"])
def update_user():
    stra_number = request.json.get("stra_number", None)
    sipa_number = request.json.get("sipa_number", None)
    pharmacy_name = request.json.get("pharmacy_name", None)
    pharmacy_address = request.json.get("pharmacy_address", None)
    name = request.json.get("name", None)
    password = request.json.get("password", None)

    try:
        decoded_token = jwt.decode(
            request.headers.get('Authorization'),
            JWT_SECRET_KEY,
            algorithms='HS256'
        )        
    except Exception as e:
        return make_response(jsonify({
            "err": "invalid token"
        }), 401)

    userToUpdate = Users.query.filter_by(email=decoded_token["sub"]).first()

    if userToUpdate:
        if stra_number:
            userToUpdate.stra_number = stra_number

        if sipa_number:
            userToUpdate.sipa_number = sipa_number

        if pharmacy_name:
            userToUpdate.pharmacy_name = pharmacy_name

        if pharmacy_address:
            userToUpdate.pharmacy_address = pharmacy_address

        if name:
            userToUpdate.name = name

        if password:
            password = password.encode("utf-8 ")
            hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt())
            userToUpdate.password = hashedPassword

        try:
            db.session.commit()

            return make_response(
                jsonify({
                    "err": None,
                }), 200
            )
        except exc.SQLAlchemyError:
            return make_response(
                jsonify({
                    "err": "internal server error",
                }), 500
            )

    return make_response(
        jsonify({
            "err": "user doesn't exist",
        }), 404
    )

# Login user
# Flask : mengubah fungsi menjadi URL
# POST : ada yang akan kita kirim, data 
# GET : hanya akan mengambil data saja
@app.route("/login", methods=["POST"])
def login_user():
    email = request.json.get("email", None).encode("utf-8 ")
    password = request.json.get("password", None).encode("utf-8 ")

    # Payload validation
    if not email:
        return make_response(
            jsonify({
                "err": "email field cannot be empty",
            }), 400)

    if not password:
        return make_response(
            jsonify({
                "err": "password field cannot be empty",
            }), 400)

    getUser = Users.query.filter_by(email=email).first()

    if not getUser:
        return make_response(
            jsonify({
                "err": "email doesn't exist",
            }), 400)

    if bcrypt.checkpw(password, getUser.password.encode("utf-8 ")):
        try:
            db.session.commit()
        except exc.SQLAlchemyError:
            return make_response(
                jsonify({
                    "err": "failed to create new session",
                }), 500
            )

        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'sub': getUser.email,
            }

            jwt_token = jwt.encode(
                payload,
                JWT_SECRET_KEY,
                algorithm='HS256'
            )

            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode()

        except Exception as e:
            return make_response(jsonify({
                "err": e.args[0]
            }), 500)

        return make_response(
            jsonify({
                "err": None,
                "token": jwt_token
            }), 200
        )
    else:
        return make_response(
            jsonify({
                "err": "password doesn't match"
            }), 400
        )


# Get current user
@app.route("/me", methods=["GET"])
def get_current_user():
    try:
        decoded_token = jwt.decode(
            request.headers.get('Authorization'),
            JWT_SECRET_KEY,
            algorithms='HS256'
        )
    except Exception as e:
        return make_response(jsonify({
            "err": "invalid token"
        }), 401)

    getUser = Users.query.filter_by(email=decoded_token["sub"]).first()

    return make_response(
        jsonify({
            "err": None,
            "user": {
                "id": getUser.id,
                "stra_number": getUser.stra_number,
                "sipa_number": getUser.sipa_number,
                "name": getUser.name,
                "pharmacy_name": getUser.pharmacy_name,
                "pharmacy_address": getUser.pharmacy_address,
                "email": getUser.email,
                "created_at": getUser.created_at,
                "updated_at": getUser.updated_at
            }
        }), 200
    )

# Join to session
@app.route("/user-sessions/start", methods=["GET"])
def create_session():
    try:
        decoded_token = jwt.decode(
            request.headers.get('Authorization'),
            JWT_SECRET_KEY,
            algorithms='HS256'
        )
    except Exception as e:
        return make_response(jsonify({
            "err": "invalid token"
        }), 401)

    getUser = Users.query.filter_by(email=decoded_token["sub"]).first()

    # Create new user session
    created_session = UserSessions(getUser.id)
    created_session.created_at = datetime.datetime.utcnow()
    created_session.updated_at = datetime.datetime.utcnow()
    
    db.session.add(created_session)

    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        return make_response(
            jsonify({
                "err": "internal server error",
            }), 500
        )

    return make_response(
        jsonify({
            "err": None,
            "session_id": created_session.id,
        })
    )

# End session
@app.route("/user-sessions/end", methods=["PUT"])
def end_session():
    try:
        jwt.decode(
            request.headers.get('Authorization'),
            JWT_SECRET_KEY,
            algorithms='HS256'
        )
    except Exception as e:
        return make_response(jsonify({
            "err": "invalid token"
        }), 401)

    user_session_id = request.json.get("session_id", None)

    sessionToUpdate = UserSessions.query.filter_by(id=user_session_id).first()

    # Update user session status
    sessionToUpdate.updated_at = datetime.datetime.utcnow()

    try:
        db.session.commit()
    except exc.SQLAlchemyError:
        return make_response(
            jsonify({
                "err": "internal server error",
            }), 500
        )

    return make_response(
        jsonify({
            "err": None,
        })
    )

# Send messages
@app.route("/messages", methods=["POST"])
def create_message():
    try:
        decoded_token = jwt.decode(
            request.headers.get('Authorization'),
            JWT_SECRET_KEY,
            algorithms='HS256'
        )
    except Exception as e:
        return make_response(jsonify({
            "err": "invalid token"
        }), 401)

    getUser = Users.query.filter_by(email=decoded_token["sub"]).first()

    user_id = getUser.id
    user_session_id = request.json.get("session_id", None)
    message = request.json.get("message", None)

    note = UserSessions.query.filter_by(id=user_session_id).first().info

    # Payload validation
    if not message:
        return make_response(
            jsonify({
                "err": "message cannot be empty",
            }), 400)

    # Bot Analyzer function goes here
    print(f"note app.py = {note}")
    bot_response, new_note = main_checker(message, user_session_id, note)
    
    # Update UserSessions info with new_note
    sessionToUpdate = UserSessions.query.filter_by(id=user_session_id).first()
    sessionToUpdate.info = new_note
    sessionToUpdate.updated_at = datetime.datetime.utcnow()

    # Store validated payload to database
    created_message = UserMessages(
        user_id, user_session_id, message, bot_response)

    db.session.add(created_message)

    try:
        db.session.commit()
    except exc.SQLAlchemyError as e:
        return make_response(
            jsonify({
                "err": e.args[0],
            }), 500
        )

    return make_response(
        jsonify({
            "err": None,
            "bot_response": bot_response,
        })
    )

# Get messages
@app.route("/messages", methods=["GET"])
def get_messages():
    try:
        decoded_token = jwt.decode(
            request.headers.get('Authorization'),
            JWT_SECRET_KEY,
            algorithms='HS256'
        )
    except Exception as e:
        return make_response(jsonify({
            "err": "invalid token"
        }), 401)

    getUser = Users.query.filter_by(email=decoded_token["sub"]).first()

    getSessions = UserSessions.query.filter_by(
        user_id=getUser.id).order_by(UserSessions.created_at).all()
    sessions_dict = user_messages_schema.dump(getSessions)

    for session in sessions_dict:
        getMessages = UserMessages.query.filter_by(
            user_session_id=session["id"]).order_by(UserMessages.created_at).all()
        messages_dict = user_messages_schema.dump(getMessages)
        session["messages"] = messages_dict

    return make_response(
        jsonify({
            "err": None,
            "data": sessions_dict,
        })
    )


# Run Server
if __name__ == '__main__':
    app.run(debug=True)
