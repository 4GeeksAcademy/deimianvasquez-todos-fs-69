from flask import Blueprint, jsonify, request
from api.models import db, Todo
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity

todos_bp = Blueprint('todos', __name__)
CORS(todos_bp)


@todos_bp.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    current_user_id = get_jwt_identity()
    todos = Todo.query.filter_by(user_id=current_user_id).all()
    return jsonify([todo.serialize() for todo in todos]), 200


@todos_bp.route('/todos', methods=['POST'])
@jwt_required()
def create_todo():
    data = request.get_json(silent=True) or {}
    label = (data.get('label') or '').strip()

    if not label:
        return jsonify({"error": "Missing required field: label"}), 400

    current_user_id = get_jwt_identity()

    try:
        new_todo = Todo(label=label, user_id=current_user_id)
        db.session.add(new_todo)
        db.session.commit()
        return jsonify(new_todo.serialize()), 201
    except Exception as error:
        print(error.args)
        db.session.rollback()
        return jsonify({"error": "Failed to create todo"}), 500


@todos_bp.route('/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    data = request.get_json(silent=True) or {}
    label = (data.get('label') or '').strip()
    is_done = data.get('is_done')

    if label == '' and is_done is None:
        return jsonify({"error": "At least one field (label or is_done) must be provided"}), 400

    current_user_id = get_jwt_identity()
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user_id).first()

    if not todo:
        return jsonify({"error": "Todo not found"}), 404

    try:
        if label != '':
            todo.label = label
        if is_done is not None:
            todo.is_done = bool(is_done)

        db.session.commit()
        return jsonify(todo.serialize()), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to update todo"}), 500


@todos_bp.route('/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    current_user_id = get_jwt_identity()
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user_id).first()

    if not todo:
        return jsonify({"error": "Todo not found"}), 404

    try:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({"message": "Todo deleted successfully"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to delete todo"}), 500
