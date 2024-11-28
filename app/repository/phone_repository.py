from typing import List, Dict
from toolz import curry, pipe
from app.db.database import driver
from app.db.models import Device, Interaction

# def create_device_and_interaction(data: dict):
#     with driver.session() as session:
#         devices = data.get('devices', [])
#         interaction = data.get('interaction', {})
#
#         query = """
#         UNWIND $devices AS device
#         MERGE (d:Device {id: device.id})
#         ON CREATE SET
#             d.brand = device.brand,
#             d.model = device.model,
#             d.name = device.name,
#             d.os = device.os,
#             d.latitude = device.location.latitude,
#             d.longitude = device.location.longitude,
#             d.altitude = device.location.altitude_meters,
#             d.accuracy = device.location.accuracy_meters
#
#         WITH device, d
#         MATCH (from:Device {id: $from_device}), (to:Device {id: $to_device})
#         MERGE (from)-[r:CONNECTED {
#             method: $method,
#             bluetooth_version: $bluetooth_version,
#             signal_strength_dbm: $signal_strength_dbm,
#             distance_meters: $distance_meters,
#             duration_seconds: $duration_seconds,
#             timestamp: $timestamp
#         }]->(to)
#         RETURN d
#         """
#
#         params = {
#             "devices": devices,
#             "from_device": interaction.get('from_device'),
#             "to_device": interaction.get('to_device'),
#             "method": interaction.get('method'),
#             "bluetooth_version": interaction.get('bluetooth_version'),
#             "signal_strength_dbm": interaction.get('signal_strength_dbm'),
#             "distance_meters": interaction.get('distance_meters'),
#             "duration_seconds": interaction.get('duration_seconds'),
#             "timestamp": interaction.get('timestamp')
#         }
#
#         session.run(query, params)
#         return {"status": "Interaction recorded"}

@curry
def create_cypher_params(devices: List[Device], interaction: Interaction) -> Dict:
    return {
        "devices": [
            {
                "id": device.id,
                "brand": device.brand,
                "model": device.model,
                "name": device.name,
                "os": device.os,
                "location": {
                    "latitude": device.location.latitude,
                    "longitude": device.location.longitude,
                    "altitude_meters": device.location.altitude_meters,
                    "accuracy_meters": device.location.accuracy_meters
                }
            } for device in devices
        ],
        "from_device": interaction.from_device,
        "to_device": interaction.to_device,
        "method": interaction.method,
        "bluetooth_version": interaction.bluetooth_version,
        "signal_strength_dbm": interaction.signal_strength_dbm,
        "distance_meters": interaction.distance_meters,
        "duration_seconds": interaction.duration_seconds,
        "timestamp": interaction.timestamp
    }

def execute_device_interaction_query(params: Dict) -> Dict:
    query = """
    UNWIND $devices AS device
    MERGE (d:Device {id: device.id})
    ON CREATE SET 
        d.brand = device.brand,
        d.model = device.model,
        d.name = device.name,
        d.os = device.os,
        d.latitude = device.location.latitude,
        d.longitude = device.location.longitude,
        d.altitude = device.location.altitude_meters,
        d.accuracy = device.location.accuracy_meters

    WITH device, d
    MATCH (from:Device {id: $from_device}), (to:Device {id: $to_device})
    MERGE (from)-[r:CONNECTED {
        method: $method,
        bluetooth_version: $bluetooth_version,
        signal_strength_dbm: $signal_strength_dbm,
        distance_meters: $distance_meters,
        duration_seconds: $duration_seconds,
        timestamp: $timestamp
    }]->(to)
    RETURN d
    """

    with driver.session() as session:
        session.run(query, params)
        return {"status": "Interaction recorded"}

def create_device_interaction(devices: List[Device], interaction: Interaction) -> Dict:
    return pipe(
        interaction,
        create_cypher_params(devices),
        execute_device_interaction_query
    )

def find_bluetooth_connections():
    with driver.session() as session:
        query = """
        MATCH path = (d1:Device)-[r:CONNECTED*]->(d2:Device)
        WHERE all(rel IN r WHERE rel.method = 'Bluetooth')
        RETURN 
            d1.id AS from_device, 
            d2.id AS to_device, 
            length(path) AS path_length
        ORDER BY length(path) DESC
        LIMIT 1
        """
        result = session.run(query)
        return [
            {
                "from_device": record["from_device"],
                "to_device": record["to_device"],
                "path_length": record["path_length"]
            } for record in result
        ]

def find_strong_signal_connections():
    with driver.session() as session:
        query = """
        MATCH path = (d1:Device)-[r:CONNECTED]->(d2:Device)
        WHERE r.signal_strength_dbm > -60
        RETURN
            d1.id AS from_device,
            d2.id AS to_device,
            r.signal_strength_dbm AS signal_strength
        """
        result = session.run(query)
        return [
            {
                "from_device": record["from_device"],
                "to_device": record["to_device"],
                "signal_strength": record["signal_strength"]
            } for record in result
        ]

def count_device_connections(device_id):
    with driver.session() as session:
        query = """
        MATCH (d:Device {id: $device_id})-[r:CONNECTED]->()
        RETURN count(r) AS connection_count
        """
        result = session.run(query, {"device_id": device_id}).single()
        return result["connection_count"] if result else 0

def check_direct_connection(device1_id, device2_id):
    with driver.session() as session:
        query = """
        MATCH (d1:Device {id: $device1_id})-[r:CONNECTED]->(d2:Device {id: $device2_id})
        RETURN count(r) > 0 AS is_connected
        """
        result = session.run(query, {
            "device1_id": device1_id,
            "device2_id": device2_id
        }).single()
        return result["is_connected"] if result else False

def get_most_recent_interaction(device_id):
    with driver.session() as session:
        query = """
        MATCH (d1:Device {id: $device_id})-[r:CONNECTED]->(d2:Device)
        RETURN
            d2.id AS connected_device,
            r.method AS method,
            r.bluetooth_version AS bluetooth_version,
            r.signal_strength_dbm AS signal_strength,
            r.distance_meters AS distance,
            r.duration_seconds AS duration,
            r.timestamp AS timestamp
        ORDER BY r.timestamp DESC
        LIMIT 1
        """
        result = session.run(query, {"device_id": device_id}).single()
        return dict(result) if result else None