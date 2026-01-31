from entities import Trip
from abc import ABC, abstractmethod

class Database(ABC):
	@abstractmethod
	def create_trip(self, trip: Trip) -> int:
		raise NotImplementedError
	@abstractmethod
	def get_all_trips(self) -> list[Trip]:
		raise NotImplementedError
	@abstractmethod
	def trip_exists(self, trip: Trip) -> bool:
		raise NotImplementedError
	