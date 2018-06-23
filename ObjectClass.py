import libtcodpy as libtcod


class Object:
    # this is a generic object: the player, a monster, an item, the stairs...
    # it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, objects=[], logger=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.always_visible = always_visible
        self.stopped = False
        self.objects = objects
        self.logger = logger

    def send_to_back(self):
        # make this object be drawn first, so all others appear above it if they're in the same tile.
        self.objects.remove(self)
        self.objects.insert(0, self)

    def draw(self, map):
        # only show if it's visible to the player; or it's set to "always visible" and on an explored tile
        if (libtcod.map_is_in_fov(map.fov_map, self.x, self.y) or
                (self.always_visible and map.tiles[self.x][self.y].explored)):
            libtcod.console_set_default_foreground(map.con, self.color)
            libtcod.console_put_char(map.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self, map):
        # erase the character that represents this object
        libtcod.console_put_char(map.con, self.x, self.y, ' ', libtcod.BKGND_NONE)
        self.send_to_back()