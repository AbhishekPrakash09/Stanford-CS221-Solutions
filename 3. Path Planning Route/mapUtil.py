import json
from collections import defaultdict
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Dict, List, Optional, Set, Tuple

import osmium
from osmium import osm

# Constants
RADIUS_EARTH = 6371000  # Radius of earth in meters (~ equivalent to 3956 miles).
UNIT_DELTA = 0.00001    # Denotes the change in latitude/longitude (in degrees) that
                        # equates to distance of ~1m.

########################################################################################
# Map Abstraction Overview & Useful Data Structures
#   > `GeoLocation` :: forms the atomic units of our abstraction; each `GeoLocation`
#                      object is uniquely specified as a pair of coordinates denoting
#                      latitude/longitude (in degrees).
#
#   > `CityMap` is the core structure defining the following:
#       + `locations` [str -> GeoLocation]: A dictionary mapping a unique label to a
#                                           specific GeoLocation.
#
#       + `tags` [str -> List[str]]: A dictionary mapping a location label (same keys
#                                    as above) to a list of meaningful "tags"
#                                    (e.g., amenity=park or landmark=hoover_tower).
#                                    These tags are parsed from OpenStreetMaps or
#                                    defined manually as "landmarks" in
#                                    `data/stanford-landmarks.json`.
#
#       + `distances` [str -> [str -> float]]: A nested dictionary mapping pairs of
#                                              locations to distances (e.g.,
#                                              `distances[label1][label2] = 21.3`).


@dataclass(frozen=True)
class GeoLocation:
    """A latitude/longitude of a physical location on Earth."""
    latitude: float
    longitude: float

    def __repr__(self):
        return f"{self.latitude},{self.longitude}"


class CityMap:
    """
    A city map consists of a set of *labeled* locations with associated tags, and
    connections between them.
    """
    def __init__(self) -> None:
        # Location label -> actual geolocation (latitude/longitude)
        self.geoLocations: Dict[str, GeoLocation] = {}

        # Location label -> list of tags (e.g., amenity=park)
        self.tags: Dict[str, List[str]] = defaultdict(list)

        # Location label -> adjacent location label -> distance between the two
        self.distances: Dict[str, Dict[str, float]] = defaultdict(dict)

    def addLocation(self, label: str, location: GeoLocation, tags: List[str]) -> None:
        """Add a location (denoted by `label`) to map with the provided set of tags."""
        assert label not in self.geoLocations, f"Location {label} already processed!"
        self.geoLocations[label] = location
        self.tags[label] = [makeTag("label", label)] + tags

    def addConnection(
        self, source: str, target: str, distance: Optional[float] = None
    ) -> None:
        """Adds a connection between source <--> target to `self.distances`."""
        if distance is None:
            distance = computeDistance(
                self.geoLocations[source], self.geoLocations[target]
            )
        self.distances[source][target] = distance
        self.distances[target][source] = distance


def addLandmarks(
    cityMap: CityMap, landmarkPath: str, toleranceMeters: float = 250.0
) -> None:
    """
    Add landmarks from `path` to `cityMap`. A landmark (e.g., Gates Building) is
    associated with a `GeoLocation`.

    Landmarks are explicitly defined via the `landmarkPath` file, which borrows
    latitude/longitude for various spots on Stanford Campus from Google Maps; these
    may not *exactly* line up with existing locations in the CityMap, so instead we map
    a given landmark onto the closest existing location (subject to a max tolerance).
    """
    with open(landmarkPath) as f:
        landmarks = json.load(f)

    # Iterate through landmarks and map onto the closest location in `cityMap`
    for item in landmarks:
        latitudeString, longitudeString = item["geo"].split(",")
        geo = GeoLocation(float(latitudeString), float(longitudeString))

        # Find the closest location by searching over all locations in `cityMap`
        bestDistance, bestLabel = min(
            (computeDistance(geo, existingGeo), existingLabel)
            for existingLabel, existingGeo in cityMap.geoLocations.items()
        )

        if bestDistance < toleranceMeters:
            for key in ["landmark", "amenity"]:
                if key in item:
                    cityMap.tags[bestLabel].append(makeTag(key, item[key]))

########################################################################################
# Utility Functions


def makeTag(key: str, value: str) -> str:
    """Locations have string-valued tags which are created from (key, value) pairs."""
    return f"{key}={value}"


def locationFromTag(tag: str, cityMap: CityMap) -> Optional[str]:
    possibleLocations = sorted(
        [location for location, tags in cityMap.tags.items() if tag in tags]
    )
    return possibleLocations[0] if len(possibleLocations) > 0 else None


