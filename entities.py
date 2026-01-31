"""
File with entity definitions.
"""

from dataclasses import dataclass
import datetime
from typing import List, Optional

@dataclass
class Trip:
	info: str
	number: str
	platforms: List[str]
	line: str
	serviceType: str
	is_express: bool
	departure_time: datetime.datetime
	coach_count: int
	scheduled_coach_count: int
	stops: List[str]




