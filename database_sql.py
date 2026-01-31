import sqlite3
from database import Database
from entities import Trip
from datetime import datetime

DB_PATH = "data.db"
def initialize_database():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.executescript('''
    CREATE TABLE IF NOT EXISTS trips (
      id INTEGER PRIMARY KEY,
      info TEXT,
      number TEXT,
      platforms TEXT,
      line TEXT,
      service_type TEXT,
      is_express BOOLEAN,
      departure_time TEXT,
      coach_count INTEGER,
      scheduled_coach_count INTEGER,
      stops TEXT,
      UNIQUE(departure_time, line, number)
    );
    CREATE INDEX IF NOT EXISTS idx_departure_time ON trips(departure_time);
  ''')
  conn.commit()
  conn.close()

class SQLite(Database):
  def get_connection(self):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
    
  def create_trip(self, trip: Trip) -> int:
    with self.get_connection() as conn:
      c = conn.cursor()
      c.execute('''
        SELECT * FROM trips WHERE departure_time = ? AND line = ? AND number = ?
        ''',
        (trip.departure_time.isoformat(), trip.line, trip.number)
      )
      row = c.fetchone()
      if row:
        return row["id"]
      
      c.execute('''
        INSERT INTO trips (
          info, number, platforms, line, service_type, is_express,
          departure_time, coach_count, scheduled_coach_count, stops
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ''', (
        trip.info,
        trip.number,
        str(trip.platforms),
        trip.line,
        trip.serviceType,
        trip.is_express,
        trip.departure_time.isoformat(),
        trip.coach_count,
        trip.scheduled_coach_count,
        str(trip.stops),
      ))
      return c.lastrowid

  def get_all_trips(self) -> list[Trip]:
    with self.get_connection() as conn:
      c = conn.cursor()
      c.execute('SELECT * FROM trips')
      rows = c.fetchall()
      trips = []
      for row in rows:
        trip = Trip(
          info=row["info"],
          number=row["number"],
          platforms=eval(row["platforms"]),
          line=row["line"],
          serviceType=row["service_type"],
          is_express=bool(row["is_express"]),
          departure_time=datetime.fromisoformat(row["departure_time"]),
          coach_count=row["coach_count"],
          scheduled_coach_count=row["scheduled_coach_count"],
          stops=eval(row["stops"]),
        )
        trips.append(trip)
      return trips
    

  def trip_exists(self, trip: Trip) -> bool:
    with self.get_connection() as conn:
      c = conn.cursor()
      c.execute('''
        SELECT 1 FROM trips WHERE departure_time = ? AND line = ? 
      ''', (trip.departure_time.isoformat(), trip.line))
      return c.fetchone() is not None

if __name__ == "__main__":
  initialize_database()