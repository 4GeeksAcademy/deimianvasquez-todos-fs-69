"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from sqlalchemy.exc import IntegrityError
from api.models import db, User
from api.utils import generate_sitemap, APIException, valid_email, send_email
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64encode
import os
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta


api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route("/health-check", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


@api.route("/users", methods=["POST"])
def create_user():
    data_form = request.form
    data_files = request.files
    data = {**data_form, **data_files}

    for field in ["email", "full_name", "password"]:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"})

    email = data["email"].strip().lower()
    full_name = data["full_name"].strip()
    password = data["password"]
    avatar_file = data.get("avatar_url")

    if not valid_email(email):
        return jsonify({"error": "Ivalid email format"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    avatar = "https://i.pravatar.cc/300"

    salt = b64encode(os.urandom(32)).decode('utf-8')
    password = generate_password_hash(password+salt)
    try:

        new_user = User(
            email=email,
            full_name=full_name,
            password=password,
            salt=salt,
            is_active=True,
            avatar_url=avatar
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify(new_user.serialize()), 201
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409
    except Exception as error:
        return jsonify({"error": f"Unexpected error: {error}"})


@api.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    for field in ["email", "password"]:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400

    user = User.query.filter_by(email=email).one_or_none()

    if not user:
        return jsonify({"error": "Ivalid email or password"}), 401

    if not check_password_hash(user.password, password+user.salt):
        return jsonify({"error": "Ivalid email or password"}), 401

    return jsonify({
        "user": user.serialize(),
        "access_token": create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
    }), 200


@api.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    try:
        user_id = get_jwt_identity()

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.serialize()), 200
    except Exception as error:
        return jsonify({"error": f"Error: {error.args}"})


@api.route("/example-email", methods=["GET"])
def send_email_example():
    try:
        success = send_email(
            subject="Test email todos",
            recipient="dvasquez@4geeksacademy.com",
            body="<strong> Esta es una prueba de email</strong>"
        )
        if success:
            return jsonify({"message": "Email sending success"}), 200
        else:
            return jsonify({"error": "Error sended message"})
    except Exception as error:
        return jsonify({"error": f"Error sending email: {error.args}"})


"""
    1.- Enviar correos --> listo
    2.- Resetaer contraseña
    3.- Actualizar la contraseña
    4.- Integrar endpoints del todolist
    5.- Integrar coud images
    6.- Todo el frontend
    7.- Desplegar en render
    8.- Usar supabase como base de datos
    9.- Activar usuario (Confirmación) 

"""
