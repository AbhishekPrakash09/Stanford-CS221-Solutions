# Route

The following sections detail some general notes for working with `route`, including setup, and
various dependency requirements.

## Prerequisites

Install the following dependencies (in a virtual environment, such as
 [miniconda](https://docs.conda.io/en/latest/miniconda.html#linux-installers)) for working with 
 [OpenStreetMap](https://www.openstreetmap.org/) (OSM) data, and visualizing maps nicely in the browser.

```bash
pip install -r requirements.txt
```

This command should work out of the box for all platforms (Linux, Mac OS, Windows).

## Creating a Custom Map

1. Use `extract.bbbike.org` to select a geographic region.
2. Download a `<name>.pbf` and place it in the `data` directory.

### Adding Custom Landmarks

Landmark files have the following format:

```json
[
  {"landmark": "gates", "geo": "37.4299865,-122.177815"},
  {"landmark": "bookstore", "geo": "37.4299866,-122.175519"},
  {"landmark": "oval", "geo": "37.4299862,-122.1843811"},
  {"landmark": "memorial_church", "geo": "37.4267088,-122.1749687"},
  {"landmark": "coupa_green_library", "amenity": "food", "geo": "37.426204,-122.1691837"},
  ...
]
```
See `data/stanford-landmarks.json` for an example. You can add your own to `data/custom-landmarks.json`.

To add a landmark, find it on [OpenStreetMap](https://www.openstreetmap.org/) via [nominatim](https://nominatim.openstreetmap.org/) and 
copy the `Center Point (lat,lon)` from the `nominatim` webpage 
(e.g., [Gates Building](https://nominatim.openstreetmap.org/ui/details.html?osmtype=W&osmid=232841885&class=building),
and set that to be the value of `"geo"`.

## Visualizing the Map

To visualize a particular map, you can use the following:

```bash
python visualization.py

# You can customize the map and the landmarks
python visualization.py --map-file data/stanford.pbf --landmark-file data/stanford-landmarks.json

# Visualize a particular solution path (requires running `grader.py` on question 1b/2b first!)
python visualization.py --path-file path.json
```
