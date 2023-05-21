import argparse
import json
from typing import List

import plotly.express as px
import plotly.graph_objects as go

from mapUtil import CityMap, addLandmarks, readMap


def plotMap(cityMap: CityMap, path: List[str], waypointTags: List[str], mapName: str):
    """
    Plot the full map, highlighting the provided path.

    :param cityMap: CityMap to plot.
    :param path: List of location labels of the path.
    :param waypointTags: List of tags that we care about hitting along the way.
    :param mapName: Display title for map visualization.
    """
    lat, lon = [], []

    # Convert `cityMap.distances` to a list of (source, target) tuples...
    connections = [
        (source, target)
        for source in cityMap.distances
        for target in cityMap.distances[source]
    ]
    for source, target in connections:
        lat.append(cityMap.geoLocations[source].latitude)
        lat.append(cityMap.geoLocations[target].latitude)
        lat.append(None)
        lon.append(cityMap.geoLocations[source].longitude)
        lon.append(cityMap.geoLocations[target].longitude)
        lon.append(None)

    # Plot all states & connections
    fig = px.line_geo(lat=lat, lon=lon)

    # Plot path (represented by connections in `path`)
    if len(path) > 0:
        solutionLat, solutionLon = [], []

        # Get and convert `path` to (source, target) tuples to append to lat, lon lists
        connections = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        for connection in connections:
            source, target = connection
            solutionLat.append(cityMap.geoLocations[source].latitude)
            solutionLat.append(cityMap.geoLocations[target].latitude)
            solutionLat.append(None)
            solutionLon.append(cityMap.geoLocations[source].longitude)
            solutionLon.append(cityMap.geoLocations[target].longitude)
            solutionLon.append(None)

        # Visualize path by adding a trace
        fig.add_trace(
            go.Scattergeo(
                lat=solutionLat,
                lon=solutionLon,
                mode="lines",
                line=dict(width=5, color="blue"),
                name="solution",
            )
        )

        # Plot the points
        for i, location in enumerate(path):
            tags = set(cityMap.tags[location]).intersection(set(waypointTags))
            if i == 0 or i == len(path) - 1 or len(tags) > 0:
                for tag in cityMap.tags[location]:
                    if tag.startswith("landmark="):
                        tags.add(tag)
            if len(tags) == 0:
                continue

            # Add descriptions as annotations for each point
            description = " ".join(sorted(tags))

            # Color the start node green, the end node red, intermediate gray
            if i == 0:
                color = "red"
            elif i == len(path) - 1:
                color = "green"
            else:
                color = "gray"

            waypointLat = [cityMap.geoLocations[location].latitude]
            waypointLon = [cityMap.geoLocations[location].longitude]

            fig.add_trace(
                go.Scattergeo(
                    lat=waypointLat,
                    lon=waypointLon,
                    mode="markers",
                    marker=dict(size=20, color=color),
                    name=description,
                )
            )

    # Plot cityMap locations with special tags (e.g. landmarks, amenities)
    for location_id, latLon in cityMap.geoLocations.items():
        tags = cityMap.tags[location_id]
        for tag in tags:
            if "landmark" in tag:
                fig.add_trace(
                    go.Scattergeo(
                        locationmode="USA-states",
                        lon=[latLon.longitude],
                        lat=[latLon.latitude],
                        text=tag.split("landmark=")[1],
                        name=tag.split("landmark=")[1],
                        marker=dict(size=10, color="purple", line_width=3),
                    )
                )
            elif "amenity" in tag:
                fig.add_trace(
                    go.Scattergeo(
                        locationmode="USA-states",
                        lon=[latLon.longitude],
                        lat=[latLon.latitude],
                        text=tag.split("amenity=")[1],
                        name=tag.split("amenity=")[1],
                        marker=dict(size=10, color="blue", line_width=3),
                    )
                )

    # Final scaling, centering, and figure title
    midIdx = len(lat) // 2
    fig.update_layout(title=mapName, title_x=0.5)
    fig.update_layout(
        geo=dict(projection_scale=20000, center=dict(lat=lat[midIdx], lon=lon[midIdx]))
    )
    fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--map-file", type=str, default="data/stanford.pbf", help="Map (.pbf)"
    )
    parser.add_argument(
        "--landmark-file",
        type=str,
        default="data/stanford-landmarks.json",
        help="Landmarks (.json)",
    )
    parser.add_argument(
        "--path-file",
        type=str,
        default="path.json",
        help="Path to visualize (.json), path should correspond to some map file",
    )
    args = parser.parse_args()

    # Create cityMap and populate any relevant landmarks
    stanfordMapName = args.map_file.split("/")[-1].split("_")[0]
    stanfordCityMap = readMap(args.map_file)
    addLandmarks(stanfordCityMap, args.landmark_file)

    # (Optional) Read path to visualize from JSON file
    if args.path_file:
        with open(args.path_file) as f:
            data = json.load(f)
            parsedPath = data["path"]
            parsedWaypointTags = data["waypointTags"]
    else:
        parsedPath = []
        parsedWaypointTags = []

    # Run the visualization
    plotMap(
        cityMap=stanfordCityMap,
        path=parsedPath,
        waypointTags=parsedWaypointTags,
        mapName=stanfordMapName,
    )
