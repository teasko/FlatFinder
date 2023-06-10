from datetime import datetime as _datetime
import requests
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from typing import List
import json

import urllib.parse
import urllib.request
from bs4 import BeautifulSoup as _BeautifulSoup
import re
import crawler.db_handler as db


def scrape_new_flats_for_user(user_id:int) -> List[dict]:
    interesting_flats = _scrape_interesting_flats_for_user(user_id=user_id)
    known_flat_ids = db.get_known_flat_ids(user_id=user_id)
    newFlats = []
    interesting_flat_ids=[]
    for flat in interesting_flats:
        if 'id' in flat.keys():
            id = flat['id']
            interesting_flat_ids.append(id)
            if not (id in known_flat_ids):
                newFlats.append(flat)
    
    db.replace_known_flats(user_id,interesting_flat_ids)
    _filter_flats_by_location(newFlats,path_polygons)


    return newFlats


def _scrape_interesting_flats_for_user(user_id:int) -> List[dict]:
    flatFilters = db.get_userFlatFilters(user_id)
   # possible sleep to have less consistent query intervals
    #_time.sleep(_random.randint(0, 60))
    # get info of relevant flats
    return _collect_relevant_flats_with_info(flatFilters)


def _collect_relevant_flats_with_info(flatFilters:db.UserFlatFilters) -> List[dict]:

    # scrape flat listings 
    base_url = 'https://inberlinwohnen.de'
    wohnungsfinder_url = base_url + '/wohnungsfinder/'
    
    response = urllib.request.urlopen(wohnungsfinder_url).read()
    html_soup = _BeautifulSoup(response, "lxml")

    # all flats
    flats = html_soup.find_all('li', class_ = 'tb-merkflat ipg')
    
    interesting_flats = []
    new_flat_ids = []

    for flat in flats:
        # retrieve information
        info_table = flat.find('table', class_ = 'tb-small-data fullw')
        info_parameters = list(map(_clean_info_parameters, info_table.find_all('th')))
        info_values = list(map(lambda x: x.string, info_table.find_all('td')))
        flat_info = dict(zip(info_parameters, info_values))

        flat_info['id'] = flat['id']
        # extract price from header
        header = flat.find_all('span', class_ = "_tb_left")
        if len(header)>0:
            header=str(header[0])
            
            flat_info["Preis in €"] = _extract_price_from_header(header)
        # create direct link to offer
        links = flat.find_all('a', class_ = 'org-but')
        url_parts = links[0]['href'].split('/')
        flat_info['url'] = base_url + '/'.join(
            [urllib.parse.quote_plus(url_part) for url_part in url_parts]
        )
        
        if _flat_satisfies_filters(flat_info,flatFilters):                
            # add flat to list for mail
            interesting_flats.append(flat_info)
        
    return interesting_flats
    
   
def _clean_info_parameters(paramerter_string):
    try:
        return paramerter_string.string[:-2]
    except:
        return 'WBS'
    
    
def _extract_price_from_header(header:str)->float:
    header_list = header.replace('<span class="_tb_left">','').replace('<strong>','').replace('</strong>','').replace('</span>','').replace(".","")
    header_list = header_list.split(',')
    euro_index = 0
    run_index = 0
    for le in list(map(lambda xvar: xvar.__contains__("€"),header_list)):
        if le:
            euro_index = run_index
            break
        else:
            run_index += 1

    if euro_index > 0:
        return header_list[euro_index-1]


def _flat_satisfies_filters(flat_info:dict, flatFilters:db.UserFlatFilters) -> bool:
    
    all_satisfied = True

    if flatFilters.minNumberRooms and 'Zimmeranzahl' in flat_info.keys():
        zimmerzahl = float(flat_info['Zimmeranzahl'].replace('.','').replace(',','.'))
        if flatFilters.minNumberRooms > zimmerzahl:
            all_satisfied = False
        if flatFilters.maxNumberRooms:
            if flatFilters.maxNumberRooms < zimmerzahl:
                all_satisfied = False
    
    if flatFilters.maxPrice and 'Preis in €' in flat_info.keys():
        if flat_info['Preis in €']:
            preis = float(str(flat_info['Preis in €']).replace('.','').replace(',','.'))
            if flatFilters.maxPrice  < preis:
                all_satisfied = False

    if flatFilters.minFlatSize and 'Wohnfläche' in flat_info.keys():
        flaeche = flat_info['Wohnfläche'].replace('.','').replace(',','.')
        flaeche = float("".join(re.findall(r'\d+\.\d+',flaeche)).strip())
        if flatFilters.minFlatSize > flaeche:
            all_satisfied = False
        if flatFilters.maxFlatSize:
            if flatFilters.maxFlatSize < flaeche:
                all_satisfied = False

    if 'WBS' in flat_info.keys():
        if not flatFilters.wbsVorhanden:
            all_satisfied = False  

    return all_satisfied


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


def _filter_flats_by_location(flats:List[dict],path_polygons) -> List[dict]:
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
