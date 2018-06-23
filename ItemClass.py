from ObjectClass import *

class Item(Object):

    def set_owner(self, owner):
        self.owner = owner

    def pick_up(self, owner):
        pass

    def drop(self):
        pass

    def use(self):
       pass


class Equipment(Item):
    def set(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.slot = slot
        self.is_equipped = False

    def toggle_equip(self):
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def pick_up(self, owner):
        self.set_owner(owner)
        # add to the player's inventory and remove from the map
        if len(owner.inventory) >= 5:
            mes = 'Your inventory is full, cannot pick up ' + self.owner.name + '.'
            # message(mes, libtcod.red)
            # event_logging(mes)
        else:
            self.owner.inventory.append(self)
            self.objects.remove()
            # mes = ' You picked up a ' + self.owner.name + '!'
            # message(mes, libtcod.green)
            # event_logging(mes)
            if self.get_equipped_in_slot(self.slot) is None:
                self.equip()

    def equip(self):
        # if the slot is already being used, dequip whatever is there first
        old_equipment = self.get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        # equip object and show a message about it
        self.is_equipped = True
        # mes = 'Equipped ' + self.owner.name + ' on ' + self.slot + '.'
        # message(mes, libtcod.light_green)
        # event_logging(mes)

    def dequip(self):
        if not self.is_equipped:
            return
        self.is_equipped = False
        # mes = 'Dequipped ' + self.owner.name + ' from ' + self.slot + '.'
        # message(mes, libtcod.light_yellow)
        # event_logging(mes)

    def use(self):
        self.toggle_equip()

    def drop(self):
        self.dequip()
        self.objects.append(self.owner)
        self.owner.inventory.remove(self)
        self.x = self.owner.x
        self.y = self.owner.y
        # mes = 'You dropped a ' + self.owner.name + '.'
        # message(mes, libtcod.yellow)
        # event_logging(mes)

    def get_equipped_in_slot(self, slot):  # returns the equipment in a slot, or None if it's empty
        for obj in self.owner.inventory:
            if isinstance(obj, Equipment) and obj.slot == slot and obj.is_equipped:
                return obj
        return None

    def get_all_equipped(self):
        equipped_list = []
        for item in self.owner.inventory:
            if isinstance(item, Equipment) and item.equipment.is_equipped:
                equipped_list.append(item)
        return equipped_list




class Heal(Item):


    def use(self):
        mes = 'Do you feel bettter?'
        #message(mes, libtcod.green)
        self.owner.heal(40)
        self.owner.inventory.remove(self)

    def pick_up(self, owner):
        self.set_owner(owner)
        if len(owner.inventory) >= 5:
            mes = 'Your inventory is full, cannot pick up ' + self.owner.name + '.'
            #message(mes, libtcod.red)
            #event_logging(mes)
        else:
            self.owner.inventory.append(self)
            self.objects.remove(self)
            # mes = ' You picked up a ' + self.owner.name + '!'
            # message(mes, libtcod.green)


    def drop(self):
        self.objects.append(self.owner)
        self.owner.inventory.remove(self)
        self.x = self.owner.x
        self.y = self.owner.y
        # mes = 'You dropped a ' + self.owner.name + '.'
        # message(mes, libtcod.yellow)
        # event_logging(mes)



