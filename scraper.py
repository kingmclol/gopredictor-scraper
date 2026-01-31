from pprint import pprint
import requests
from datetime import datetime, timedelta
import json
ENDPOINT = "https://www.gotracker.ca/gotracker/mobile/proxy/web/Messages/Departures/All"

from entities import Trip
from time import sleep
from database_sql import *

def fetch_data():
	res = requests.get(ENDPOINT)
	decoded_res = res.content.decode("utf-8-sig") 
	data = json.loads(decoded_res)
	# with open("response.json", "r", encoding="utf-8-sig") as f:
	# 	data = json.load(f)
	return data

def parse_data_trips(data_json) -> list[Trip]:
	if data_json["status"] != "Ok":
		return []
	
	trips = []
	for item in data_json["trips"]:
		trip = Trip(
			info=item["info"],
			number=item["number"],
			platforms=_parse_platforms(item["platform"]),
			line=item["service"],
			serviceType=item["serviceType"],
			is_express=item["isExpress"],
			departure_time=datetime.fromisoformat(item["time"]),
			coach_count=item["coachCount"],
			scheduled_coach_count=item["scheduledCoachCount"],
			stops=_parse_stops(item["stops"]),
		)
		trips.append(trip)
	return trips

def _parse_platforms(platforms_str) -> list[str]:
	"""
	Given a string for the train's platforms, return a list of the platforms that the train is using
	
	:param platforms_str: The platforms string from response JSON
	:return: the list of platforms
	:rtype: list[str]

	>>> _parse_platforms("5")
	['5']
	>>> _parse_platforms("7 & 8")
	['7', '8']
	>>> parse_platforms("-")
	[]
	"""
	platforms = []
	if platforms_str == "-":
		return platforms
	
	for platform in platforms_str.split("&"):
		platforms.append(platform.strip())
	return platforms

def _parse_stops(stops_list) -> list[str]:
	"""
	Given a list of stops from the response JSON, return a list of stop names
	
	:param stops_list: The list of stops from response JSON
	:return: The list of the stops, with "Express To" removed
	:rtype: list[str]

	>>> _parse_stops([{"name": "Toronto"}, {"name": "Express To"}, {"name": "Ottawa"}])
	['Toronto', 'Ottawa']
	>>> _parse_stops([{"name": "Montreal"}])
	['Montreal']
	"""
	stops = []
	for stop in stops_list:
		if stop["name"] != "Express To":
			stops.append(stop["name"])
	return stops




if __name__ == "__main__":
	times_fetched = 0

	while True:
		data_json = fetch_data()
		trips = parse_data_trips(data_json)
		
		# unnecessary call since api call returns in time sorted already?
		trips.sort(key=lambda trip: trip.departure_time)

		pprint([f"{trip.line} {trip.departure_time.isoformat()} | {trip.platforms}" for trip in trips])

		first_trip_unknown_platform = None
		for trip in trips:
			if not trip.platforms and trip.info != "Cancelled / Annulé":
				first_trip_unknown_platform = trip
				break
		
		if first_trip_unknown_platform: 
			print(f"\nFirst trip with unknown platform: {first_trip_unknown_platform.line} at {first_trip_unknown_platform.departure_time.isoformat()}")

			next_platform_reveal_time = first_trip_unknown_platform.departure_time -  timedelta(minutes = 8)

			wait_time = (next_platform_reveal_time - datetime.now()).total_seconds()

			if wait_time < 0:
				print("Platform reveal time has already passed..? Will fetch again in 5 minutes.")
				wait_time = 300  # 5 minutes
		else:
			print("All trips have known platforms. Will check next hour.")
			wait_time = 3600  # 1 hour
			next_platform_reveal_time = datetime.now() + timedelta(seconds=wait_time)

		times_fetched += 1
		print(f"Times fetched: {times_fetched}. Next fetch at {next_platform_reveal_time.isoformat()} (in {wait_time} seconds)\n")


		for known_platform_trip in [trip for trip in trips if trip.platforms]:
			if not trip_exists(known_platform_trip):
				create_trip(known_platform_trip)
				print(f"Stored trip: {known_platform_trip.line} at {known_platform_trip.departure_time.isoformat()} with platforms {known_platform_trip.platforms}")
			else:
				print(f"Trip already exists in database: {known_platform_trip.line} at {known_platform_trip.departure_time.isoformat()}")
		
		if wait_time > 0:
			sleep(wait_time)
		sleep(5);