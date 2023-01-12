from flask import Flask, request, jsonify, Response
from configuration import Configuration
from models import database, User, UserRole
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
import re

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/register", methods=["POST"])
def register():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    isCustomer = request.json.get("isCustomer", "")

    if len(forename) == 0:
        return jsonify(message="Field forename is missing."), 400
    if len(surname) == 0:
        return jsonify(message="Field surname is missing."), 400
    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400
    if len(password) == 0:
        return jsonify(message="Field password is missing."), 400
    if isinstance(isCustomer, str) and len(isCustomer) == 0:
        return jsonify(message="Field isCustomer is missing."), 400

    emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(emailRegex, email) or len(email) > 256:
        return jsonify(message="Invalid email."), 400

    if not re.fullmatch(r'^(?=.{8,256}$)(?=[^A-Z]*[A-Z])(?=\D*\d)(?=(?:[^a-z]*[a-z]))[a-zA-Z0-9#*.!?$,]+$', password):
        return jsonify(message="Invalid password."), 400

    user = User.query.filter(User.email == email).first()
    if user:
        return jsonify(message="Email already exists."), 400

    user = User(email=email, password=password, forename=forename, surname=surname)
    database.session.add(user)
    database.session.commit()

    roleId = -1
    if isCustomer:
        roleId = 2
    else:
        roleId = 3

    userRole = UserRole(userId=user.id, roleId=roleId)
    database.session.add(userRole)
    database.session.commit()

    return Response(status=200)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400
    if len(password) == 0:
        return jsonify(message="Field password is missing."), 400

    emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(emailRegex, email) or len(email) > 256:
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not user:
        return jsonify(message="Invalid credentials."), 400

    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": [str(role.name) for role in user.roles]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims)

    return jsonify(accessToken=accessToken, refreshToken=refreshToken)


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roles": refreshClaims["roles"]
    }

    accessToken = create_access_token(identity=identity, additional_claims=additionalClaims)

    return jsonify(accessToken=accessToken), 200


@application.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    email = request.json.get("email", "")

    identity = get_jwt_identity()
    if identity != "admin@admin.com":
        return jsonify(msg="Missing Authorization Header"), 401

    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400

    emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(emailRegex, email) or len(email) > 256:
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(User.email == email).first()
    if not user:
        return jsonify(message="Unknown user."), 400

    database.session.delete(user)
    database.session.commit()

    return Response(status=200)


@application.route("/", methods=["GET"])
def index():
    return "Authentication"


if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5000)
