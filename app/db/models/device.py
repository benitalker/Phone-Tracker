from dataclasses import dataclass
from typing import Optional
from .location import Location

@dataclass
class Device:
    location: Location
    id: str
    brand: str
    model: str
    os: str
    name: str