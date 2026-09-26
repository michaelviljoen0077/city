from neurotraffic.core.config import Config
from neurotraffic.core.simulation import World
from neurotraffic.vehicles.pathfinder import Pathfinder
from neurotraffic.vehicles.route import Route
from neurotraffic.world.traffic_light import TrafficLight


def make_world():
    world = World()
    world.build()
    return world


def run(world, seconds):
    for _ in range(int(seconds / Config.SIM_TIMESTEP)):
        world.update(Config.SIM_TIMESTEP)


def test_grid_layout():
    world = make_world()
    cm = world.city_map
    n = Config.GRID_COLS * Config.GRID_ROWS
    assert len(cm.nodes) == n
    # Two directed roads per adjacent pair
    pairs = Config.GRID_ROWS * (Config.GRID_COLS - 1) + Config.GRID_COLS * (Config.GRID_ROWS - 1)
    assert len(cm.roads) == 2 * pairs
    # Lights on every 3+ way intersection, i.e. everything but the corners
    assert len(cm.get_traffic_lights()) == n - 4


def test_pathfinder_finds_shortest_route():
    world = make_world()
    cm = world.city_map
    path = Pathfinder().find_route(cm, 0, Config.GRID_COLS * Config.GRID_ROWS - 1)
    assert path[0] == 0 and path[-1] == len(cm.nodes) - 1
    # Manhattan distance in hops on a grid
    assert len(path) - 1 == (Config.GRID_COLS - 1) + (Config.GRID_ROWS - 1)
    route = Route(path, cm)
    assert len(route.road_segments) == len(path) - 1


def test_traffic_light_cycle_and_signals():
    world = make_world()
    tl = world.city_map.get_traffic_lights()[0]
    assert tl.state_for("N") == "green" and tl.state_for("E") == "red"

    tl.update(world, Config.DEFAULT_PHASE_TIME)
    assert tl.phase == "ALL_RED_1"
    # Only the approach that just had green gets yellow
    assert tl.state_for("N") == "yellow" and tl.state_for("S") == "yellow"
    assert tl.state_for("E") == "red" and tl.state_for("W") == "red"

    tl.update(world, TrafficLight.ALL_RED_DURATION)
    assert tl.phase == "EW_GREEN" and tl.is_green_for("E")
    assert tl.switch_count == 1

    tl.reset()
    assert tl.phase == "NS_GREEN" and tl.switch_count == 0


def test_cars_complete_trips_without_overlapping():
    world = make_world()
    for _ in range(int(60 / Config.SIM_TIMESTEP)):
        world.update(Config.SIM_TIMESTEP)
        for road in world.city_map.roads:
            positions = sorted(v.position_on_road for v in road.vehicles)
            for a, b in zip(positions, positions[1:]):
                assert b - a >= Config.CAR_LENGTH, f"cars overlap on road {road.id}"
    m = world.metrics
    assert m.cars_spawned > 0
    assert m.cars_completed > 0
    assert m.cars_completed + len(world.vehicles) == m.cars_spawned


def test_reset_clears_state():
    world = make_world()
    run(world, 20)
    world.reset()
    assert world.vehicles == []
    assert all(not road.vehicles for road in world.city_map.roads)
    assert world.metrics.cars_spawned == 0
    assert all(tl.phase == "NS_GREEN" for tl in world.city_map.get_traffic_lights())
