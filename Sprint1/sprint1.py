from datetime import time, datetime, timedelta
from typing import Dict, List


# =========================
# Domain Model / Fachmodell
# =========================

class Station:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        # Darstellung der Station / String representation of station
        return f"Station({self.name})"

    def __hash__(self):
        # Stationen müssen als Dictionary-Key nutzbar sein
        # Stations must be hashable to be used as dict keys
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Station) and self.name == other.name


class Connection:
    def __init__(self, destination: Station, travel_time_minutes: int):
        # Zielstation / destination station
        self.destination = destination
        # Fahrzeit in Minuten / travel time in minutes
        self.travel_time_minutes = travel_time_minutes


class Line:
    def __init__(self):
        # Gewichtete Adjazenzliste
        # Weighted adjacency list
        self.adjacency: Dict[Station, List[Connection]] = {}

    def add_station(self, station: Station):
        # Station zur Linie hinzufügen
        # Add station to the line
        if station not in self.adjacency:
            self.adjacency[station] = []

    def connect(self, from_station: Station, to_station: Station, minutes: int):
        # Gerichtete Verbindung mit Gewicht
        # Directed weighted connection
        self.add_station(from_station)
        self.add_station(to_station)
        self.adjacency[from_station].append(
            Connection(to_station, minutes)
        )

    def get_travel_time_from_start(self, start: Station, target: Station) -> int:
        """
        Berechnet die kumulierte Fahrzeit vom Start bis zur Zielstation.
        Calculates cumulative travel time from start to target station.
        """
        current = start
        total_minutes = 0

        # Da Sprint 1 nur eine lineare Strecke erlaubt,
        # können wir einfach vorwärts iterieren.
        # Since Sprint 1 is strictly linear, we iterate forward.
        while current != target:
            connection = self.adjacency[current][0]
            total_minutes += connection.travel_time_minutes
            current = connection.destination

        return total_minutes


# =================================
# Application Logic / Zeitberechnung
# =================================

class TimetableService:
    def __init__(
        self,
        line: Line,
        first_departure: time,
        last_departure: time,
        interval_minutes: int
    ):
        self.line = line
        self.first_departure = first_departure
        self.last_departure = last_departure
        self.interval_minutes = interval_minutes

    def get_next_departure(self, station: Station, desired_time: time) -> time:
        """
        Gibt die nächste tatsächliche Abfahrtszeit zurück,
        die gleich oder nach der Wunschzeit liegt.

        Returns the next actual departure time
        equal to or later than the desired time.
        """

        start_station = Station("A")

        # Fahrzeit vom Start zur gewünschten Station
        # Travel time from A to target station
        offset_minutes = self.line.get_travel_time_from_start(
            start_station, station
        )

        # Startzeit als datetime für Berechnungen
        # Convert start time to datetime for calculations
        current = datetime.combine(
            datetime.today(), self.first_departure
        )

        last = datetime.combine(
            datetime.today(), self.last_departure
        )

        desired_dt = datetime.combine(
            datetime.today(), desired_time
        )

        while current <= last:
            arrival_time = current + timedelta(minutes=offset_minutes)

            if arrival_time >= desired_dt:
                return arrival_time.time()

            current += timedelta(minutes=self.interval_minutes)

        # Falls kein Zug mehr fährt
        # If no more trains are running
        raise ValueError("Keine weitere Abfahrt an diesem Tag.")


# =========================
# Setup der Teststrecke
# =========================

line = Line()

A = Station("A")
B = Station("B")
C = Station("C")
D = Station("D")

line.connect(A, B, 2)
line.connect(B, C, 3)
line.connect(C, D, 1)

timetable = TimetableService(
    line=line,
    first_departure=time(5, 0),
    last_departure=time(23, 0),
    interval_minutes=10
)
# =========================
# User Input / Benutzereingabe
# =========================

def read_station_input() -> Station:
    """
    Liest den Namen der Haltestelle ein und gibt das passende Station-Objekt zurück.
    Reads the station name and returns the corresponding Station object.
    """
    station_map = {
        "A": A,
        "B": B,
        "C": C,
        "D": D
    }

    while True:
        name = input("Bitte Haltestelle eingeben (A, B, C, D): ").strip().upper()
        if name in station_map:
            return station_map[name]
        print("Ungültige Haltestelle. Bitte erneut eingeben.")


def read_time_input() -> time:
    """
    Liest eine Uhrzeit im Format HH:MM ein.
    Reads a time in HH:MM format.
    """
    while True:
        value = input("Bitte gewünschte Abfahrtszeit eingeben (HH:MM): ").strip()
        try:
            return datetime.strptime(value, "%H:%M").time()
        except ValueError:
            print("Ungültiges Zeitformat. Bitte HH:MM verwenden.")


# =========================
# Program Start / Programmstart
# =========================

if __name__ == "__main__":
    try:
        station = read_station_input()
        desired_time = read_time_input()

        next_departure = timetable.get_next_departure(station, desired_time)

        print(
            f"Die nächste Bahn fährt um {next_departure} "
            f"an Haltestelle {station.name} ab."
        )

    except ValueError as e:
        # Fachliche Fehlerausgabe
        # Business-level error output
        print(str(e))

