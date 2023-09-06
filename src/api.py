from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import db_handler as db

# from helper_functions import row2dict


class User(BaseModel):
    email: str
    active: bool = False


class UserFlatFilters(BaseModel):
    minNumberRooms: int
    maxNumberRooms: int
    minFlatSize: int
    maxFlatSize: int
    maxPrice: int
    wbsVorhanden: bool = False


app = FastAPI()


@app.get("/users")
def get_users():
    users = db.get_users()
    return {"users": users}


@app.post("/users")
def add_user(user: User):
    user_id = db.create_user(email=user.email, active=user.active)
    return {"user_id": user_id}


@app.get("/users/{user_id}/flatfilters")
def get_user_filters_for_id(user_id: int) -> UserFlatFilters:
    if db.check_user_exists(user_id):
        db_filters = db.get_userFlatFilters(user_id=user_id)
        if db_filters:
            return UserFlatFilters(
                minNumberRooms=db_filters.minNumberRooms,
                maxNumberRooms=db_filters.maxNumberRooms,
                minFlatSize=db_filters.minFlatSize,
                maxFlatSize=db_filters.maxFlatSize,
                maxPrice=db_filters.maxPrice,
                wbsVorhanden=db_filters.wbsVorhanden,
            )
        else:
            raise HTTPException(
                status_code=404, detail=f"No flat filters for user with id {user_id}"
            )
    else:
        raise HTTPException(
            status_code=404, detail=f"User with user_id {user_id} does not exist"
        )


@app.post("/users/{user_id}/flatfilters")
def set_user_filters_for_id(user_id: int, flatfiters: UserFlatFilters):
    if db.check_user_exists(user_id):
        db.set_userFlatFilters(user_id=user_id, flat_filters=flatfiters.dict())
    else:
        raise HTTPException(
            status_code=404, detail=f"User with user_id {user_id} does not exist"
        )


@app.get("/users/{user_id}/polygons")
def get_user_polygons_for_id(user_id: int) -> dict:
    if db.check_user_exists(user_id):
        poly = db.get_polygon(user_id=user_id)
        if poly:
            return poly
        else:
            raise HTTPException(
                status_code=404, detail=f"No polygons for user with id {user_id}"
            )

    else:
        raise HTTPException(
            status_code=404, detail=f"User with user_id {user_id} does not exist"
        )


@app.post("/users/{user_id}/polygons")
def set_user_polygons_for_id(user_id: int, geojson: dict):
    if db.check_user_exists(user_id):
        # extract polygon list from geojson
        polygons = geojson

        db.set_polygon(user_id=user_id, polygons=polygons)
    else:
        raise HTTPException(
            status_code=404, detail=f"User with user_id {user_id} does not exist"
        )
