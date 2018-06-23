import unittest
from FighterClass import *
from ItemClass import *
from MapClass import *


class TestMethods(unittest.TestCase):

    def test_fighter_move(self):
        player = Player(0, 0, 'O', 'player', libtcod.white, blocks=True, objects=[])
        player.level = 1
        map = Map(70, 70)
        player.x, player.y = map.start_x, map.start_y
        x, y = player.x, player.y
        player.move(-1, -1, map)

        if not player.stopped:
            self.assertEqual(player.x, x - 1)
            self.assertEqual(player.y, y - 1)
        else:
            self.assertEqual(player.x, x)
            self.assertEqual(player.y, y)

    def test_pick_item(self):
        player = Player(0, 0, 'O', 'player', libtcod.white, blocks=True, objects=[])
        player.set(hp=100, defense=1, power=4, xp=0)
        map = Map(70, 70)
        player.x, player.y = map.start_x, map.start_y
        heal_item = Heal(0, 0, '!', 'healing potion', libtcod.violet, objects=player.objects)
        player.objects.extend([player, heal_item])
        self.assertEqual(heal_item in player.inventory, False)
        heal_item.pick_up(player)
        self.assertEqual(heal_item in player.objects, False)
        self.assertEqual(heal_item in player.inventory, True)

    def test_heal(self):
        player = Player(0, 0, 'O', 'player', libtcod.white, blocks=True, objects=[])
        player.set(hp=100, defense=1, power=4, xp=0)
        map = Map(70, 70)
        player.x, player.y = map.start_x, map.start_y
        heal_item = Heal(0, 0, '!', 'healing potion', libtcod.violet, objects=player.objects)
        player.objects.extend([player, heal_item])
        heal_item.pick_up(player)
        player.hp = 50
        hp = player.hp
        self.assertEqual(heal_item in player.inventory, True)
        player.heal(20)
        self.assertEqual(player.hp > hp, True)

    def test_monstr_attack(self):
        player = Player(0, 0, 'O', 'player', libtcod.white, blocks=True, objects=[])
        player.set(hp=100, defense=0, power=4, xp=0)
        map = Map(70, 70)
        player.x, player.y = map.start_x, map.start_y
        monster = Monster(player.x + 0, player.y + 1, '*', 'Frightful Snowflake', libtcod.darker_green,
                             blocks=True, objects=player.objects)
        monster.set(hp=8, defense=2, power=5, xp=100)
        player.objects.extend([player, monster])
        prev_hp = player.hp
        monster.attack(player)
        self.assertEqual(player.hp, prev_hp - monster.power + player.defense)

    def test_player_attack(self):
        player = Player(0, 0, 'O', 'player', libtcod.white, blocks=True, objects=[])
        player.set(hp=100, defense=1, power=4, xp=0)
        map = Map(70, 70)
        player.x, player.y = map.start_x, map.start_y
        monster = Monster(player.x + 0, player.y + 1, '*', 'Frightful Snowflake', libtcod.darker_green,
                          blocks=True, objects=player.objects)
        monster.set(hp=8, defense=2, power=5, xp=100)
        player.objects.extend([player, monster])
        prev_hp = monster.hp
        monster.take_turn(player, map)
        player.move_or_attack(0, 1, map)
        self.assertEqual(monster.hp, prev_hp - player.power + monster.defense)


if __name__ == '__main__':
    unittest.main()
