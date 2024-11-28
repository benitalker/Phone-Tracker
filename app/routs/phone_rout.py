from flask import Blueprint, jsonify, request
from app.repository.phone_repository import create_device_and_interaction

phone_blueprint = Blueprint("phone", __name__)

@phone_blueprint.route("/api/phone_tracker", methods=['POST'])
def get_interaction():
    try:
        data = request.json
        print(data)
        if not isinstance(data, list):
            return jsonify({"error": "Expected a list of interactions"}), 400

        results = []
        for interaction_data in data:
            result = create_device_and_interaction(interaction_data)
            results.append(result)

        return jsonify(results), 201
    except Exception as e:
        print(f"Error processing interaction: {str(e)}")
        return jsonify({"error": "Failed to process interaction"}), 400
