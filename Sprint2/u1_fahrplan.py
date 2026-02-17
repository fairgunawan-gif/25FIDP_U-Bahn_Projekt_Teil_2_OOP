from datetime import datetime
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


# ----------------------------
# Hilfsfunktionen
# ----------------------------
def time_to_minutes(t):
    if t == "NA":
        return None
    h, m, s = map(int, t.split(":"))
    return h * 60 + m + s / 60


def minutes_to_time(min_float):
    whole = int(min_float)
    sec = int(round((min_float - whole) * 60))
    if sec == 60:
        whole += 1
        sec = 0
    hh = whole // 60
    mm = whole % 60
    return f"{hh:02d}:{mm:02d}:{sec:02d}"


# ----------------------------
# Datenklassen
# ----------------------------

class Station:
    def __init__(self, name, ankunft, abfahrt):
        self.name = name
        self.ankunft = time_to_minutes(ankunft)
        self.abfahrt = time_to_minutes(abfahrt)


class Richtung:
    def __init__(self, stationen, takt=10, betriebsschluss=23):
        self.stationen = stationen
        self.takt = takt
        self.betriebsschluss = betriebsschluss * 60
        self.index_map = {s.name: i for i, s in enumerate(stationen)}

        # find first valid departure
        self.base_start = next(
            s.abfahrt for s in stationen if s.abfahrt is not None
        )

        # find last valid arrival
        self.base_end = next(
            s.ankunft for s in reversed(stationen) if s.ankunft is not None
        )

        self.duration = self.base_end - self.base_start

    def finde_verbindung(self, start, ziel, wunsch_min):
        if start not in self.index_map or ziel not in self.index_map:
            return None, None, False

        start_index = self.index_map[start]
        ziel_index = self.index_map[ziel]

        if ziel_index <= start_index:
            return None, None, False

        # Two passes: first today, then next day if nothing found
        for next_day in [False, True]:
            effective_wunsch = wunsch_min if not next_day else 0
            zugstart = self.base_start

            while zugstart <= self.betriebsschluss:
                offset = zugstart - self.base_start

                start_abfahrt = self.stationen[start_index].abfahrt
                ziel_ankunft = self.stationen[ziel_index].ankunft

                if start_abfahrt is None or ziel_ankunft is None:
                    zugstart += self.takt
                    continue

                abfahrt = start_abfahrt + offset
                ankunft = ziel_ankunft + offset

                if abfahrt >= effective_wunsch and ankunft > abfahrt:
                    return minutes_to_time(abfahrt), minutes_to_time(ankunft), next_day

                zugstart += self.takt

        return None, None, False


class LinieU1:
    def __init__(self, stationen_hin, stationen_zurueck, takt=10):
        self.richtung_hin = Richtung(stationen_hin, takt)
        self.richtung_zurueck = Richtung(stationen_zurueck, takt)

    def naechste_abfahrt_und_ankunft(self, start, ziel, uhrzeit):
        h, m = map(int, uhrzeit.split(":"))
        wunsch = h * 60 + m

        # try forward direction
        abfahrt, ankunft, next_day = self.richtung_hin.finde_verbindung(start, ziel, wunsch)
        if abfahrt:
            return abfahrt, ankunft, next_day

        # try backward direction
        abfahrt, ankunft, next_day = self.richtung_zurueck.finde_verbindung(start, ziel, wunsch)
        if abfahrt:
            return abfahrt, ankunft, next_day

        return None, None, False

    def stationen_anzahl(self, start, ziel):
        for richtung in [self.richtung_hin, self.richtung_zurueck]:
            if start in richtung.index_map and ziel in richtung.index_map:
                i1 = richtung.index_map[start]
                i2 = richtung.index_map[ziel]
                if i2 > i1:
                    return i2 - i1
        return 0


# ----------------------------
# U1 Fahrplan – Erste komplette Runde
# ----------------------------

