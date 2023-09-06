import json

from dotenv import load_dotenv

import db_handler as db

# from flat_finder import scrape_new_flats_for_user
# from helper_functions import row2dict

load_dotenv()

if __name__ == "__main__":
    db.create_base()

    # user details

    print()
    print("##### Input User details for new user #####")
    email = input("Enter email address: ")

    user_id = db.create_user(email)
    print(f"user with created successfully. user id is {user_id}")

    print("")
    print("##### Flat search details #####")
    # user needs
    minNumberRooms = 0
    maxNumberRooms = 0
    minFlatSize = 0
    maxFlatSize = 0
    maxPrice = 0
    wbsVorhanden = False

    # User Input
    valid_input = 0
    while valid_input == 0:
        minNumberRooms_str = input("Enter min number of rooms: ")
        try:
            minNumberRooms = int(minNumberRooms_str)
            valid_input = 1
        except ValueError:
            print("not a valid int")

    valid_input = 0
    while valid_input == 0:
        maxNumberRooms_str = input("Enter max number of rooms: ")
        try:
            maxNumberRooms = int(maxNumberRooms_str)
            valid_input = 1
        except ValueError:
            print("not a valid int")

    valid_input = 0
    while valid_input == 0:
        minFlatSize_str = input("Enter min flat size: ")
        try:
            minFlatSize = int(minFlatSize_str)
            valid_input = 1
        except ValueError:
            print("not a valid int")

    valid_input = 0
    while valid_input == 0:
        maxFlatSize_str = input("Enter max flat size: ")
        try:
            maxFlatSize = int(maxFlatSize_str)
            valid_input = 1
        except ValueError:
            print("not a valid int")

    valid_input = 0
    while valid_input == 0:
        maxPrice_str = input("Enter max max price: ")
        try:
            maxPrice = int(maxPrice_str)
            valid_input = 1
        except ValueError:
            print("not a valid int")

    valid_input = 0
    while valid_input == 0:
        wbsVorhanden_str = input("WBS vorhanden? n/y: ")
        if wbsVorhanden_str.lower() == "n":
            wbsVorhanden = False
            valid_input = 1
        elif wbsVorhanden_str.lower() == "y":
            wbsVorhanden = True
            valid_input = 1
        else:
            print("not a valid answer")

    flatFilters = {
        "minNumberRooms": minNumberRooms,
        "maxNumberRooms": maxNumberRooms,
        "minFlatSize": minFlatSize,
        "maxFlatSize": maxFlatSize,
        "maxPrice": maxPrice,
        "wbsVorhanden": wbsVorhanden,
    }

    db.set_userFlatFilters(user_id=user_id, flat_filters=flatFilters)
    print("user search filters added successfully")

    print("")
    print("##### Geojson with polygon for search area #####")
    path_to_geo = input("enter full path to geojson: ")
    try:
        with open(path_to_geo, "r") as f:
            geojason = json.load(f)
            db.set_polygon(user_id, geojason)
    except Exception as e:
        print("Error occured: ")
        print(e)