def computeDistance(geo1: GeoLocation, geo2: GeoLocation) -> float:
    """
    Compute the distance (straight line) between two geolocations, specified as
    latitude/longitude. This function is analogous to finding the euclidean distance
    between points on a plane; however, because the Earth is spherical, we're using the
    *Haversine formula* to compute distance subject to the curved surface.

    You can read more about the Haversine formula here:
     > https://en.wikipedia.org/wiki/Haversine_formula

    Note :: For small distances (e.g., Stanford campus --> the greater Bay Area),
    factoring in the curvature of the earth might be a bit overkill!

    However, you could think about using this function to generalize to larger maps
    spanning much greater distances (possibly for fun future projects)!

    :param geo1: Source `GeoLocation`, with attributes for latitude/longitude.
    :param geo2: Target `GeoLocation`, with attributes for latitude/longitude.

    :return: Returns distance between geo1 and geo2 in meters.
    :rtype: float (distance)
    """
    lon1, lat1 = radians(geo1.longitude), radians(geo1.latitude)
    lon2, lat2 = radians(geo2.longitude), radians(geo2.latitude)

    # Haversine formula
    deltaLon, deltaLat = lon2 - lon1, lat2 - lat1
    haversine = (sin(deltaLat / 2) ** 2) + (cos(lat1) * cos(lat2)) * (
        sin(deltaLon / 2) ** 2
    )

    # Return distance d (factor in radius of earth in meters)
    return 2 * RADIUS_EARTH * asin(sqrt(haversine))


def checkValid(
    path: List[str],
    cityMap: CityMap,
    startLocation: str,
    endTag: str,
    waypointTags: List[str],
) -> bool:
    """Check if a given solution/path is valid subject to the given CityMap instance."""
    # Check that path starts with `startLocation`
    if path[0] != startLocation:
        print(f"Invalid path: does not start with {startLocation}")
        return False

    # Check that path ends with a location with `endTag`
    if endTag not in cityMap.tags[path[-1]]:
        print("Invalid path: final location does not contain {endTag}")
        return False

    # Check that adjacent locations are *connected* in the underlying CityMap instance
    for i in range(len(path) - 1):
        if path[i + 1] not in cityMap.distances[path[i]]:
            print(f"Invalid path: {path[i]} is not connected to {path[i + 1]}")
            return False

    # Check that all waypointTags are represented
    doneTags = set(tag for location in path for tag in cityMap.tags[location])
    diffTags = set(waypointTags).difference(doneTags)
    if len(diffTags) > 0:
        print(f"Invalid path: does not contain waypoints {diffTags}")
        return False

    # Otherwise, we're good!
    return True


def getTotalCost(path: List[str], cityMap: CityMap) -> float:
    """Return the total distance of the given path (assuming it's valid)."""
    cost = 0.0
    for i in range(len(path) - 1):
        cost += cityMap.distances[path[i]][path[i + 1]]
    return cost


########################################################################################
# Data Processing Functions -- for creating simple programmatic maps, and loading maps
# from OpenStreetMap (OSM) data. Here are some useful acronyms that you may find useful
# as you read through the following code:
#
#   - `OSM` (OpenStreetMap): We use actual data from the OpenStreetMaps project
#                            (https://www.openstreetmap.org/). You can think of
#                            OpenStreetMaps as "Wikipedia" for Google Maps; lots
#                            of useful info!
#
#   - `*.pbf`: File format for OSM data; `pbf` = Protocolbuffer Binary Format; a file
#              format like xml/json that's used by OpenStreetMaps. You shouldn't need
#              to worry about this, as we provide utilities to read these files below.
#
#   - `osmium`: A Python package for dealing with `OSM` data. You will need to install
#               this as a dependency (via `requirements.txt` or `pip install osmium`).


def makeGridLabel(x: int, y: int) -> str:
    """Function to create location label from (latitude, longitude) in degrees."""
    return f"{x},{y}"


def createGridMap(width: int, height: int) -> CityMap:
    """Create a simple map width x height grid of locations."""
    cityMap = CityMap()

    # A "simple" city is just a grid with distance ~1m between adjacent locations.
    for x, lat in enumerate([x * UNIT_DELTA for x in range(width)]):
        for y, lon in enumerate([y * UNIT_DELTA for y in range(height)]):
            # We label each location as just the grid index (x, y)
            cityMap.addLocation(
                makeGridLabel(x, y),
                GeoLocation(lat, lon),
                tags=[makeTag("x", x), makeTag("y", y)],
            )
            if x > 0:
                cityMap.addConnection(
                    makeGridLabel(x - 1, y), makeGridLabel(x, y), distance=1
                )
            if y > 0:
                cityMap.addConnection(
                    makeGridLabel(x, y - 1), makeGridLabel(x, y), distance=1
                )

    return cityMap

