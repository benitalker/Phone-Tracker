import uuid
from returns.maybe import Maybe
from app.db.database import driver
from app.db.models import Device, Interaction

def create_device_and_interaction(data: dict):
    with driver.session() as session:
        devices = data.get('devices', [])
        interaction = data.get('interaction', {})

        query = """
        UNWIND $devices AS device
        MERGE (d:Device {id: device.id})
        ON CREATE SET 
            d.uuid = device.uuid,
            d.brand = device.brand,
            d.model = device.model,
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

        devices_with_uuid = [
            {**device, 'uuid': str(uuid.uuid4())} for device in devices
        ]

        params = {
            "devices": devices_with_uuid,
            "from_device": interaction.get('from_device'),
            "to_device": interaction.get('to_device'),
            "method": interaction.get('method'),
            "bluetooth_version": interaction.get('bluetooth_version'),
            "signal_strength_dbm": interaction.get('signal_strength_dbm'),
            "distance_meters": interaction.get('distance_meters'),
            "duration_seconds": interaction.get('duration_seconds'),
            "timestamp": interaction.get('timestamp')
        }

        session.run(query, params)
        return {"status": "Interaction recorded"}

def get_all_devices() -> list[Device]:
    with driver.session() as session:
        query = "MATCH (d:Device) RETURN d"
        res = session.run(query).data()

        devices = []
        for device_data in res:
            device_dict = dict(device_data['d'])
            location = Location(
                latitude=device_dict.get('latitude', 0),
                longitude=device_dict.get('longitude', 0),
                altitude_meters=device_dict.get('altitude', 0),
                accuracy_meters=device_dict.get('accuracy', 0)
            )
            device = Device(
                uuid=device_dict.get('uuid', ''),
                id=device_dict.get('id', ''),
                brand=device_dict.get('brand', ''),
                model=device_dict.get('model', ''),
                os=device_dict.get('os', ''),
                location=location
            )
            devices.append(device)

        return devices

def get_device_by_id(device_id: str):
    with driver.session() as session:
        query = """
        MATCH (d:Device {uuid: $uuid})
        RETURN d
        """
        params = {"uuid": device_id}
        res = session.run(query, params).single()

        if not res:
            return None

        device_dict = dict(res.get("d"))
        location = Location(
            latitude=device_dict.get('latitude', 0),
            longitude=device_dict.get('longitude', 0),
            altitude_meters=device_dict.get('altitude', 0),
            accuracy_meters=device_dict.get('accuracy', 0)
        )

        return Device(
            uuid=device_dict.get('uuid', ''),
            id=device_dict.get('id', ''),
            brand=device_dict.get('brand', ''),
            model=device_dict.get('model', ''),
            os=device_dict.get('os', ''),
            location=location
        )

def delete_device(device_id: str):
    with driver.session() as session:
        query = """
        MATCH (d:Device {uuid: $uuid})
        DELETE d
        RETURN d
        """
        params = {"uuid": device_id}
        res = session.run(query, params).single()
        return Maybe.from_optional(res).map(lambda _: f"Device {device_id} deleted successfully")

def update_device(device_id: str, new_data: dict):
    with driver.session() as session:
        query = """
        MATCH (d:Device {uuid: $uuid})
        SET d += $new_data
        RETURN d
        """
        params = {
            "uuid": device_id,
            "new_data": new_data
        }
        res = session.run(query, params).single()
        return (Maybe.from_optional(res.get("d"))
                .map(lambda u: dict(u)))

def find_bluetooth_connections():
    with driver.session() as session:
        query = """
        MATCH path = (d1:Device)-[r:CONNECTED {method: 'Bluetooth'}]->(d2:Device)
        RETURN 
            d1.id AS from_device, 
            d2.id AS to_device, 
            length(path) AS path_length
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