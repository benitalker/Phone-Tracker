from typing import Dict
from toolz import curry
from app.db.models import Location, Device, Interaction
from app.repository.phone_repository import create_device_interaction, relationship_exists


@curry
def validate_device_data(device_data: Dict) -> bool:
    required_keys = ['id', 'brand', 'model', 'os', 'location', 'name']
    return all(key in device_data for key in required_keys)

def parse_location(location_data: Dict) -> Location:
    return Location(
        latitude=location_data['latitude'],
        longitude=location_data['longitude'],
        altitude_meters=location_data.get('altitude_meters', 0),
        accuracy_meters=location_data.get('accuracy_meters', 0)
    )

def parse_device(device_data: Dict) -> Device:
    return Device(
        id=device_data['id'],
        brand=device_data['brand'],
        model=device_data['model'],
        name=device_data['name'],
        os=device_data['os'],
        location=parse_location(device_data['location'])
    )

def parse_interaction(interaction_data: Dict) -> Interaction:
    return Interaction(
        from_device=interaction_data['from_device'],
        to_device=interaction_data['to_device'],
        method=interaction_data['method'],
        bluetooth_version=interaction_data.get('bluetooth_version', ''),
        signal_strength_dbm=interaction_data.get('signal_strength_dbm', 0),
        distance_meters=interaction_data.get('distance_meters', 0),
        duration_seconds=interaction_data.get('duration_seconds', 0),
        timestamp=interaction_data['timestamp']
    )


def process_device_interaction(data: Dict) -> Dict:
    if not isinstance(data, dict):
        raise ValueError("Invalid data format. Expected a dictionary.")

    devices = data.get('devices', [])
    interaction = data.get('interaction', {})

    if not all(map(validate_device_data, devices)):
        raise ValueError("Invalid device data detected.")

    parsed_devices = list(map(parse_device, devices))
    parsed_interaction = parse_interaction(interaction)

    if parsed_interaction.from_device == parsed_interaction.to_device:
        raise ValueError("A device cannot create a relationship with itself.")

    if relationship_exists(parsed_interaction):
        raise ValueError("A relationship with the same timestamp already exists.")

    return create_device_interaction(parsed_devices, parsed_interaction)