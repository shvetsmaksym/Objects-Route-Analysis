from DataStructures.Route import Route


class Object:

    def __init__(self, id):
        self.id = id
        self.routes = list()
        self.map_routes = dict()

    def add_route(self, id_route):
        if id_route not in [r.id for r in self.routes]:
            r = Route(id=id_route)
            self.routes.append(r)
            self.map_routes[id_route] = r

    def get_route(self, id_route):
        return self.map_routes[id_route]


