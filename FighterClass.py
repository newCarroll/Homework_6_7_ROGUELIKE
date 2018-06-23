import math

from ObjectClass import *
from LoggerClass import *


class Fighter(Object):
    # combat-related properties and methods (monster, player, NPC).
    def set(self, hp, defense, power, xp, inventory=[]):
        self.max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.defense = defense
        self.base_power = power
        self.power = power
        self.xp = xp
        self.stopped = False
        self.died = False
        self.inventory = inventory

    def attack(self, target):
        # a simple formula for attack damage
        damage = self.power - target.defense
        target.take_damage(damage, self)

        if not self.logger is None:
            # make the target take some damage
            mess = self.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.'
            self.logger.message(mess)

    def take_damage(self, damage, owner):
        # apply damage if possible
        if damage > 0:
            self.hp -= damage
            if self.hp <= 0:
                self.die()

            self.get_experience(owner)

    def get_experience(self, owner):
        pass

    def move(self, dx, dy, map):
        # move by the given amount, if the destination is not blocked
        blocked = map.is_blocked(self.x + dx, self.y + dy)
        # now check for any blocking objects
        if not blocked:
            for object in self.objects:
                if object != self and object.blocks and object.x == self.x + dx and object.y == self.y + dy:
                    blocked = True
                    break
        if not blocked:
            self.x += dx
            self.y += dy
            self.stopped = False
        else:
            self.stopped = True

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def die(self):
        pass


class Player(Fighter):

    def heal(self, amount):
        self.hp = min(self.hp + amount, self.max_hp)

    def get_experience(self, owner):
        owner.xp += self.xp


    def die(self):
        mes = 'You died!'
        self.logger.message(mes, libtcod.red)
        self.char = 'X'
        self.color = libtcod.dark_red
        self.died = True

    @property
    def power(self):
        bonus = sum(equipment.power_bonus for equipment in self.inventory)
        return self.base_power + bonus

    @property
    def defense(self):
        bonus = sum(equipment.defense_bonus for equipment in self.inventory)
        return self.base_defense + bonus

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in self.inventory)
        return self.max_hp + bonus

    def move_or_attack(self, dx, dy, map):
        x = self.x + dx
        y = self.y + dy
        # the coordinates the player is moving to/attacking

        # try to find an attackable object there
        target = None
        for object in self.objects:
            if isinstance(object, Monster) and object.x == x and object.y == y:
                target = object
                break

        # attack if target found, move otherwise
        if target is not None:
           self.attack(target)
        else:
            self.move(dx, dy, map)
            map.fov_recompute = True


class Monster(Fighter):

    def move_towards(self, target, map):
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy, map)

    def take_turn(self, target, map):
        if libtcod.map_is_in_fov(map.fov_map, self.x, self.y):
            if self.distance_to(target) >= 2:
                self.move_towards(target, map)
            elif target.hp > 0:
                self.attack(target)

    def die(self):
        mes = 'The ' + self.name + ' is dead! You gain ' + str(self.xp) + ' experience points.'
        self.logger.message(mes, libtcod.yellow)
        self.objects.remove(self)
