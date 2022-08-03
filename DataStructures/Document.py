import multiprocessing as mp
import os
import json
import pandas as pd
import numpy as np
from random import random
from itertools import combinations
import matplotlib.pyplot as plt
from tqdm import tqdm

from logger import timer_func
from Constants import *


class Document:

    def __init__(self, filepath=None):
        self.time_range = None
        self.p1 = None
        self.p2 = None

        base_file_name = filepath.split('/')[-1].split('\\')[-1].rstrip('.json')
        self.doc_path = os.path.join(TMP_PATH, base_file_name)
        self.split_js_path = os.path.join(self.doc_path, SPLIT_JSONS)
        self.result_path = os.path.join(self.doc_path, RESULTS_PATH)
        self.plot_path = os.path.join(self.doc_path, PLOT_PATH)
        if not os.path.exists(self.doc_path):
            os.mkdir(self.doc_path)

    def set_criteria(self, time_range, p1, p2):
        """
        Method used to set criteria such as time range and rectangle area to looking for when analysing object's route.
        :param time_range: float >= 0
        :param p1: (x1, y1) - bottom left point of rectangle area
        :param p2: (x2, y2) - top right point of rectangle area
        """
        self.time_range = time_range
        self.p1 = p1
        self.p2 = p2

    # ---- NEXT TWO METHODS SPLIT INPUT JSON FILE INTO SMALLER JSON FILES FOR EACH ROUTE ----
    @timer_func
    def split_input_json_data(self, json_data, multiprocessing=False):
        """
        Method splits input json file into smaller json files each corresponding to exact one route.
        Saves split files into temp folder.
        :param multiprocessing: True / False
        """
        if not os.path.exists(self.split_js_path):
            os.mkdir(self.split_js_path)

        if multiprocessing:
            with mp.Pool(processes=mp.cpu_count()) as p:
                  p.map(self.save_to_json, json_data)
        else:
            for record in tqdm(json_data):
                self.save_to_json(record)

    def save_to_json(self, record):
        """Save one route to a new json file."""
        file_path = os.path.join(self.split_js_path, f"Object_{record['idObject']}_path_{record['idPath']}.json")
        with open(file_path, 'w') as file:
            json_formatted = json.dumps(record, ensure_ascii=True)
            file.write(json_formatted)

    # ---- NEXT TWO METHODS CHECK EACH ROUTE FOR PASSING THE RECTANGLE AREA IN THE GIVEN TIME RANGE AND UPDATE ----
    # ---- JSON FILES CORRESPONDING TO EACH ROUTE WITH THIS INFORMATION ----
    @timer_func
    def update_routes_with_entries_exists_info(self, multiprocessing=False):
        """
        Method process each route to find enters and exits from the rectangle area and update json files corresponding
        to each route with this information.
        :param multiprocessing: True / False
        """
        paths = iter([os.path.join(self.split_js_path, fname) for fname in os.listdir(self.split_js_path)])
        if multiprocessing:
            with mp.Pool(processes=mp.cpu_count()) as p:
                p.map(self.check_for_entries_and_exits, paths)
        else:
            for p in tqdm(paths):
                self.check_for_entries_and_exits(p)

    def check_for_entries_and_exits(self, json_path):
        """
        Method checks for entries and exits for a single route
        :param json_path: path to json file containing route's data
        """
        with open(json_path, 'r') as file:
            route_data = json.load(file)

        points = self.get_points(route_data['points'])

        df = pd.DataFrame(points, columns=["X", "Y", "Time"])
        df_bool = (df['X'] >= self.p1[0]) & (df['X'] <= self.p2[0]) & \
                  (df['Y'] >= self.p1[1]) & (df['Y'] <= self.p2[1]) & \
                     (df['Time'] >= self.time_range[0]) & (df['Time'] <= self.time_range[1])
        entries = (df_bool.shift(1) == False) & (df_bool == True)
        exits = (df_bool.shift(1) == True) & (df_bool == False)

        entries = list(df['Time'][entries])
        exits = list(df['Time'][exits])

        if abs(len(entries) - len(exits)) > 1:
            raise ValueError("Absolute value of len(entries) - len(exits) can't be greater than 1.")

        # Update input json file with entries/exits data
        if len(entries) < len(exits):
            entries.insert(0, None)
        elif len(exits) < len(entries):
            exits.append(None)
        elif len(exits) == len(entries) != 0 and exits[0] < entries[0]:
            entries.insert(0, None)
            exits.append(None)
        res = [[n, x] for n, x in zip(entries, exits)]

        if res:
            route_data["EntriesExits"] = res
            json_formatted = json.dumps(route_data, ensure_ascii=True)
            with open(json_path, 'w') as file:
                file.write(json_formatted)

    # ---- NEXT THREE METHODS COLLECT INFORMATION ABOUT PASSING RECTANGLE AREA IN GIVEN TIME RANGE BY EVERY OBJECT ----
    # ---- AND EVERY ROUTE ----
    @timer_func
    def get_results(self, multiprocessing=False):
        """
        Method looks for every json in split jsons, collect information about entries and exits, and write it to self.result_path
        :param multiprocessing: True / False
        """
        paths = iter([os.path.join(self.split_js_path, fname) for fname in os.listdir(self.split_js_path)])

        if not multiprocessing:
            for path in tqdm(paths):
                with open(path, 'r') as file:
                    route_data = json.load(file)
                if 'EntriesExits' in route_data:
                    res = f"object: {route_data['idObject']}, path: {route_data['idPath']}," \
                          f" crossing area times: {route_data['EntriesExits']}"

                    with open(self.result_path, 'a') as f:
                        f.write(str(res) + '\n')

        else:
            """This solution was taken from StackOverflow:
            https://stackoverflow.com/questions/13446445/python-multiprocessing-safely-writing-to-a-file"""
            manager = mp.Manager()
            q = manager.Queue()
            pool = mp.Pool(processes=mp.cpu_count())

            # put listener to work first
            pool.apply_async(self.queue_listener, (q,))

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
        """
        Method collects information about entries and exits from given path and put it to the queue.
        :param path: path to json with route data
        :param q: queue
        """
        with open(path, 'r') as file:
            route_data = json.load(file)

        if 'EntriesExits' in route_data:
            res = f"object: {route_data['idObject']}, path: {route_data['idPath']}," \
                          f" crossing area times: {route_data['EntriesExits']}"
            q.put(res)
            return res

    def queue_listener(self, q):
        """
        Method listens messages from the queue and write them into self.result_path file.
        :param q: queue
        """
        with open(self.result_path, 'w') as f:
            while 1:
                m = q.get()
                if m == 'kill':
                    break
                f.write(str(m) + '\n')
                f.flush()

    # ---- OTHER METHODS ----
    @staticmethod
    def get_points(points):
        """INPUT:
        - points: dict extracted from expected input json file."""

        x = np.array([points[i]['x'] for i in range(len(points))])
        y = np.array([points[i]['y'] for i in range(len(points))])
        t = np.array([points[i]['time'] for i in range(len(points))])

        return np.array([(x1, y1, t1) for x1, y1, t1 in zip(x, y, t)])

    @timer_func
    def plot_routes(self):
        if len(os.listdir(self.split_js_path)) > 30:
            list_paths = combinations(os.listdir(self.split_js_path), 30)
        else:
            list_paths = os.listdir(self.split_js_path)

        for route in list_paths:
            self.plot_one_route(route)

        plt.savefig(self.plot_path)

    def plot_one_route(self, route_path):
        with open(os.path.join(self.split_js_path, route_path), 'r') as file:
            route_data = json.load(file)
            points = Document.get_points(route_data['points'])
            plt.plot(points[:, 0], points[:, 1], color=[random() * .75, random() * .60, random() * .80])






