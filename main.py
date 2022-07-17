import json

from DataStructures import *


def process_json(filepath):
    with open(filepath, 'r') as js_file:
        json_routes_data = json.load(js_file)

    doc = Document()
    doc.split_routes(json_routes_data, multiprocessing=False)

    return doc


if __name__ == "__main__":
    document = process_json('paths2.json')
    print("Split input json file.")

    p1, p2, time_range = (90, 400), (100, 405), (800, 905)
    document.set_criteria(time_range, p1, p2)
    print("Set time range and rectangle to looking for.\n" + 50 * "-")

    document.update_routes_with_entries_exists_info(multiprocessing=False)

    print(50 * "-", "\nUpdate routes with entries and exists information.")

    document.get_results()
    print("Write all routes' entries and exits into results.txt.")