def createGridMapWithCustomTags(width: int, height: int, tags: Dict[Tuple[int,int], List[str]]) -> CityMap:
    """Create a simple map width x height grid of locations."""
    cityMap = CityMap()

    # A "simple" city is just a grid with distance ~1m between adjacent locations.
    for x, lat in enumerate([x * UNIT_DELTA for x in range(width)]):
        for y, lon in enumerate([y * UNIT_DELTA for y in range(height)]):
            # We label each location as just the grid index (x, y)
            cityMap.addLocation(
                makeGridLabel(x, y),
                GeoLocation(lat, lon),
                tags=[makeTag("x", x), makeTag("y", y)] + tags[(x,y)],
            )
            if x > 0:
                cityMap.addConnection(
                    makeGridLabel(x - 1, y), makeGridLabel(x, y), distance=1
                )
            if y > 0:
                cityMap.addConnection(
                    makeGridLabel(x, y - 1), makeGridLabel(x, y), distance=1
                )

    return cityMap

def readMap(osmPath: str) -> CityMap:
    """
    Create a CityMap given a path to a OSM `.pbf` file; uses the osmium package to do
    any/all processing of discrete locations and connections between them.

    :param osmPath: Path to `.pbf` file defining a set of locations and connections.
    :return An initialized CityMap object, built using the OpenStreetMaps data.
    """
    # Note :: `osmium` defines a nice class called `SimpleHandler` to facilitate
    # reading `.pbf` files.
    #   > You can read more about this class/functionality here:
    #     https://docs.osmcode.org/pyosmium/latest/intro.html
    class MapCreationHandler(osmium.SimpleHandler):
        def __init__(self) -> None:
            super().__init__()
            self.nodes: Dict[str, GeoLocation] = {}
            self.tags: Dict[str, List[str]] = defaultdict(list)
            self.edges: Set[str, str] = set()

        def node(self, n: osm.Node) -> None:
            """An `osm.Node` contains the actual tag attributes for a given node."""
            self.tags[str(n.id)] = [makeTag(tag.k, tag.v) for tag in n.tags]

        def way(self, w: osm.Way) -> None:
            """An `osm.Way` contains an ordered list of connected nodes."""

            # We only include "ways" that are accessible on foot
            #   =>> Reference: https://github.com/Tristramg/osm4routing2
            #                  See -> `src/osm4routing/categorize.rs#L96`
            pathType = w.tags.get("highway", None)
            if pathType is None or pathType in {
                "motorway",
                "motorway_link",
                "trunk",
                "trunk_link",
            }:
                return
            elif (
                w.tags.get("pedestrian", "n/a") == "no"
                or w.tags.get("foot", "n/a") == "no"
            ):
                return

            # Otherwise, iterate through all nodes along the "way"...
            wayNodes = w.nodes
            for sourceIdx in range(len(wayNodes) - 1):
                s, t = wayNodes[sourceIdx], wayNodes[sourceIdx + 1]
                sLabel, tLabel = str(s.ref), str(t.ref)
                sLoc = GeoLocation(s.location.lat, s.location.lon)
                tLoc = GeoLocation(t.location.lat, t.location.lon)

                # Assert that the locations aren't the same!
                assert sLoc != tLoc, "Source and Target are the same location!"

                # Add to trackers...
                self.nodes[sLabel], self.nodes[tLabel] = sLoc, tLoc
                self.edges.add((sLabel, tLabel))

    # Build nodes & edges via MapCreationHandler
    #   > Pass `location=True` to enforce embedded lat/lon geometries!
    mapCreator = MapCreationHandler()
    mapCreator.apply_file(osmPath, locations=True)

    # Build CityMap by iterating through the parsed nodes and connections
    cityMap = CityMap()
    for nodeLabel in mapCreator.nodes:
        cityMap.addLocation(
            nodeLabel, mapCreator.nodes[nodeLabel], tags=mapCreator.tags[nodeLabel]
        )

    # When adding connections, don't pass distance flag (automatically compute!)
    for src, tgt in mapCreator.edges:
        cityMap.addConnection(src, tgt)

    return cityMap


def printMap(cityMap: CityMap):
    """Display a dense overview of the provided map, with tags for each location."""
    for label in cityMap.geoLocations:
        tagsStr = " ".join(cityMap.tags[label])
        print(f"{label} ({cityMap.geoLocations[label]}): {tagsStr}")
        for label2, distance in cityMap.distances[label].items():
            print(f"  -> {label2} [distance = {distance}]")


def createStanfordMap() -> CityMap:
    cityMap = readMap("data/stanford.pbf")
    addLandmarks(cityMap, "data/stanford-landmarks.json")
    return cityMap

def createCustomMap(map_file: str, landmarks_file: str) -> CityMap:
    """
    Create a CityMap given a path to an OSM `.pbf` file; uses the osmium package to do
    any/all processing of discrete locations and connections between them.
    
    :param map_file: Path to `.pbf` file defining a set of locations and connections.
    :param landmarks_file: Path to `.json` file defining a set of landmarks.
    
    For further details on the format of the `.pbf` and `.json` files, see the README.md file.
    """
    cityMap = readMap(map_file)
    addLandmarks(cityMap, landmarks_file)
    return cityMap


if __name__ == "__main__":
    stanfordMap = createStanfordMap()
    printMap(stanfordMap)
