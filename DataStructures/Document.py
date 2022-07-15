import sys
from DataStructures.Object import Object


class Document:

    def __init__(self):
        self.objects = list()
        self.map_objects = dict()
        self.p1 = None
        self.p2 = None
        self.t1 = None
        self.t2 = None

    def add_object(self, id_object):
        if id_object not in [obj.id for obj in self.objects]:
            o = Object(id=id_object)
            self.objects.append(o)
            self.map_objects[id_object] = o

    def get_object(self, id_object):
        return self.map_objects[id_object]

    def set_area(self, p1=(-sys.maxsize, -sys.maxsize), p2=(sys.maxsize, sys.maxsize)):
        self.p1 = p1
        self.p2 = p2

    def set_time_range(self, t1=0, t2=sys.maxsize):
        self.t1 = t1
        self.t2 = t2

    def get_all_routes(self):
        all_routes = []
        for o in self.objects:
            for r in o.routes:
                all_routes.append([o.id, r])
        return all_routes