u1_daten_richtung_hin = [
    ("Langwasser Süd", "NA", "05:00:00"),
    ("Gemeinschaftshaus", "05:03:00", "05:03:30"),
    ("Langwasser Mitte", "05:05:30", "05:06:00"),
    ("Scharfreiterring", "05:08:00", "05:08:30"),
    ("Langwasser Nord", "05:11:30", "05:12:00"),
    ("Messe", "05:14:00", "05:14:30"),
    ("Bauernfeindstraße", "05:17:30", "05:18:00"),
    ("Hasenbuck", "05:20:00", "05:20:30"),
    ("Frankenstraße", "05:22:30", "05:23:00"),
    ("Maffeiplatz", "05:25:00", "05:25:30"),
    ("Aufseßplatz", "05:26:30", "05:27:00"),
    ("Hauptbahnhof", "05:29:00", "05:30:00"),
    ("Lorenzkirche", "05:32:00", "05:32:30"),
    ("Weißer Turm", "05:35:30", "05:36:00"),
    ("Plärrer", "05:38:00", "05:39:00"),
    ("Gostenhof", "05:41:00", "05:41:30"),
    ("Bärenschanze", "05:42:30", "05:43:00"),
    ("Maximilianstraße", "05:45:00", "05:45:30"),
    ("Eberhardshof", "05:47:30", "05:48:00"),
    ("Muggenhof", "05:50:00", "05:50:30"),
    ("Stadtgrenze", "05:53:30", "05:54:00"),
    ("Jakobinenstraße", "05:56:00", "05:56:30"),
    ("Fürth Hbf.", "05:59:30", "06:00:30")
]

u1_daten_richtung_zurueck = [
    ("Fürth Hbf.", "05:59:30", "06:00:30"),
    ("Jakobinenstraße", "06:03:30", "06:04:00"),
    ("Stadtgrenze", "06:06:00", "06:06:30"),
    ("Muggenhof", "06:09:30", "06:10:00"),
    ("Eberhardshof", "06:12:00", "06:12:30"),
    ("Maximilianstraße", "06:14:30", "06:15:00"),
    ("Bärenschanze", "06:17:00", "06:17:30"),
    ("Gostenhof", "06:18:30", "06:19:00"),
    ("Plärrer", "06:21:00", "06:22:00"),
    ("Weißer Turm", "06:24:00", "06:24:30"),
    ("Lorenzkirche", "06:27:30", "06:28:00"),
    ("Hauptbahnhof", "06:30:00", "06:31:00"),
    ("Aufseßplatz", "06:33:00", "06:33:30"),
    ("Maffeiplatz", "06:34:30", "06:35:00"),
    ("Frankenstraße", "06:37:00", "06:37:30"),
    ("Hasenbuck", "06:39:30", "06:40:00"),
    ("Bauernfeindstraße", "06:42:00", "06:42:30"),
    ("Messe", "06:45:30", "06:46:00"),
    ("Langwasser Nord", "06:48:00", "06:48:30"),
    ("Scharfreiterring", "06:51:30", "06:52:00"),
    ("Langwasser Mitte", "06:54:00", "06:54:30"),
    ("Gemeinschaftshaus", "06:56:30", "06:57:00"),
    ("Langwasser Süd", "07:00:00", "NA")
]

# Build Station objects for each direction separately
stationen_hin = [Station(name, ank, abf) for name, ank, abf in u1_daten_richtung_hin]
stationen_zurueck = [Station(name, ank, abf) for name, ank, abf in u1_daten_richtung_zurueck]

u1 = LinieU1(stationen_hin, stationen_zurueck)


# ----------------------------
# Autocomplete für Eingabe
# ----------------------------

station_namen = sorted(set(
    [s.name for s in stationen_hin] + [s.name for s in stationen_zurueck]
))
station_completer = WordCompleter(
    station_namen,
    ignore_case=True,
    sentence=True
)

def station_prompt(text):
    return prompt(text, completer=station_completer)


def dialog(u1):
    print("\n--- U1 Fahrplanauskunft ---")

    start = station_prompt("Start-Abfahrt Station: ")
    ziel  = station_prompt("Ziel-Ankunft Station: ")
    zeit_input = input("Gewünschte Abfahrtszeit (HH:MM): ")

    if start not in station_namen or ziel not in station_namen:
        print("Station nicht gefunden.")
        return

    abfahrt, ankunft, next_day = u1.naechste_abfahrt_und_ankunft(start, ziel, zeit_input)

    if abfahrt is None:
        print("Keine passende Verbindung gefunden.")
        return

    anzahl_station = u1.stationen_anzahl(start, ziel)

    print("\n--- Verbindung gefunden ---")
    print(f"Startstation: {start}")
    print(f"Zielstation: {ziel}")
    print(f"Abfahrtszeit: {abfahrt}" + (" (nächster Tag)" if next_day else ""))
    print(f"Ankunftszeit: {ankunft}" + (" (nächster Tag)" if next_day else ""))
    print(f"Anzahl Stationen: {anzahl_station}")



if __name__ == "__main__":
    dialog(u1)
