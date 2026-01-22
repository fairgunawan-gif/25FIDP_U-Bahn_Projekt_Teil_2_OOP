@startuml

class Station {
    - name: str
    + __init__(name: str)
    + __repr__(): str
    + __hash__(): int
    + __eq__(other): bool
}

class Connection {
    - destination: Station
    - travel_time: int
    + __init__(destination: Station, travel_time_minutes: int)
}

class Line {
    - adjacency: Dict[Station, List[Connection]]
    + __init__()
    + add_connection(from_station: Station, to_station: Station, travel_time_minutes: int)
    + stations(): List[Station]
    + travel_time_from_start(start: Station, target: Station): int
    + __str__(): str
}

class Schedule {
    - first: time
    - last: time
    - interval: timedelta
    + __init__(first: time, last: time, interval_minutes: int)
    + departures_from_start(): List[datetime]
}

class DepartureService {
    - line: Line
    - schedule: Schedule
    - start_station: Station
    + __init__(line: Line, schedule: Schedule, start_station: Station)
    + next_departure(station: Station, desired_time: time): time
}

Station "1" <-- "0..*" Connection : destination
Line "1" o-- "0..*" Connection
Line "1" --> "0..*" Station : adjacency key
DepartureService --> Line
DepartureService --> Schedule
DepartureService --> Station : start_station

@enduml
