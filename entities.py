# entities.py - Updated for Core Fantasy Engine
import math
import random
from config import *
from quest import QuestLog, Quest
from items import *
from spells import CORE_SPELLS, STARTING_MAGE_SPELLS, get_spell_by_name

def roll_dice(num_dice, sides):
    """Rolls a number of dice with a given number of sides."""
    return sum(random.randint(1, sides) for _ in range(num_dice))

def calculate_modifier(score):
    """Calculates the unified modifier from an ability score."""
    return math.floor((score - 10) / 2)

def universal_resolution(d20_roll, ability_modifier, proficiency_bonus, target_number):
    """The Universal Resolution Mechanic - core of CFE."""
    return (d20_roll + ability_modifier + proficiency_bonus) >= target_number

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
        self.level = 1
        
        # CFE Temporary Effects
        self.temporary_ac_bonus = 0
        self.sleeping = False
        self.invisible = False
        self.restrained = False
        self.flying = False
        self.hasted = False
        
        self.update_modifiers()

    @property
    def ac(self):
        """Calculates total AC using CFE system."""
        base_ac = 10  # CFE base AC
        dex_bonus = self.modifiers['DEX']
        equipment_bonus = 0
        
        # Add equipment AC bonuses
        if hasattr(self, 'equipment'):
            for item in self.equipment.values():
                if item and hasattr(item, 'bonuses'):
                    equipment_bonus += item.bonuses.get('ac', 0)
        
        return base_ac + dex_bonus + equipment_bonus + self.temporary_ac_bonus

    @property
    def attack_bonus(self):
        """Calculates total attack bonus using CFE system."""
        base_bonus = self.base_attack_bonus
        str_bonus = self.modifiers['STR']
        equipment_bonus = 0
        
        if hasattr(self, 'equipment') and self.equipment.get("Weapon"):
            weapon = self.equipment["Weapon"]
            if hasattr(weapon, 'bonuses'):
                equipment_bonus += weapon.bonuses.get('attack', 0)
        
        return base_bonus + str_bonus + equipment_bonus

    @property
    def spell_attack_bonus(self):
        """Spell attack bonus for mages."""
        return self.modifiers['INT'] + (self.level // 2)

    # CFE Saving Throws
    @property
    def fortitude_save(self):
        """Fortitude save (CON-based) - resists poison, disease, physical effects."""
        base_bonus = self.level // 2
        con_bonus = self.modifiers['CON']
        equipment_bonus = 0
        
        if hasattr(self, 'equipment'):
            for item in self.equipment.values():
                if item and hasattr(item, 'bonuses'):
                    equipment_bonus += item.bonuses.get('fortitude', 0)
        
        return base_bonus + con_bonus + equipment_bonus

    @property
    def reflex_save(self):
        """Reflex save (DEX-based) - dodges area attacks, traps."""
        base_bonus = self.level // 2
        dex_bonus = self.modifiers['DEX']
        equipment_bonus = 0
        
        if hasattr(self, 'equipment'):
            for item in self.equipment.values():
                if item and hasattr(item, 'bonuses'):
                    equipment_bonus += item.bonuses.get('reflex', 0)
        
        return base_bonus + dex_bonus + equipment_bonus

    @property
    def will_save(self):
        """Will save (WIS-based) - resists mental effects, magic."""
        base_bonus = self.level // 2
        wis_bonus = self.modifiers['WIS']
        equipment_bonus = 0
        
        if hasattr(self, 'equipment'):
            for item in self.equipment.values():
                if item and hasattr(item, 'bonuses'):
                    equipment_bonus += item.bonuses.get('will', 0)
        
        return base_bonus + wis_bonus + equipment_bonus

    def update_modifiers(self):
        for stat, value in self.abilities.items():
            self.modifiers[stat] = calculate_modifier(value)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0: 
            self.hp = 0
        return damage

    def make_saving_throw(self, save_type, dc):
        """Make a saving throw using CFE system."""
        roll = roll_dice(1, 20)
        
        if save_type == "fortitude":
            total = roll + self.fortitude_save
        elif save_type == "reflex":
            total = roll + self.reflex_save
        elif save_type == "will":
            total = roll + self.will_save
        else:
            total = roll  # No bonus for unknown save types
        
        return total >= dc, total

    def attack(self, target):
        """Attack using CFE Universal Resolution Mechanic."""
        attack_roll = roll_dice(1, 20)
        total_attack = attack_roll + self.attack_bonus
        
        if universal_resolution(attack_roll, self.attack_bonus - self.modifiers['STR'], self.modifiers['STR'], target.ac):
            # Calculate damage
            damage = self.calculate_damage()
            actual_damage = target.take_damage(damage)
            return f"{self.name} hits {target.name} for {actual_damage} damage!"
        else:
            return f"{self.name} misses {target.name}."

    def calculate_damage(self):
        """Calculate damage from equipped weapon or default."""
        base_damage = 1  # Unarmed damage
        damage_bonus = self.modifiers['STR']
        
        if hasattr(self, 'equipment') and self.equipment.get("Weapon"):
            weapon = self.equipment["Weapon"]
            if hasattr(weapon, 'damage_dice'):
                base_damage = roll_dice(weapon.damage_dice, weapon.damage_sides)
            if hasattr(weapon, 'bonuses'):
                damage_bonus += weapon.bonuses.get('damage', 0)
        
        return max(1, base_damage + damage_bonus)
            
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
    """The player character with CFE archetype abilities."""
    def __init__(self, archetype, abilities):
        super().__init__(0, 0, '@', COLOR_PLAYER, 'Player')
        self.abilities = abilities
        self.update_modifiers()
        
        self.archetype = archetype
        self.level = 1
        self.xp = 0
        self.gold = roll_dice(3, 6) * 10  # CFE starting gold: 3d6 × 10
        
        # CFE Archetype-specific setup
        hp_die = ARCHETYPES[archetype]["hp_die"]
        self.max_hp = roll_dice(1, hp_die) + self.modifiers['CON']
        if self.max_hp < 1: 
            self.max_hp = 1
        self.hp = self.max_hp
        
        self.base_attack_bonus = ARCHETYPES[archetype]["attack_bonus_start"]
        
        # Equipment slots
        self.equipment = {
            "Weapon": None,
            "Armor": None,
            "Shield": None,
            "Ring": None
        }
        
        # Starting equipment based on archetype
        starting_items = STARTING_ITEMS.get(archetype, [])
        self.inventory = starting_items.copy()
        
        # Auto-equip appropriate starting items
        for item in starting_items:
            if hasattr(item, 'equip_slot') and item.equip_slot in self.equipment:
                self.equipment[item.equip_slot] = item
                self.inventory.remove(item)
        
        # Archetype-specific abilities
        if archetype == "Warrior":
            self.power_attack_available = True
            
        elif archetype == "Mage":
            # CFE Spell system
            self.spell_slots = SPELL_SLOTS_BY_LEVEL[1].copy()
            self.max_spell_slots = SPELL_SLOTS_BY_LEVEL[1].copy()
            self.known_spells = STARTING_MAGE_SPELLS.copy()
            self.prepared_spells = {1: [], 2: [], 3: []}
            # Auto-prepare starting spells
            for spell_name in STARTING_MAGE_SPELLS[:2]:  # Prepare first 2 spells
                if spell_name in self.known_spells:
                    self.prepared_spells[1].append(spell_name)
            
        elif archetype == "Expert":
            # CFE Skills
            self.skills = {
                "stealth": True,
                "lockpicking": True,
                "trap_disarm": True,
                "hide": True
            }
            self.sneak_attack_dice = 1  # Starts at 1d6
        
        self.known_locations = set()
        self.quest_log = QuestLog()

    @property
    def display_inventory(self):
        """Returns a filtered list of items for the inventory panel (no equipment)."""
        return [item for item in self.inventory if not (hasattr(item, 'equip_slot') and item.equip_slot)]

    @property 
    def xp_to_next_level(self):
        """Calculate XP needed for next level."""
        if self.level >= 5:
            return LEVEL_PROGRESSION[5]["xp_required"] * 2  # Beyond level 5
        next_level = min(5, self.level + 1)
        return LEVEL_PROGRESSION[next_level]["xp_required"]

    def level_up(self):
        """Handle CFE leveling up."""
        if self.xp < self.xp_to_next_level:
            return "Not enough XP to level up!"
        
        old_level = self.level
        self.level += 1
        
        # Spend XP
        self.xp -= LEVEL_PROGRESSION[old_level + 1]["xp_required"]
        
        # Gain HP
        hp_die = ARCHETYPES[self.archetype]["hp_die"]
        hp_gain = roll_dice(1, hp_die) + self.modifiers['CON']
        self.max_hp += max(1, hp_gain)
        self.hp = self.max_hp  # Full heal on level up
        
        # Increase attack bonus
        if self.archetype == "Warrior":
            self.base_attack_bonus += 1
        elif self.archetype == "Expert" and self.level % 2 == 0:
            self.base_attack_bonus += 1
        elif self.archetype == "Mage" and self.level % 3 == 0:
            self.base_attack_bonus += 1
        
        # Archetype-specific improvements
        if self.archetype == "Mage" and self.level <= 5:
            # Update spell slots
            self.spell_slots = SPELL_SLOTS_BY_LEVEL[self.level].copy()
            self.max_spell_slots = SPELL_SLOTS_BY_LEVEL[self.level].copy()
            
        elif self.archetype == "Expert":
            # Improve sneak attack
            if self.level == 3:
                self.sneak_attack_dice = 2
            elif self.level == 5:
                self.sneak_attack_dice = 3
        
        return f"You reached level {self.level}! Gained {hp_gain} HP!"

    def check_for_level_up(self):
        """Check if player can level up."""
        return self.xp >= self.xp_to_next_level

    # --- CFE Archetype Abilities ---
    
    def power_attack(self, target):
        """Warrior's Power Attack: -2 to hit, double damage on hit."""
        if self.archetype != "Warrior":
            return "You don't know how to power attack!"
        
        attack_roll = roll_dice(1, 20)
        total_attack = attack_roll + self.attack_bonus - 2  # -2 penalty
        
        if total_attack >= target.ac:
            damage = self.calculate_damage() * 2  # Double damage
            actual_damage = target.take_damage(damage)
            return f"Power attack hits {target.name} for {actual_damage} damage!"
        else:
            return f"Power attack misses {target.name}."

    def attempt_skill(self, skill_name, difficulty_class):
        """Expert skill check using CFE Universal Resolution Mechanic."""
        if self.archetype != "Expert":
            return "You don't have that skill!"
        
        if skill_name not in self.skills:
            return f"You don't know the {skill_name} skill!"
        
        roll = roll_dice(1, 20)
        ability_mod = self.modifiers['DEX']  # Most skills use DEX
        prof_bonus = self.level // 2
        
        total = roll + ability_mod + prof_bonus
        
        if total >= difficulty_class:
            return f"{skill_name.title()} succeeded! ({total} vs DC {difficulty_class})"
        else:
            return f"{skill_name.title()} failed. ({total} vs DC {difficulty_class})"

    def sneak_attack(self, target):
        """Expert's sneak attack - extra damage when target is unaware."""
        if self.archetype != "Expert":
            return 0
        
        # Check if conditions are met (simplified for MVP)
        if hasattr(target, 'sleeping') and target.sleeping:
            return roll_dice(self.sneak_attack_dice, 6)
        if hasattr(target, 'surprised') and target.surprised:
            return roll_dice(self.sneak_attack_dice, 6)
        
        return 0

    # --- CFE Magic System ---
    
    def prepare_spell(self, spell_name, spell_level):
        """Prepare a spell in an available slot."""
        if self.archetype != "Mage":
            return "You cannot cast spells!"
        
        if spell_name not in self.known_spells:
            return f"You don't know the spell {spell_name}!"
        
        spell = get_spell_by_name(spell_name)
        if not spell or spell.level != spell_level:
            return f"Invalid spell or level!"
        
        # Check if we have available slots
        max_prepared = self.max_spell_slots.get(spell_level, 0)
        currently_prepared = len(self.prepared_spells.get(spell_level, []))
        
        if currently_prepared >= max_prepared:
            return f"No more level {spell_level} spell slots available!"
        
        self.prepared_spells[spell_level].append(spell_name)
        return f"Prepared {spell_name}!"

    def cast_spell(self, spell_name, target=None, game_engine=None):
        """Cast a prepared spell using CFE magic system."""
        if self.archetype != "Mage":
            return "You cannot cast spells!"
        
        spell = get_spell_by_name(spell_name)
        if not spell:
            return f"Unknown spell: {spell_name}!"
        
        # Check if spell is prepared
        if spell_name not in self.prepared_spells.get(spell.level, []):
            return f"{spell_name} is not prepared!"
        
        # Check if we have spell slots
        if self.spell_slots.get(spell.level, 0) <= 0:
            return "No spell slots remaining for that level!"
        
        # Cast the spell
        self.spell_slots[spell.level] -= 1
        self.prepared_spells[spell.level].remove(spell_name)
        
        # Execute spell effect
        try:
            result = spell.effect(self, target, game_engine)
            return result
        except Exception as e:
            return f"Spell casting failed: {str(e)}"

    def rest(self):
        """Rest to restore spell slots and prepare spells."""
        if self.archetype == "Mage":
            # Restore all spell slots
            self.spell_slots = self.max_spell_slots.copy()
            # Clear prepared spells (player must re-prepare)
            self.prepared_spells = {1: [], 2: [], 3: []}
            return "You rest and restore your magical energy. Your prepared spells have been cleared."
        return "You rest and feel refreshed."

    def gain_treasure_xp(self, gold_value):
        """Gain 1 XP per 1 GP of treasure value (CFE system)."""
        self.xp += gold_value
        return f"Gained {gold_value} XP from treasure!"

    def gain_monster_xp(self, monster_xp):
        """Gain XP from defeating monsters."""
        self.xp += monster_xp
        return f"Gained {monster_xp} XP from combat!"

    def use_item(self, item):
        """Use a consumable item."""
        if item.item_type == 'consumable':
            if item.healing:
                if len(item.healing) == 3:  # (num_dice, die_size, bonus)
                    num_dice, die_size, bonus = item.healing
                    heal_amount = roll_dice(num_dice, die_size) + bonus
                else:  # Legacy format (num_dice, die_size)
                    heal_amount = roll_dice(item.healing[0], item.healing[1])
                
                self.hp = min(self.max_hp, self.hp + heal_amount)
                self.inventory.remove(item)
                return f"You use the {item.name}, healing for {heal_amount} HP."
        return f"You can't use the {item.name}."

    def equip(self, item):
        """Equip an item from inventory."""
        if not hasattr(item, 'equip_slot') or not item.equip_slot:
            return "You can't equip that."
        
        if item.equip_slot not in self.equipment:
            return "Invalid equipment slot."
        
        # Check proficiency
        if hasattr(item, 'category'):
            if item.category in WEAPON_CATEGORIES:
                allowed_weapons = get_weapons_by_proficiency(self.archetype)
                if item not in allowed_weapons:
                    return f"{self.archetype}s cannot use {item.name}!"
            elif item.category in ARMOR_CATEGORIES:
                allowed_armor = get_armor_by_proficiency(self.archetype)
                if item not in allowed_armor:
                    return f"{self.archetype}s cannot wear {item.name}!"
        
        # Unequip current item
        currently_equipped = self.equipment.get(item.equip_slot)
        if currently_equipped:
            self.inventory.append(currently_equipped)
        
        # Equip new item
        self.equipment[item.equip_slot] = item
        if item in self.inventory:
            self.inventory.remove(item)
        
        return f"You equip the {item.name}."

class Monster(Combatant):
    """CFE Monster using template system."""
    def __init__(self, x, y, template_name):
        if template_name not in MONSTER_TEMPLATES:
            raise ValueError(f"Unknown monster template: {template_name}")
        
        template = MONSTER_TEMPLATES[template_name]
        
        super().__init__(
            x, y, template["char"], template["color"], template["name"],
            hp=template["hp"], ac=template["ac"], attack_bonus=template["attack_bonus"]
        )
        
        self.template_name = template_name
        self.damage_dice = template["damage_dice"]
        self.damage_sides = template["damage_sides"]
        self.speed = template["speed"]
        self.xp_value = template["xp_value"]
        self.special_abilities = template["special_abilities"]

    def calculate_damage(self):
        """Calculate monster damage using template."""
        base_damage = roll_dice(self.damage_dice, self.damage_sides)
        
        # Apply special ability modifiers
        bonus = 0
        if "brute_strength" in self.special_abilities:
            bonus += 2  # Ogres hit harder
        
        return max(1, base_damage + bonus)

    def attack(self, target):
        """Monster attack with special abilities."""
        # Check for horde tactics
        attack_bonus = self.attack_bonus
        if "horde_tactics" in self.special_abilities:
            # +1 if any ally is adjacent to target (simplified)
            attack_bonus += self.check_horde_tactics(target)
        
        attack_roll = roll_dice(1, 20)
        total_attack = attack_roll + attack_bonus
        
        if total_attack >= target.ac:
            damage = self.calculate_damage()
            
            # Special ability effects
            if "poison_bite" in self.special_abilities:
                poison_result = self.apply_poison(target)
                damage_result = f"{self.name} bites {target.name} for {target.take_damage(damage)} damage!"
                return damage_result + " " + poison_result
            
            elif "blunt_vulnerability" in self.special_abilities:
                # Check if attacker is using blunt weapon
                weapon = getattr(target, 'equipment', {}).get('Weapon')
                if weapon and hasattr(weapon, 'name') and any(word in weapon.name.lower() for word in ['mace', 'club', 'hammer']):
                    damage *= 2
                    damage_result = f"{self.name} takes double damage from the blunt weapon!"
                
            target.take_damage(damage)
            return f"{self.name} hits {target.name} for {damage} damage!"
        else:
            return f"{self.name} misses {target.name}."

    def check_horde_tactics(self, target):
        """Check if goblin gets horde tactics bonus."""
        # Simplified: assume bonus if this is a goblin
        if self.template_name == "Goblin":
            return 1
        return 0

    def apply_poison(self, target):
        """Apply poison bite effect."""
        save_dc = 12
        success, total = target.make_saving_throw("fortitude", save_dc)
        
        if not success:
            poison_damage = roll_dice(1, 6)
            target.take_damage(poison_damage)
            return f"{target.name} takes {poison_damage} poison damage!"
        else:
            return f"{target.name} resists the poison!"

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
        # Create a simple template for crows
        super().__init__(x, y, "Goblin")  # Reuse goblin template but modify
        self.name = "a crow"
        self.char = CROW_CHAR
        self.color = COLOR_BLACK
        self.hp = 1
        self.xp_value = 0
        self.special_abilities = []

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