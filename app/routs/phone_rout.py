from flask import Blueprint, jsonify, request

phone_blueprint = Blueprint("phone", __name__)

@phone_blueprint.route("/api/phone_tracker", methods=['POST'])
def get_interaction():
   print(request.json)
   return jsonify({ }), 200
