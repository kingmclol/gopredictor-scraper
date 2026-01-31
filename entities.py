"""
File with entity definitions.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Trip:
	info: str
	number: str
	platforms: List[str]
	line: str
	serviceType: str
	is_express: bool
	departure_time: datetime
	coach_count: int
	scheduled_coach_count: int
	stops: List[str]

	@classmethod
	def from_row(cls, row) -> Trip:
		def parse_list(val: List | str | None) -> List:
			if val is None:
				return []
			if isinstance(val, list):
				return val
			return eval(val)
		
		return cls(
				info=row["info"],
				number=row["number"],
				platforms=parse_list(row["platforms"]),
				line=row["line"],
				serviceType=row["service_type"],
				is_express=bool(row["is_express"]),
				departure_time=datetime.fromisoformat(row["departure_time"]),
				coach_count=row["coach_count"],
				scheduled_coach_count=row["scheduled_coach_count"],
				stops=parse_list(row["stops"]),
			)
	
	def to_dict(self) -> dict:
		return {
			"info": self.info,
			"number": self.number,
			"platforms": self.platforms,
			"line": self.line,
			"service_type": self.serviceType,
			"is_express": self.is_express,
			"departure_time": self.departure_time.isoformat(),
			"coach_count": self.coach_count,
			"scheduled_coach_count": self.scheduled_coach_count,
			"stops": self.stops,
		}