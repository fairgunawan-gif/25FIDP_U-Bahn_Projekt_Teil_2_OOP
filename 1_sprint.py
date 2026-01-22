from datetime import time, timedelta, datetime
from typing import Dict, List


# ====== Domain Classes ======

class Station:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Station({self.name})"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Station) and self.name == other.name


class Connection:
    def __init__(self, destination: Station, travel_time_minutes: int):
        self.destination = destination
        self.travel_time = travel_time_minutes


class Line:
    """
    Directed graph (Sprint 1: single path)
    """
    def __init__(self):
        self.adjacency: Dict[Station, List[Connection]] = {}

    def add_connection(self, from_station: Station, to_station: Station, travel_time_minutes: int):
        self.adjacency.setdefault(from_station, [])
        self.adjacency.setdefault(to_station, [])
        self.adjacency[from_station].append(
            Connection(to_station, travel_time_minutes)
        )

    def stations(self) -> List[Station]:
        return list(self.adjacency.keys())

    def travel_time_from_start(self, start: Station, target: Station) -> int:
        current = start
        total = 0

        while current != target:
            connections = self.adjacency.get(current)
            if not connections:
                raise ValueError("Kein Pfad verfügbar")
            conn = connections[0]
            total += conn.travel_time
            current = conn.destination

        return total

    def __str__(self):
        result = []
        for s, connections in self.adjacency.items():
            for c in connections:
                result.append(f"{s.name} → {c.destination.name} ({c.travel_time} min)")
        return "\n".join(result)


class Schedule:
    """
    Global schedule at start station A
    """
    def __init__(self, first: time, last: time, interval_minutes: int):
        self.first = first
        self.last = last
        self.interval = timedelta(minutes=interval_minutes)

    def departures_from_start(self) -> List[datetime]:
        today = datetime.today().date()
        current = datetime.combine(today, self.first)
        end = datetime.combine(today, self.last)

        result = []
        while current <= end:
            result.append(current)
            current += self.interval
        return result


class DepartureService:
    """
    Computes derived departures at any station
    based on the global start schedule.
    """
    def __init__(self, line: Line, schedule: Schedule, start_station: Station):
        self.line = line
        self.schedule = schedule
        self.start_station = start_station

    def next_departure(self, station: Station, desired_time: time) -> time:
        offset_minutes = self.line.travel_time_from_start(
            self.start_station, station
        )

        desired_dt = datetime.combine(datetime.today().date(), desired_time)

        for dep in self.schedule.departures_from_start():
            arrival = dep + timedelta(minutes=offset_minutes)
            if arrival >= desired_dt:
                return arrival.time()

        raise ValueError("Keine weitere Abfahrt verfügbar")


# ====== Setup ======

A = Station("A")
B = Station("B")
C = Station("C")
D = Station("D")

line = Line()
line.add_connection(A, B, 2)
line.add_connection(B, C, 3)
line.add_connection(C, D, 1)

schedule = Schedule(
    first=time(5, 0),
    last=time(23, 0),
    interval_minutes=10
)

service = DepartureService(line, schedule, start_station=A)


# ====== Terminal UI Helpers ======

def parse_time(value: str) -> time:
    try:
        h, m = map(int, value.strip().split(":"))
        return time(h, m)
    except:
        raise ValueError("Zeitformat muss HH:MM sein")


def select_station(stations: List[Station]) -> Station:
    print("\nStartstation auswählen:")
    for i, station in enumerate(stations, start=1):
        print(f"{i}. {station.name}")

    while True:
        choice = input("Nummer eingeben: ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(stations):
                return stations[idx - 1]
        print("Ungültige Auswahl. Bitte erneut versuchen.")


# ====== Main Program ======

def main():
    print("Fahrplanauskunft – Sprint 1")
    print("\nStrecke:")
    print(line)

    stations = line.stations()
    start_station = select_station(stations)

    while True:
        try:
            desired_time_str = input(
                "\nGewünschte Abfahrtszeit (HH:MM): "
            ).strip()
            desired_time = parse_time(desired_time_str)
            break
        except ValueError as e:
            print(f"Fehler: {e}")

    try:
        next_dep = service.next_departure(start_station, desired_time)
        print(
            f"\nNächste Abfahrt von Station {start_station.name}: "
            f"{next_dep.strftime('%H:%M')}"
        )
    except ValueError as e:
        print(f"Fehler: {e}")


if __name__ == "__main__":
    main()
