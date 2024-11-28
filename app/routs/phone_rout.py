from flask import Blueprint, jsonify, request
from app.service.device_service import process_device_interaction
from app.repository.phone_repository import (
    find_bluetooth_connections,
    find_strong_signal_connections,
    count_device_connections,
    check_direct_connection,
    get_most_recent_interaction
)

phone_blueprint = Blueprint("phone", __name__)

@phone_blueprint.route("/phone_tracker", methods=['POST'])
def create_interaction():
    data = request.json
    if not data:
        return jsonify({"error": "Expected a list of interactions"}), 400
    try:
        result = process_device_interaction(data)
        return jsonify(result), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Failed to process interaction"}), 500

@phone_blueprint.route("/bluetooth", methods=['GET'])
def get_bluetooth_connections():
    connections = find_bluetooth_connections()
    return jsonify(connections), 200

@phone_blueprint.route("/strong-signal", methods=['GET'])
def get_strong_signal_connections():
    connections = find_strong_signal_connections()
    return jsonify(connections), 200

@phone_blueprint.route("/connection-count/<device_id>", methods=['GET'])
def get_device_connection_count(device_id):
    try:
        count = count_device_connections(device_id)
        return jsonify({"device_id": device_id, "connection_count": count}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch connection count: {str(e)}"}), 500

@phone_blueprint.route("/direct-connection", methods=['GET'])
def check_connection():
    data = request.json
    if not data or "device1" not in data or "device2" not in data:
        return jsonify({"error": "Both device IDs are required"}), 400
    try:
        is_connected = check_direct_connection(data["device1"], data["device2"])
        return jsonify({
            "device1": data["device1"],
            "device2": data["device2"],
            "is_connected": is_connected
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to check connection: {str(e)}"}), 500

@phone_blueprint.route("/last-interaction/<device_id>", methods=['GET'])
def get_last_interaction(device_id):
    try:
        interaction = get_most_recent_interaction(device_id)
        if interaction:
            return jsonify(interaction), 200
        return jsonify({"error": "No recent interactions found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to fetch last interaction: {str(e)}"}), 500
