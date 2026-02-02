from database import Database
from entities import Trip
from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
assert SUPABASE_URL and SUPABASE_KEY, "Key/url not set for supabase in env"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class Supabase(Database): 
  def create_trip(self, trip: Trip) -> int:
    existing = supabase.table("trips").select("*").eq("departure_time", trip.departure_time.isoformat()).eq("line", trip.line).eq("number", trip.number).execute()
    if existing.data:
      return existing.data[0]["id"]
    
    data = trip.to_dict()
    
    response = supabase.table("trips").insert(data).execute()
    return response.data[0]["id"]

  def upsert_trip(self, trip: Trip) -> int:
    existing = supabase.table("trips").select("*").eq("departure_time", trip.departure_time.isoformat()).eq("line", trip.line).eq("number", trip.number).execute()
    if existing.data:
      supabase.table("trips").update(trip.to_dict()).eq("id", existing.data[0]["id"]).execute()
      return existing.data[0]["id"]
    
    data = trip.to_dict()
    response = supabase.table("trips").insert(data).execute()
    return response.data[0]["id"]
  
  def get_all_trips(self) -> list[Trip]:
    response = (
      supabase
      .table("trips")
      .select("*")
      .execute()
    )
    trips = []
    for row in response.data:
        trip = Trip.from_row(row)
        trips.append(trip)
    return trips
    

  def trip_exists(self, trip: Trip) -> bool:
    response = (
      supabase.table("trips")
      .select("id")
      .eq("departure_time", trip.departure_time.isoformat())
      .eq("line", trip.line)
      .eq("number", trip.number)
      .execute()
    )
    if len(response.data) > 0:
      return True
    return False
  
  def batch_upsert_trips(self, trips: list[Trip]) -> int:
    data = [trip.to_dict() for trip in trips]
    response = supabase.table("trips").upsert(data, on_conflict="departure_time,line,number").execute()
    return len(response.data)
