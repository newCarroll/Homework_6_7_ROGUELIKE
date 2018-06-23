import libtcodpy as libtcod

class Tile:
    # a tile of the map and its properties
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        # all tiles start unexplored
        self.explored = False

        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight


class Rect:
    # a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Map:
    def __init__(self, map_height, map_width):
        self.room_min_size = 6
        self.room_max_size = 10
        self.max_rooms = 15
        self.tiles = [[Tile(True)
                      for y in range(map_height)]
                      for x in range(map_width)]
        self.rooms = []
        self.num_rooms = 0

        self.start_x = 0
        self.start_y = 0
        self.width = map_width
        self.height = map_height
        self.fov_map = libtcod.map_new(self.width, self.height)
        self.fov_recompute = True
        self.con = libtcod.console_new(self.width, self.height)

        self.create_rooms()
        self.initialize_fov()

    def create_rooms(self):
        for r in range(self.max_rooms):
            # random width and height
            w = libtcod.random_get_int(0, self.room_min_size, self.room_max_size)
            h = libtcod.random_get_int(0, self.room_min_size, self.room_max_size)
            x = libtcod.random_get_int(0, 0, self.width - w - 1)
            y = libtcod.random_get_int(0, 0, self.height - h - 1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # run through the other rooms and see if they intersect with this one
            failed = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                self.create_room(new_room)

                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()
                self.gate_x, self.gate_y = new_x, new_y

                if self.num_rooms == 0:
                    # this is the first room, where the player starts at
                    self.start_x = new_x
                    self.start_y = new_y
                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = self.rooms[self.num_rooms - 1].center()

                    # draw a coin (random number that is either 0 or 1)
                    if libtcod.random_get_int(0, 0, 1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.rooms.append(new_room)
                self.num_rooms += 1

    def initialize_fov(self):
        for y in range(self.height):
            for x in range(self.width):
                libtcod.map_set_properties(self.fov_map, x, y, not self.tiles[x][y].block_sight,
                                           not self.tiles[x][y].blocked)

        libtcod.console_clear(self.con)

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False


    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def is_blocked(self, x, y):
        return self.tiles[x][y].blocked