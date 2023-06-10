# ToDo put Config loading somewhere else

import requests
from math import radians, cos, acos
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from typing import List
import json

def _getCoordinatesFromAddress(address:str) -> Point:
    base_url =   "https://nominatim.openstreetmap.org/search?q="
    address_url = address.replace(",","+")
    request_url = base_url + address_url + "&format=json"
    
    r = requests.get(request_url)
    if r.status_code == 200:
        r = r.json()
        if len(r) > 0:
            entry = -1
            for i in range(len(r)):
                if ("type" in r[i].keys()) and ("lat" in r[i].keys()) and ("lon" in r[i].keys()):
                    if (len(r[i]["lat"])>0) and (len(r[i]["lon"])>0):
                        if (r[i]["type"] == "house") or (entry < 0):
                            entry=i
                            break

            if entry >=0:
                return Point(float(r[entry]["lon"]),float(r[entry]["lat"]))
            else:
                raise ValueError("no lat/lon values for address")
        else:
            raise ValueError("address not found")
    else:
        raise ConnectionError(r.reason)


def _getCoordinateDistance(x1,x2,r=6371):
    (lat1, lon1) = x1
    (lat2, lon2) = x2

    # Convert degrees to radians
    coordinates = lat1, lon1, lat2, lon2
    phi1, lambda1, phi2, lambda2 = [
        radians(c) for c in coordinates
    ]
    
    # Apply the haversine formula
    d = r*acos(cos(phi2-phi1) - cos(phi1) * cos(phi2) *
              (1-cos(lambda2-lambda1)))
    return d


def _createPolygons(file_path:str) -> List[Polygon]:
    with open(file_path, 'r') as f:
        geojason = json.load(f)
    
    polygon_list = []
    for feature in geojason["features"]:
        if feature["geometry"]['type'] == "Polygon":
            for polygon in feature["geometry"]['coordinates']:
                polygon_list.append(Polygon(polygon))


    return polygon_list


def _checkCoordinatesInPolygons(polygons:List[Polygon], coordinates: Point) -> bool:
    is_contained = False
    for polygon in polygons:
        if polygon.contains(coordinates):
            is_contained = True
            break
    return is_contained


def _checkAddressInPolygons(address:str,polygon_path)->bool:
    coords = _getCoordinatesFromAddress(address)
    polygons = _createPolygons(polygon_path)
    return _checkCoordinatesInPolygons(polygons,coords)


def filter_flats_by_location(flats:List[dict],path_polygons) -> List[dict]:
    res = []
    for flat in flats:
        if 'Adresse' in flat.keys():
            addr = flat['Adresse']
            try:
                if _checkAddressInPolygons(addr,path_polygons):
                    res.append(flat)
            except:
                pass
    return res