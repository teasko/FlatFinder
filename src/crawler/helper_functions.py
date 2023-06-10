from typing import List

def _prettify_flat_dict(flat: dict) -> str:
    pretty_string = ''
    for key in flat:
        pretty_string += key + ': ' + str(flat[key]) + '\n'
    return pretty_string

def prettify_list_of_flats(flats: List[dict])-> str:
    if len(flats) > 0:
        pretty_string = 'CHECK OUT:\n\n'
        for flat in flats:
            pretty_string += _prettify_flat_dict(flat) + '\n'
        # print info >> will be send as email
        return pretty_string

def rows2dict(rows):
    res = []
    for row in rows:
        d = {}
        for column in row.__table__.columns:
            d[column.name] = str(getattr(row, column.name))

    res.append(d)
    return res

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d
