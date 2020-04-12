from datetime import datetime


@dataclass
class Hotspot:
    id: int
    name: str
    description: str
    target: int
    previous_week: int
    current_week: int

