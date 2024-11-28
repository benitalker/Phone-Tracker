from flask import Blueprint, jsonify, request
from app.repository.phone_repository import create_device_and_interaction, find_bluetooth_connections, \
    find_strong_signal_connections, count_device_connections

phone_blueprint = Blueprint("phone", __name__)

@phone_blueprint.route("/phone_tracker", methods=['POST'])
def get_interaction():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Expected a list of interactions"}), 400
        result = create_device_and_interaction(data)
        return jsonify(result), 201
    except Exception as e:
        print(f"Error processing interaction: {str(e)}")
        return jsonify({"error": "Failed to process interaction"}), 400

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
    print(device_id)
    count = count_device_connections(device_id)
    return jsonify({"device_id": device_id, "connection_count": count}), 200

# @phone_blueprint.route("/api/connection/direct", methods=['GET'])
# def check_connection():
#     device1_id = request.args.get('device1')
#     device2_id = request.args.get('device2')
#
#     if not device1_id or not device2_id:
#         return jsonify({"error": "Both device IDs are required"}), 400
#
#     is_connected = check_direct_connection(device1_id, device2_id)
#     return jsonify({
#         "device1": device1_id,
#         "device2": device2_id,
#         "is_connected": is_connected
#     }), 200
#
#
# @phone_blueprint.route("/api/device/<device_id>/last-interaction", methods=['GET'])
# def get_last_interaction(device_id):
#     interaction = get_most_recent_interaction(device_id)
#     if interaction:
#         return jsonify(interaction), 200
#     return jsonify({"error": "No recent interactions found"}), 404