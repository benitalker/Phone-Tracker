from dataclasses import dataclass
import uuid
from typing import Optional
from app.db.models import Location

@dataclass
class Device:
    uuid: str = str(uuid.uuid4())
    id: str = ''
    brand: str = ''
    model: str = ''
    os: str = ''
    location: Optional[Location] = None