import numpy as np
import logging
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import heapq
import time


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Cul:
    def __init__(self, db_path='cul_data.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._setup_database()

    def _setup_database(self):
        self.cursor.execute('DROP TABLE IF EXISTS cul_data')
        self.cursor.execute('''
            CREATE TABLE cul_data (
                id INTEGER PRIMARY KEY,
                timestamp REAL,
                ship_name TEXT,
                metric TEXT,
                value REAL,
                pos_x REAL,
                pos_y REAL
            )
        ''')
        self.conn.commit()

    def log_data(self, ship_name, metric, value, pos=None):
        timestamp = time.time()
        pos_x, pos_y = pos if pos is not None else (None, None)
        self.cursor.execute(
            'INSERT INTO cul_data (timestamp, ship_name, metric, value, pos_x, pos_y) VALUES (?, ?, ?, ?, ?, ?)',
            (timestamp, ship_name, metric, value, pos_x, pos_y)
        )
        self.conn.commit()
        logger.info(f"{ship_name} {metric}={value:.2f} at pos=({pos_x},{pos_y})")

    def distance(self, pos1, pos2):
        return np.linalg.norm(np.array(pos2) - np.array(pos1))

    def close(self):
        self.conn.close()
        logger.info("Database closed.")

class Ship:
    def __init__(self, name, start_pos, cul_logger, speed=1.0):
        self.name = name
        self.pos = np.array(start_pos, dtype=float)
        self.speed = speed
        self.cul = cul_logger
        self.path = []
        self.target_index = 0
        self.target = None

    def set_path(self, path):
        if not path or len(path) < 2:
            return
        self.path = path
        self.target_index = 1
        self.target = np.array(self.path[self.target_index], dtype=float)
        self.cul.log_data(self.name, "route_enter", 0, pos=self.pos)
        logger.info(f"{self.name} path set: {self.path}, speed={self.speed}")

    def update(self):
        if self.target is None:
            return
        direction = self.target - self.pos
        dist_to_target = np.linalg.norm(direction)
        step = min(self.speed, dist_to_target)
        self.pos += (direction / dist_to_target) * step
        self.cul.log_data(self.name, "distance_traveled", step, pos=self.pos)

        if dist_to_target <= self.speed:
            self.cul.log_data(self.name, "route_exit", dist_to_target, pos=self.pos)
            logger.info(f"{self.name} reached {self.target}")
            self.target_index += 1
            if self.target_index < len(self.path):
                self.target = np.array(self.path[self.target_index], dtype=float)
                self.cul.log_data(self.name, "route_enter", 0, pos=self.pos)
            else:
                self.target = None


def fastest_path(graph, start, end, positions, ship_speed):
    queue = [(0, start, [start])] 
    visited = {}
    while queue:
        total_time, node, path = heapq.heappop(queue)
        if node == end:
            return path
        if node in visited and visited[node] <= total_time:
            continue
        visited[node] = total_time

        for neighbor in graph.get(node, []):
            dist = np.linalg.norm(np.array(positions[neighbor]) - np.array(positions[node]))
            travel_time = dist / ship_speed
            heapq.heappush(queue, (total_time + travel_time, neighbor, path + [neighbor]))

    return None

def input_planets():
    planets = {}
    n = int(input("Enter number of planets: "))
    for _ in range(n):
        name = input("Planet name: ")
        x = float(input(f"{name} X coordinate: "))
        y = float(input(f"{name} Y coordinate: "))
        planets[name] = (x, y)
    return planets

def input_routes(planets):
    routes = []
    print("Enter routes (type 'done' when finished):")
    while True:
        a = input("Start planet: ")
        if a.lower() == 'done':
            break
        b = input("End planet: ")
        if b.lower() == 'done':
            break
        if a in planets and b in planets:
            routes.append((a, b))
        else:
            print("Invalid planets. Try again.")
    return routes

def input_ships(planets):
    ships = []
    n = int(input("Enter number of ships: "))
    for _ in range(n):
        name = input("Ship name: ")
        start = input("Start planet: ")
        end = input("End planet: ")
        speed = float(input("Speed of ship: "))
        if start in planets:
            ships.append({'name': name, 'start': start, 'end': end, 'speed': speed})
        else:
            print(f"Invalid start planet for {name}, skipping.")
    return ships

def get_simulation_config():
    use_defaults = input("Use default setup? (y/n): ").lower() == 'y'

    if use_defaults:
        planets = {
            'Earth': (0, 0),
            'Mars': (100, 50),
            'Venus': (-50, 80),
        }
        routes = [('Earth', 'Mars'), ('Earth', 'Venus'), ('Venus', 'Mars')]
        ships = [
            {'name': 'Apollo', 'start': 'Earth', 'end': 'Mars', 'speed': 5},
            {'name': 'Odyssey', 'start': 'Venus', 'end': 'Mars', 'speed': 3},
        ]
    else:
        planets = input_planets()
        routes = input_routes(planets)
        ships = input_ships(planets)

    return planets, routes, ships


def main():
    cul_logger = Cul()

    planets, routes, ships_data = get_simulation_config()

    graph = {}
    for a, b in routes:
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, []).append(a)

    ships = []
    for s in ships_data:
        ship = Ship(s['name'], planets[s['start']], cul_logger, s['speed'])
        path = fastest_path(graph, s['start'], s['end'], planets, ship.speed)
        if path:
            ship.set_path([planets[p] for p in path])
            ships.append(ship)
        else:
            print(f"No path found for {s['name']} from {s['start']} to {s['end']}")

    
    fig, ax = plt.subplots()
    all_x = [x for x, y in planets.values()]
    all_y = [y for x, y in planets.values()]
    ax.set_xlim(min(all_x)-50, max(all_x)+50)
    ax.set_ylim(min(all_y)-50, max(all_y)+50)

    for name, (x, y) in planets.items():
        ax.plot(x, y, 'o', markersize=10)
        ax.text(x+2, y+2, name)

    for a, b in routes:
        x1, y1 = planets[a]
        x2, y2 = planets[b]
        ax.plot([x1, x2], [y1, y2], 'gray', linestyle='--')

    colors = ['red', 'blue', 'green', 'orange', 'purple']
    markers = [ax.plot(ship.pos[0], ship.pos[1], 's', color=colors[i % len(colors)], markersize=8)[0]
               for i, ship in enumerate(ships)]

    def animate(frame):
        all_done = True
        for ship, marker in zip(ships, markers):
            ship.update()
            marker.set_data([ship.pos[0]], [ship.pos[1]])
            if ship.target is not None:
                all_done = False
        if all_done:
            ani.event_source.stop()
        return markers

    ani = FuncAnimation(fig, animate, frames=1000, interval=50, blit=True)
    ani.save('simulation.gif', writer='pillow', fps=20)

    cul_logger.close()

if __name__ == "__main__":
    main()
