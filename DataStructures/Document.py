import multiprocessing as mp
import os
import json
import pandas as pd
import numpy as np
from random import random
import matplotlib.pyplot as plt


if not os.path.exists('temp'):
    os.mkdir('temp')

RESULTS_PATH = os.path.join('temp', 'results.txt')
SPLIT_JSONS_PATH = os.path.join('temp', 'split_jsons')


class Document:

    def __init__(self):
        self.time_range = None
        self.p1 = None
        self.p2 = None

    @staticmethod
    def split_routes(json_data, multiprocessing=False):
        """
        Method splits input json file into smaller json files each containing only one route.
        Saves split files into temp folder.
        """
        if not os.path.exists(SPLIT_JSONS_PATH):
            os.mkdir(SPLIT_JSONS_PATH)

        if multiprocessing:
            with mp.Pool(processes=mp.cpu_count()) as p:
                  p.map(Document.save_to_json, json_data)
        else:
            for record in json_data:
                Document.save_to_json(record)

    @staticmethod
    def save_to_json(record):
        file_path = os.path.join(SPLIT_JSONS_PATH, f"Object_{record['idObject']}_path_{record['idPath']}.json")
        with open(file_path, 'w') as file:
            json_formatted = json.dumps(record, ensure_ascii=True)
            file.write(json_formatted)

    # --------------------------------------
    def set_criteria(self, time_range, p1, p2):
        self.time_range = time_range
        self.p1 = p1
        self.p2 = p2

    def update_routes_with_entries_exists_info(self, multiprocessing=False):
        paths = iter([os.path.join(SPLIT_JSONS_PATH, fname) for fname in os.listdir(SPLIT_JSONS_PATH)])
        if multiprocessing:
            with mp.Pool(processes=mp.cpu_count()) as p:
                p.map(self.check_for_entries_and_exits, paths)
        else:
            for p in paths:
                self.check_for_entries_and_exits(p)

    def check_for_entries_and_exits(self, json_path):
        with open(json_path, 'r') as file:
            route_data = json.load(file)

        points = self.get_points(route_data['points'])

        df = pd.DataFrame(points, columns=["X", "Y", "Time"])
        df_bool = (df['X'] >= self.p1[0]) & (df['X'] <= self.p2[0]) & \
                  (df['Y'] >= self.p1[1]) & (df['Y'] <= self.p2[1]) & \
                     (df['Time'] >= self.time_range[0]) & (df['Time'] <= self.time_range[1])
        entries = (df_bool.shift(1) == False) & (df_bool == True)
        exits = (df_bool.shift(1) == True) & (df_bool == False)

        passed_condition = False
        if entries.any():
            route_data['Entries'] = list(df['Time'][entries])
            passed_condition = True
        if exits.any():
            route_data['Exits'] = list(df['Time'][exits])
            passed_condition = True

        if passed_condition:
            print(f"object: {route_data['idObject']}, path: {route_data['idPath']},"
                  f" entries: {list(df['Time'][entries])}), exits: {list(df['Time'][exits])}")
            json_formatted = json.dumps(route_data, ensure_ascii=True)
            with open(json_path, 'w') as file:
                file.write(json_formatted)

    # --------------------------------------
    @staticmethod
    def get_results():
        """Below solution was gotten from StackOverflow:
        https://stackoverflow.com/questions/13446445/python-multiprocessing-safely-writing-to-a-file"""

        paths = iter([os.path.join(SPLIT_JSONS_PATH, fname) for fname in os.listdir(SPLIT_JSONS_PATH)])
        manager = mp.Manager()
        q = manager.Queue()
        pool = mp.Pool(processes=mp.cpu_count())

        # put listener to work first
        watcher = pool.apply_async(Document.queue_listener, (q,))

        jobs = []
        for path in paths:
            job = pool.apply_async(Document.collect_entries_exits, (path, q))
            jobs.append(job)

        # collect results from the workers through the pool result queue
        for job in jobs:
            job.get()

        # now we are done, kill the listener
        q.put('kill')
        pool.close()
        pool.join()

    @staticmethod
    def collect_entries_exits(path, q):
        with open(path, 'r') as file:
            route_data = json.load(file)

        if 'Entries' in route_data and 'Exits' in route_data:
            res = f"object: {route_data['idObject']}, path: {route_data['idPath']}," \
                  f" entries: {route_data['Entries']}), exits: {route_data['Exits']}"
            q.put(res)
            return res

    @staticmethod
    def queue_listener(q):
        with open(RESULTS_PATH, 'w') as f:
            while 1:
                m = q.get()
                if m == 'kill':
                    break
                f.write(str(m) + '\n')
                f.flush()

    # --------------------------------------
    @staticmethod
    def get_points(points):
        """INPUT:
        - points: dict retained from json file."""

        x = np.array([points[i]['x'] for i in range(len(points))])
        y = np.array([points[i]['y'] for i in range(len(points))])
        t = np.array([points[i]['time'] for i in range(len(points))])

        return np.array([(x1, y1, t1) for x1, y1, t1 in zip(x, y, t)])

    @staticmethod
    def plot_routes():
        for route in os.listdir('temp/'):
            with open(os.path.join("temp", route), 'r') as file:
                route_data = json.load(file)
                points = Document.get_points(route_data['points'])
                plt.plot(points[:, 0], points[:, 1], color=[random() * .90, random() * .90, random()])

        plt.show()






