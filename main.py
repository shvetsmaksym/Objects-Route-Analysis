import json

from DataStructures import *


def process_json(filepath):
    with open(filepath, 'r') as js_file:
        route_data = json.load(js_file)

    doc = Document()
    for record in route_data:
        doc.add_object(id_object=record['idObject'])
        o = doc.get_object(id_object=record['idObject'])

        o.add_route(id_route=record['idPath'])
        r = o.get_route(id_route=record['idPath'])
        r.set_points(record['points'])

    return doc


if __name__ == "__main__":
    document = process_json('paths2.json')
    all_routes = document.get_all_routes()
    p1, p2, t1, t2 = (50, 380), (100, 400), 890, 905

    for route in all_routes:
        route.append(route[1].check_for_enter_to_area(p1, p2, t1, t2))

    all_routes = [[r[0], r[1].id, r[2]] for r in all_routes if r[2] != (None, None)]
    print(all_routes)




