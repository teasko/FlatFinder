from datetime import datetime as _datetime
#import json as _json
#import random as _random
#import requests as _requests
#import time as _time
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup as _BeautifulSoup
from typing import List
import re
import crawler.db_handler as db

def scrape_interesting_flats_for_user(user_id:int) -> List[dict]:
    flatFilters = db.get_userFlatFilters(user_id)
   # possible sleep to have less consistent query intervals
    #_time.sleep(_random.randint(0, 60))
    # get info of relevant flats
    return _collect_relevant_flats_with_info(flatFilters)

def scrape_new_flats_for_user(user_id:int) -> List[dict]:
    interesting_flats = scrape_interesting_flats_for_user(user_id=user_id)
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

    return newFlats


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






    