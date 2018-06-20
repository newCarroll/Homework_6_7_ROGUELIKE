import unittest
import roguelike as rog
import libtcodpy as libtcod


class TestMethods(unittest.TestCase):

    def test_move(self):
        player = rog.Object(0, 0, 'O', 'player', libtcod.white, blocks=True, fighter=None)
        player.level = 1
        x, y = player.x, player.y
        player.move(-1, -1)

        if not player.stopped:
            self.assertEqual(player.x, x - 1)
            self.assertEqual(player.y, y - 1)
        else:
            self.assertEqual(player.x, x)
            self.assertEqual(player.y, y)

    def test_pick_item(self):
        item_component = rog.Item(use_function=rog.cast_heal)
        heal_item = rog.Object(0, 0, '!', 'healing potion', libtcod.violet, item=item_component)
        rog.objects.append(heal_item)
        self.assertEqual(heal_item in rog.inventory, False)
        heal_item.item.pick_up()
        self.assertEqual(heal_item in rog.objects, False)
        self.assertEqual(heal_item in rog.inventory, True)

    def test_heal(self):
        item_component = rog.Item(use_function=rog.cast_heal)
        heal_item = rog.Object(rog.player.x, rog.player.y, '!', 'healing potion', libtcod.violet, item=item_component)
        rog.objects.append(heal_item)
        heal_item.item.pick_up()
        rog.player.fighter.hp = 50
        hp = rog.player.fighter.hp
        self.assertEqual(heal_item in rog.inventory, True)
        rog.player.fighter.heal(rog.HEAL_AMOUNT)
        self.assertEqual(rog.player.fighter.hp > hp, True)

    def test_monstr_attack(self):
        fighter_component = rog.Fighter(hp=8, defense=2, power=5, xp=100, death_function=rog.monster_death)
        ai_component = rog.BasicMonster()
        monster = rog.Object(rog.player.x + 0, rog.player.y + 1, '*', 'Frightful Snowflake', libtcod.darker_green,
                             blocks=True, fighter=fighter_component, ai=ai_component)
        prev_hp = rog.player.fighter.hp
        monster.ai.take_turn()
        self.assertEqual(rog.player.fighter.hp, prev_hp - monster.fighter.power + rog.player.fighter.defense)

    def test_monstr_movement(self):
        fighter_component = rog.Fighter(hp=8, defense=2, power=5, xp=100, death_function=rog.monster_death)
        ai_component = rog.BasicMonster()
        monster = rog.Object(rog.player.x + 2, rog.player.y + 1, '*', 'Frightful Snowflake', libtcod.darker_green,
                             blocks=True, fighter=fighter_component, ai=ai_component)
        prev_distance = monster.distance_to(rog.player)
        monster.ai.take_turn()
        monster.ai.take_turn()
        self.assertEqual(monster.distance_to(rog.player) < prev_distance, True)

    def test_player_attack(self):
        fighter_component = rog.Fighter(hp=8, defense=2, power=5, xp=100, death_function=rog.monster_death)
        ai_component = rog.BasicMonster()
        monster = rog.Object(rog.player.x + 0, rog.player.y + 1, '*', 'Frightful Snowflake', libtcod.darker_green,
                             blocks=True, fighter=fighter_component, ai=ai_component)
        rog.objects.append(monster)
        prev_hp = monster.fighter.hp
        monster.ai.take_turn()
        rog.player_move_or_attack(0, 1)
        self.assertEqual(monster.fighter.hp, prev_hp - rog.player.fighter.power + monster.fighter.defense)


if __name__ == '__main__':
    unittest.main()
