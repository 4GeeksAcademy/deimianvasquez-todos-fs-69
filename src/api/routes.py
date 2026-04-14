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
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt, decode_token
from datetime import timedelta
import cloudinary.uploader as uploader


api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)

ALLOWED_IMAGES_TYPES = {"image/jpej", "image/png", "image/webp"}
MAX_IMAGEN_SIZE_BYTES = 2*1024*2024


def _resolve_avatar_url(avatar_file):
    if not avatar_file:
        return "https://i.pravatar.cc/300"

    if avatar_file.mimetype not in ALLOWED_IMAGES_TYPES:
        raise ValueError("Avatar must be JPG, PNG, WEBP")

    avatar_file.stream.seek(0, 2)
    file_size = avatar_file.stream.tell()
    avatar_file.stream.seek(0)

    if file_size > MAX_IMAGEN_SIZE_BYTES:
        raise ValueError("Avatar max size is 2MB")

    return "https://i.pravatar.cc/300"


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
    avatar_url = _resolve_avatar_url(avatar_file)

    if avatar_file:
        try:
            uploade_result = uploader.upload(avatar_file)
            avatar = uploade_result.get("secure_url", avatar_url)
        except Exception as error:
            return jsonify({"error": "Error updating image"}), 500

    if not valid_email(email):
        return jsonify({"error": "Ivalid email format"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    salt = b64encode(os.urandom(32)).decode('utf-8')
    password = generate_password_hash(password+salt)
    try:

        new_user = User(
            email=email,
            full_name=full_name,
            password=password,
            salt=salt,
            is_active=False,
            avatar_url=avatar
        )

        db.session.add(new_user)
        db.session.flush()

        frontend_url = (os.getenv("URL_FRONTEND") or "").strip()
        if not frontend_url:
            db.session.rollback()
            return jsonify({"error": "El URL_FRONTEND is required"}), 500

        activaton_token = create_access_token(
            identity=str(new_user.id),
            additional_claims={"purpose": "account_activation"},
            expires_delta=timedelta(hours=1)
        )

        activation_link = f"{frontend_url}/activation-account?token={activaton_token}"
        email_body = f"""
        <div>
            <p>Hola {new_user.full_name},</p>
            <p>Bienvenido! Por favor activa tu cuenta ingresando al siguiente enlace:</p>
            <a href=\"{activation_link}\">Activar cuenta</a>
            <p>If you did not create this account, you can ignore this email.</p>
        </div>
        """

        success = send_email(
            subject="Activación de usuario",
            recipient=new_user.email,
            body=email_body
        )

        if not success:
            db.session.rollback()
            return jsonify({"error": "Failed to send activation email"}), 500

        db.session.commit()
        return jsonify({
            "user": new_user.serialize(),
            "message": "User created. Check your email to activate the account"
        }), 201
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
    if not user.is_active:
        return jsonify({"error": "Your account no activate"}), 403

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


@api.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"error": "Missing required fiel email"}), 400

    user = User.query.filter_by(email=email).one_or_none()
    if not user:
        return jsonify({"message": "if email exists, a password reset link will be send"}), 200

    recovery_token = create_access_token(
        identity=str(user.id),
        additional_claims={"purpose": "password_reset"},
        expires_delta=timedelta(hours=1)
    )

    frontend_url = (os.getenv("URL_FRONTEND") or "").strip()

    if not frontend_url:
        return jsonify({"error": "URL_FRONTEND is required"}), 500

    body = f"""
        <div>
            <p>Hola {user.full_name},</p>
            <p>Solicitud para restaurar la contraseña. Da click en el siguiente enlace:</p>
            <a href="{frontend_url}/recovery-password?token={recovery_token}">Reset Password</a>
            <p>Si tu no solicitaste este enlace puedes ignorarlo.</p>
        </div>
    """

    try:
        success = send_email(
            subject="Solicitud de restaurar la contraseña",
            recipient=user.email,
            body=body
        )
        if success:
            return jsonify({"message": "Email sending success"}), 200
        else:
            return jsonify({"error": "Error sended message"})
    except Exception as error:
        return jsonify({"error": f"Error sending email: {error.args}"})


@api.route("/update-password", methods=["POST"])
@jwt_required()
def update_password():
    claims = get_jwt()
    if claims.get("purpose") != "password_reset":
        return jsonify({"error": "Invalid tokoken for password update"}), 403

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    new_password = data.get("new_password", "")

    if not new_password:
        return jsonify({"error": "Misssing required field: new_password"}), 400

    salt = b64encode(os.urandom(32)).decode("utf-8")
    user.password = generate_password_hash(new_password+salt)
    user.salt = salt

    try:
        db.session.commit()
        return jsonify({"message": "password updated successfully"}), 200
    except Exception as error:
        db.session.rollback()
        print(error.args)
        return jsonify({"error": "Error updating password"}), 500


@api.route("/activate-account", methods=["POST"])
def activate_account():
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or request.args.get("token") or "").strip()

    if not token:
        return jsonify({"error": "Missing required field. token"}), 400

    try:
        decoded = decode_token(token)

    except Exception as error:
        return jsonify({"error": "invalid token or expired token"})

    if decoded.get("purpose") != "account_activation":
        return jsonify({"error": "Ivalid token purpose"}), 403

    user_id = decoded.get("sub")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    if user.is_active:
        return jsonify({"message": "User already activated"}), 200

    user.is_active = True

    try:
        db.session.commit()
        return jsonify({"message": "User activated successfully"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": "Fallaste"}), 500


@api.route("/hello", methods=["GET"])
def hello():
    return jsonify("hola"), 200


"""
4.- Integrar endpoints del todolist
6.- Todo el frontend
7.- Desplegar en render
8.- Usar supabase como base de datos
"""
