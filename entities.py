# entities.py
import math
import random
from config import *
from quest import QuestLog, Quest
from items import *

def roll_dice(num_dice, sides):
    """Rolls a number of dice with a given number of sides."""
    return sum(random.randint(1, sides) for _ in range(num_dice))

def calculate_modifier(score):
    """Calculates the unified modifier from an ability score."""
    return math.floor((score - 10) / 2)

class GameObject:
    """Base class for all game objects that appear on the map."""
    def __init__(self, x, y, char, color, name):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name

class Combatant(GameObject):
    """Base class for any object that can participate in combat."""
    def __init__(self, x, y, char, color, name, hp=10, ac=10, attack_bonus=0):
        super().__init__(x, y, char, color, name)
        self.max_hp = hp
        self.hp = hp
        self.base_ac = ac
        self.base_attack_bonus = attack_bonus
        self.abilities = {'STR': 10, 'DEX': 10, 'CON': 10, 'INT': 10, 'WIS': 10, 'CHA': 10}
        self.modifiers = {}
        self.update_modifiers()

    @property
    def ac(self):
        """Calculates total AC. Can be overridden by subclasses."""
        return self.base_ac

    @property
    def attack_bonus(self):
        """Calculates total attack bonus. Can be overridden by subclasses."""
        return self.base_attack_bonus

    def update_modifiers(self):
        for stat, value in self.abilities.items():
            self.modifiers[stat] = calculate_modifier(value)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0: self.hp = 0
        return damage

    def attack(self, target):
        attack_roll = roll_dice(1, 20) + self.attack_bonus
        damage = 0
        if hasattr(self, 'equipment') and self.equipment.get("Weapon"):
            weapon = self.equipment["Weapon"]
            damage = roll_dice(weapon.damage_dice, weapon.damage_sides)
        else:
            damage = 1 # Unarmed damage
        
        if attack_roll >= target.ac:
            target.take_damage(damage)
            return f"{self.name} hits {target.name} for {damage} damage!"
        else:
            return f"{self.name} misses {target.name}."
            
    def take_turn(self, target, game_map, all_combatants):
        """Default hostile AI: move towards player and attack within a certain range."""
        dx, dy = target.x - self.x, target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 10: return None 

        if distance < 1.5:
            return self.attack(target)
        else:
            move_dx = int(round(dx / distance)) if distance > 0 else 0
            move_dy = int(round(dy / distance)) if distance > 0 else 0
            new_x, new_y = self.x + move_dx, self.y + move_dy

            if 0 <= new_x < game_map.shape[0] and 0 <= new_y < game_map.shape[1]:
                is_wall = game_map[new_x, new_y].blocked
                is_occupied = any(c.x == new_x and c.y == new_y for c in all_combatants if c is not self and c.hp > 0)

                if not is_wall and not is_occupied:
                    self.x, self.y = new_x, new_y
        return None

class Player(Combatant):
    """The player character, with added stats from character creation."""
    def __init__(self, archetype, abilities):
        super().__init__(0, 0, '@', COLOR_PLAYER, 'Player')
        self.abilities = abilities
        self.update_modifiers()
        
        self.archetype = archetype
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 2000
        self.gold = 25
        
        self.max_hp = ARCHETYPES[archetype]["hp_die"] + self.modifiers['CON']
        if self.max_hp < 1: self.max_hp = 1
        self.hp = self.max_hp
        
        self.inventory = [health_potion, rope, iron_sword, wooden_shield]
        self.equipment = {
            "Weapon": short_sword,
            "Armor": leather_armor,
            "Shield": None,
            "Ring": None
        }
        self.known_locations = set()
        self.quest_log = QuestLog()

    @property
    def display_inventory(self):
        """Returns a filtered list of items for the inventory panel (no equipment)."""
        return [item for item in self.inventory if not item.equip_slot]

    @property
    def attack_bonus(self):
        bonus = self.modifiers['STR']
        for item in self.equipment.values():
            if item:
                bonus += item.bonuses.get('attack', 0)
        return bonus

    @property
    def ac(self):
        bonus = 10 + self.modifiers['DEX']
        for item in self.equipment.values():
            if item:
                bonus += item.bonuses.get('ac', 0)
        return bonus

    def level_up(self):
        """Handles the player leveling up."""
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level *= 2
        
        hp_gain = roll_dice(1, ARCHETYPES[self.archetype]["hp_die"]) + self.modifiers['CON']
        self.max_hp += max(1, hp_gain)
        self.hp = self.max_hp
        return f"You reached level {self.level}!"

    def use_item(self, item):
        """Uses a consumable item."""
        if item.item_type == 'consumable':
            if item.healing:
                heal_amount = roll_dice(item.healing[0], item.healing[1])
                self.hp = min(self.max_hp, self.hp + heal_amount)
                self.inventory.remove(item)
                return f"You use the {item.name}, healing for {heal_amount} HP."
        return f"You can't use the {item.name}."

    def equip(self, item):
        """Equips an item from inventory."""
        if item.equip_slot:
            currently_equipped = self.equipment.get(item.equip_slot)
            if currently_equipped:
                self.inventory.append(currently_equipped)
            
            self.equipment[item.equip_slot] = item
            self.inventory.remove(item)
            return f"You equip the {item.name}."
        return "You can't equip that."

class Monster(Combatant):
    """An AI-controlled monster."""
    def __init__(self, x, y, char, color, name, hp, ac, attack_bonus, xp_value):
        super().__init__(x, y, char, color, name, hp=hp, ac=ac, attack_bonus=attack_bonus)
        self.xp_value = xp_value

class NPC(GameObject):
    """A non-player character that can be interacted with."""
    def __init__(self, x, y, name, dialogue, quest=None):
        super().__init__(x, y, NPC_CHAR, COLOR_NPC, name)
        self.dialogue = dialogue
        self.quest = quest

    def take_turn(self, target, game_map, all_combatants):
        """NPCs don't do anything on their turn."""
        return None

class Crow(Monster):
    """A non-hostile creature that wanders randomly."""
    def __init__(self, x, y):
        super().__init__(x, y, CROW_CHAR, COLOR_BLACK, 'a crow', hp=1, ac=10, attack_bonus=0, xp_value=0)

    def take_turn(self, target, game_map, all_combatants):
        """Crows just move around randomly."""
        dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0), (0,0)])
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < game_map.shape[0] and 0 <= new_y < game_map.shape[1]:
            if not game_map[new_x, new_y].blocked:
                is_occupied = any(c.x == new_x and c.y == new_y for c in all_combatants if c is not self)
                if not is_occupied:
                    self.x, self.y = new_x, new_y
        return None
