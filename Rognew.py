import random
from MapClass import Map as Map
from ItemClass import *
from LoggerClass import *
from FighterClass import *
from ObjectClass import *


FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
BAR_WIDTH = 20
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
PANEL_HEIGHT = 7
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
INVENTORY_WIDTH = 50

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)


logger = Logger()


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    # render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)
    # render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    # now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    # finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))


def inventory_menu(header, active, con, player):
    # show a menu with each item of the inventory as an option
    if len(player.inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in player.inventory:
            text = item.name
            if isinstance(item, Equipment) and item.is_equipped:
                text = text + ' (on ' + item.slot + ')'
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, con)
    # if an item was chosen, return it
    if index is None or len(player.inventory) == 0 or active == 0:
        return None
    return player.inventory[index]




class Game:
    def __init__(self,map_height, map_width, screen_height, screen_width):
        self.dungeon_level = 1
        self.objects = []
        self.level = 1
        self.map_height = map_height
        self.map_width = map_width
        self.player = Player(0, 0, 'O', 'player', libtcod.white,
                             blocks=True, objects=[], logger=logger)
        self.player.set(hp=100, defense=1, power=4, xp=0)
        self.initialize()
        self.player.objects = self.objects
        self.give_dagger_to_player()

    def initialize(self):
        self.map = Map(self.map_height, self.map_width)
        self.game_state = 'playing'
        self.objects = [self.player]
        self.player.objects = self.objects
        self.prev_key = 'up'
        self.prev_step = 0
        for room in self.map.rooms:
            self.place_monsters(room)
            self.place_items(room)
        self.create_gate()
        self.player.x, self.player.y = self.map.start_x, self.map.start_y,

    def create_gate(self):
        self.stairs = Object(self.map.gate_x, self.map.gate_y, '<', 'stairs', libtcod.white,
                        always_visible=True, objects=self.objects, logger=logger)
        self.objects.append(self.stairs)
        self.stairs.send_to_back()

    def give_dagger_to_player(self):
        dagger = Equipment(0, 0, '-', 'dagger', libtcod.sky, objects=self.objects, logger=logger)
        dagger.set(slot='right hand', power_bonus=2)
        dagger.set_owner(self.player)
        self.player.inventory.append(dagger)
        dagger.equip()
        dagger.always_visible = True

    def place_monsters(self, room):
        # this is where we decide the chance of each monster or item appearing.

        # maximum number of monsters per room
        if self.level > 30:
            max_monsters = 30
        else:
            max_monsters = self.level + 3

        # choose random number of monsters
        num_monsters = libtcod.random_get_int(0, 0, max_monsters)

        for i in range(num_monsters):
            # choose random spot for this monster
            x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
            y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

            # only place it if the tile is not blocked
            if not self.map.is_blocked(x, y):
                choice = random.random()
                if choice > 0.4:
                    monster = Monster(x, y, '8', 'The Hateful Eight', libtcod.desaturated_green,
                                      blocks=True, objects=self.objects, logger=logger)
                    monster.set(hp=8, defense=0, power=2, xp=50)
                    self.objects.append(monster)

                if choice > 0.7:
                    monster = Monster(x, y, '*', 'Frightful Snowflake', libtcod.darker_green,
                                      blocks=True, objects=self.objects, logger=logger)
                    monster.set(hp=8, defense=2, power=5, xp=100)
                    self.objects.append(monster)



    def place_items(self, room):
        # maximum number of items per room
        max_items = 2
        # chance of each item (by default they have a chance of 0 at level 1, which then goes up)
        # choose random number of items
        num_items = libtcod.random_get_int(0, 0, max_items)

        for i in range(num_items):
            # choose random spot for this item
            x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
            y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

            # only place it if the tile is not blocked
            if not self.map.is_blocked(x, y):
                choice = random.random()

                if choice >= 0.9 and choice * 100 / 2 == 0:
                    # create a sword
                    item = Equipment(x, y, '/', 'sword', libtcod.sky, objects=self.objects, logger=logger)
                    item.set(slot='right hand', power_bonus=3)

                elif choice >= 0.9 and choice * 100 / 10 == 0:
                    # create a shield
                    item = Equipment(x, y, '[', 'shield', libtcod.darker_orange, objects=self.objects, logger=logger)
                    item.set(slot='left hand', defense_bonus=1)

                else:
                    item = Heal(x, y, '!', 'healing potion', libtcod.violet, objects=self.objects, logger=logger)

                self.objects.append(item)
                item.send_to_back()  # items appear below other objects
                item.always_visible = True  # items are visible even out-of-FOV, if in an explored area


    def start(self):
        logger.message('Ready', libtcod.red)
        logger.message('Steady', libtcod.yellow)
        logger.message('Go!', libtcod.green)
        logger.message('The game is coming', libtcod.green)
        self.play()

    def play(self):
        global key, mouse
        step = 0
        mouse = libtcod.Mouse()
        key = libtcod.Key()

        some_happened = False
        while not libtcod.console_is_window_closed():
            step += 1
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)
            if some_happened:
                self.render_all()
                libtcod.console_flush()
                #check_level_up()
                for object in self.objects:
                    object.clear(self.map)
                self.player.clear(self.map)

            player_action = self.handle_keys(step)
            if player_action == 'exit' or self.player.died:
                break

            some_happened = True
            if self.game_state == 'playing' and player_action != 'didnt-take-turn' and player_action != 'nothing_happened':
                for object in self.objects:
                    if isinstance(object, Monster) and not object.died:
                        object.take_turn(self.player, self.map)
            elif player_action == 'nothing_happened':
                some_happened = False

        logger.message('End of game')

    def handle_keys(self, step):
        if key.vk == libtcod.KEY_ESCAPE:
            return 'exit'  # exit game

        if self.game_state == 'playing':
            if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
                current_key = 'up'
                if step != self.prev_step + 1 or current_key != self.prev_key:
                    self.prev_step = step
                    self.prev_key = current_key
                    self.player.move_or_attack(0, -1, self.map)
                elif current_key == self.prev_key and self.player.stopped:
                    self.player.move_or_attack(0, 0, self.map)
                else:
                    return 'nothing_happened'
            elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
                current_key = 'down'
                if step != self.prev_step + 1 or current_key != self.prev_key:
                    self.prev_step = step
                    self.prev_key = current_key
                    self.player.move_or_attack(0, 1, self.map)
                elif current_key == self.prev_key and self.player.stopped:
                    self.player.move_or_attack(0, 0, self.map)
                else:
                    return 'nothing_happened'
            elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
                current_key = 'left'
                if step != self.prev_step + 1 or current_key != self.prev_key:
                    self.prev_step = step
                    self.prev_key = current_key
                    self.player.move_or_attack(-1, 0, self.map)
                elif current_key == self.prev_key and self.player.stopped:
                    self.player.move_or_attack(0, 0, self.map)
                else:
                    return 'nothing_happened'
            elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
                current_key = 'right'
                if step != self.prev_step + 1 or current_key != self.prev_key:
                    self.prev_step = step
                    self.prev_key = current_key
                    self.player.move_or_attack(1, 0, self.map)
                elif current_key == self.prev_key and self.player.stopped:
                    self.player.move_or_attack(0, 0, self.map)
                else:
                    return 'nothing_happened'
            else:
                # test for other keys
                key_char = chr(key.c)
                self.prev_key = 'other'

                if key_char == 'g':
                    for object in self.objects:
                        if object.x == self.player.x and object.y == self.player.y and isinstance(object, Item):
                            object.pick_up(self.player)
                            break

                if key_char == 'i':
                    # show the inventory; if an item is selected, use it
                    chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n',
                                                 1, self.map.con, self.player)
                    if chosen_item is not None:
                        chosen_item.use()

                if key_char == 'r':
                    # show the inventory; if an item is selected, drop it
                    chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n',
                                                 1, self.map.con, self.player)
                    if chosen_item is not None:
                        chosen_item.drop()

                if key_char == '1':
                    # go down stairs, if the player is on them
                    if self.stairs.x == self.player.x and self.stairs.y == self.player.y:
                        self.next_level()
                return 'didnt-take-turn'

    def next_level(self):
        self.player.heal(self.player.max_hp)
        self.dungeon_level += 1
        mes = "Let's play..."
        logger.message(mes, libtcod.red)
        self.initialize()



    def render_all(self):
        if self.map.fov_recompute:
            # recompute FOV if needed (the player moved or something)
            self.map.fov_recompute = False
            libtcod.map_compute_fov(self.map.fov_map, self.player.x, self.player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

            # go through all tiles, and set their background color according to the FOV
            for y in range(self.map.height):
                for x in range(self.map.width):
                    visible = libtcod.map_is_in_fov(self.map.fov_map, x, y)
                    wall = self.map.tiles[x][y].block_sight
                    if not visible:
                        # if it's not visible right now, the player can only see it if it's explored
                        if self.map.tiles[x][y].explored:
                            if wall:
                                libtcod.console_set_char_background(self.map.con, x, y, color_dark_wall, libtcod.BKGND_SET)
                            else:
                                libtcod.console_set_char_background(self.map.con, x, y, color_dark_ground, libtcod.BKGND_SET)
                    else:
                        # it's visible
                        if wall:
                            libtcod.console_set_char_background(self.map.con, x, y, color_light_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(self.map.con, x, y, color_light_ground, libtcod.BKGND_SET)
                            # since it's visible, explore it
                        self.map.tiles[x][y].explored = True

        for object in self.objects:
            if object != self.player:
                object.draw(self.map)
        self.player.draw(self.map)

        # blit the contents of "con" to the root console
        libtcod.console_blit(self.map.con, 0, 0, self.map.width, self.map.height, 0, 0, 0)

        # prepare to render the GUI panel
        libtcod.console_set_default_background(panel, libtcod.black)
        libtcod.console_clear(panel)

        # print the game messages, one line at a time
        y = 1
        for (line, color) in logger.game_msgs:
            libtcod.console_set_default_foreground(panel, color)
            libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
            y += 1

        # show the player's stats
        render_bar(1, 1, BAR_WIDTH, 'HP', self.player.hp, self.player.max_hp,
                   libtcod.light_red, libtcod.darker_red)
        libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(self.dungeon_level))

        # display names of objects under the mouse
        libtcod.console_set_default_foreground(panel, libtcod.light_gray)

        # blit the contents of "panel" to the root console
        libtcod.console_blit(panel, 0, 0, screen_width, PANEL_HEIGHT, 0, 0, PANEL_Y)


def menu(header, options, width, screen_height, screen_width, con):
    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, screen_height, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    # print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = screen_width / 2 - width / 2
    y = screen_width / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    # convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options):
        return index
    return None


def create_main_menu(screen_width, screen_height, con):
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        libtcod.image_blit_2x(img, 0, 0, 0)

        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, screen_width / 2, screen_height / 2 - 4,
                                 libtcod.BKGND_NONE, libtcod.CENTER, 'ROGUELIKE')
        libtcod.console_print_ex(0, screen_width / 2, screen_height - 2, libtcod.BKGND_NONE, libtcod.CENTER, '')

        choice = menu('', ['Play a game', 'Quit'], 24, screen_height, screen_width, con)
        if choice == 0:
            new_game = Game(map_height, map_width, screen_width, screen_height)
            new_game.start()
        elif choice == 1:
            break


if __name__ == '__main__':
    screen_width = 80
    screen_height = 50
    limit_fps = 40

    map_width = 80
    map_height = 43
    panel_height = 7
    logger = Logger()

    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'python/libtcod tutorial', False)
    libtcod.sys_set_fps(limit_fps)
    con = libtcod.console_new(map_width, map_height)
    panel = libtcod.console_new(screen_width, panel_height)

    create_main_menu(screen_width, screen_height, con)
