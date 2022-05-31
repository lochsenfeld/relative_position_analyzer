from dataclasses import dataclass


@dataclass
class CalibrationEntity:
    timestamp: str
    position1_original: float = None
    position2_original: float = None
    position1_calculated: float = None
    position2_calculated: float = None
