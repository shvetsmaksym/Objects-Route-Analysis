import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Route:

    def __init__(self, id):
        self.id = id
        self.points = None

    def set_points(self, points):
        """INPUT:
        - points: dict retained from json file."""

        x = np.array([points[i]['x'] for i in range(len(points))])
        y = np.array([points[i]['y'] for i in range(len(points))])
        t = np.array([points[i]['time'] for i in range(len(points))])

        self.points = np.array([(x1, y1, t1) for x1, y1, t1 in zip(x, y, t)])

    def check_for_enter_to_area(self, p1, p2, t1, t2):
        df = pd.DataFrame(self.points, columns=["X", "Y", "Time"])
        df_bool = (df['X'] >= p1[0]) & (df['X'] <= p2[0]) & \
                  (df['Y'] >= p1[1]) & (df['Y'] <= p2[1]) & \
                     (df['Time'] >= t1) & (df['Time'] <= t2)
        entries = (df_bool.shift(1) == False) & (df_bool == True)
        exits = (df_bool.shift(1) == True) & (df_bool == False)

        if entries.any():
            entries = list(df['Time'][entries])
        else:
            entries = None
        if exits.any():
            exits = list(df['Time'][exits])
        else:
            exits = None

        return entries, exits

    def plot_route(self):
        plt.plot(self.points[:, 0], self.points[:, 1])
        plt.title(f"Route {self.id}")
        plt.show()
