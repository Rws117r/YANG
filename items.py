# items.py - CFE Equipment System
from config import WEAPON_CATEGORIES, ARMOR_CATEGORIES
import random

def roll_dice(num_dice, sides):
    """Rolls a number of dice with a given number of sides."""
    return sum(random.randint(1, sides) for _ in range(num_dice))

class Item:
    """Base class for all items using CFE category system."""
    def __init__(self, name, category, description="", item_type='misc', equip_slot=None, bonuses=None, healing=None):
        self.name = name
        self.category = category
        self.description = description
        self.item_type = item_type
        self.equip_slot = equip_slot
        self.bonuses = bonuses if bonuses else {}
        self.healing = healing
        
        # Load properties from category if it's a weapon or armor
        if category in WEAPON_CATEGORIES:
            weapon_data = WEAPON_CATEGORIES[category]
            self.damage_dice = weapon_data["damage_dice"]
            self.damage_sides = weapon_data["damage_sides"]
            self.cost = weapon_data["cost"]
            self.properties = weapon_data["properties"]
            self.item_type = weapon_data["item_type"]
            self.equip_slot = weapon_data["equip_slot"]
        elif category in ARMOR_CATEGORIES:
            armor_data = ARMOR_CATEGORIES[category]
            self.ac_bonus = armor_data["ac_bonus"]
            self.cost = armor_data["cost"]
            self.properties = armor_data["properties"]
            self.item_type = armor_data["item_type"]
            self.equip_slot = armor_data["equip_slot"]
            # Convert AC bonus to bonuses dict for compatibility
            self.bonuses = {"ac": armor_data["ac_bonus"]}
        else:
            # Non-category items (consumables, misc)
            self.damage_dice = None
            self.damage_sides = None
            self.cost = 0
            self.properties = []

class MagicItem(Item):
    """Special class for magic items with enhanced properties."""
    def __init__(self, name, base_category, magic_bonus, description="", special_properties=None):
        super().__init__(name, base_category, description)
        self.magic_bonus = magic_bonus
        self.is_magical = True
        self.special_properties = special_properties or []
        
        # Apply magic bonus to appropriate stats
        if hasattr(self, 'damage_dice'):  # Weapon
            if 'attack' not in self.bonuses:
                self.bonuses['attack'] = 0
            if 'damage' not in self.bonuses:
                self.bonuses['damage'] = 0
            self.bonuses['attack'] += magic_bonus
            self.bonuses['damage'] += magic_bonus
        elif hasattr(self, 'ac_bonus'):  # Armor
            self.bonuses['ac'] = self.ac_bonus + magic_bonus

# --- CFE Weapon Instances ---

# Simple Melee Weapons
dagger = Item("Dagger", "Simple Melee", "A sharp, double-edged blade.")
club = Item("Club", "Simple Melee", "A heavy wooden bludgeon.")

# Light Melee Weapons  
short_sword = Item("Short Sword", "Light Melee", "A simple, one-handed blade.")
mace = Item("Mace", "Light Melee", "A heavy war hammer with a flanged head.")
hand_axe = Item("Hand Axe", "Light Melee", "A small, balanced throwing axe.")

# Heavy Melee Weapons
longsword = Item("Longsword", "Heavy Melee", "A well-balanced two-handed sword.")
battle_axe = Item("Battle Axe", "Heavy Melee", "A large, two-handed axe.")
greatsword = Item("Greatsword", "Heavy Melee", "A massive two-handed blade.")

# Ranged Weapons
short_bow = Item("Short Bow", "Light Ranged", "A compact bow for quick shots.")
long_bow = Item("Long Bow", "Heavy Ranged", "A powerful longbow requiring great strength.")

# --- CFE Armor Instances ---

# Light Armor
leather_armor = Item("Leather Armor", "Light Armor", "Hardened leather plates.")
studded_leather = Item("Studded Leather", "Light Armor", "Leather reinforced with metal studs.")

# Medium Armor
scale_mail = Item("Scale Mail", "Medium Armor", "Armor made of overlapping metal scales.")
chain_mail = Item("Chain Mail", "Medium Armor", "Interlocking metal rings.")

# Heavy Armor
splint_armor = Item("Heavy Armor", "Heavy Armor", "Armor made of metal strips.")
plate_armor = Item("Plate Armor", "Heavy Armor", "Full suit of articulated metal plates.")

# Shields
wooden_shield = Item("Wooden Shield", "Shield", "A simple, round wooden shield.")
steel_shield = Item("Steel Shield", "Shield", "A reinforced metal shield.")

# --- CFE Magic Items (Templates) ---

# Booster Template - Weapons
iron_sword_plus_1 = MagicItem(
    "Iron Sword +1", "Light Melee", 1,
    "A finely crafted sword with a magical edge.",
    ["magical_weapon"]
)

# Booster Template - Armor/Accessories
ring_of_protection_plus_1 = MagicItem(
    "Ring of Protection +1", None, 1,
    "A silver ring that provides magical protection.",
    ["protection_bonus"]
)
ring_of_protection_plus_1.equip_slot = "Ring"
ring_of_protection_plus_1.bonuses = {"ac": 1, "fortitude": 1, "reflex": 1, "will": 1}
ring_of_protection_plus_1.item_type = "accessory"

# Consumable Template
health_potion = Item(
    "Potion of Healing", None,
    "A vial of glowing red liquid. Heals 2d4+2 HP.",
    item_type='consumable',
    healing=(2, 4, 2)  # (num_dice, die_size, bonus)
)

mana_potion = Item(
    "Potion of Mana", None,
    "A blue liquid that restores magical energy.",
    item_type='consumable'
)

# Utility Items
rope = Item("Rope", None, "A 50-foot coil of sturdy rope.", item_type='misc')
torch = Item("Torch", None, "A wooden torch that burns for 1 hour.", item_type='misc')
rations = Item("Rations", None, "One day's worth of preserved food.", item_type='misc')

# --- Treasure Items ---
gold_coins = Item("Gold Coins", None, "Gleaming gold pieces.", item_type='treasure')
silver_coins = Item("Silver Coins", None, "Silver pieces of various kingdoms.", item_type='treasure')
gems = Item("Precious Gems", None, "A collection of valuable gemstones.", item_type='treasure')

# --- Item Lists for Easy Access ---

ALL_WEAPONS = [
    dagger, club, short_sword, mace, hand_axe, 
    longsword, battle_axe, greatsword, short_bow, long_bow
]

ALL_ARMOR = [
    leather_armor, studded_leather, scale_mail, chain_mail,
    splint_armor, plate_armor, wooden_shield, steel_shield
]

ALL_MAGIC_ITEMS = [
    iron_sword_plus_1, ring_of_protection_plus_1
]

ALL_CONSUMABLES = [
    health_potion, mana_potion
]

ALL_MISC_ITEMS = [
    rope, torch, rations
]

STARTING_ITEMS = {
    "Warrior": [short_sword, leather_armor, wooden_shield, health_potion, rope],
    "Mage": [dagger, health_potion, rope, torch],
    "Expert": [short_sword, leather_armor, short_bow, health_potion, rope]
}

def create_random_treasure(value_range=(10, 100)):
    """Creates a random treasure item worth the specified gold value."""
    value = random.randint(value_range[0], value_range[1])
    
    if value < 25:
        return Item(f"{value} Silver Coins", None, f"A small pouch containing {value} silver pieces.", item_type='treasure'), value
    elif value < 100:
        return Item(f"{value} Gold Coins", None, f"A heavy purse containing {value} gold pieces.", item_type='treasure'), value
    else:
        return Item(f"Precious Gems ({value} gp)", None, f"A collection of gems worth {value} gold pieces.", item_type='treasure'), value

def get_weapons_by_proficiency(archetype):
    """Returns weapons the archetype can use."""
    if archetype == "Warrior":
        return ALL_WEAPONS  # Can use all weapons
    elif archetype == "Mage":
        return [dagger, club]  # Simple weapons only
    elif archetype == "Expert":
        return [dagger, club, short_sword, mace, hand_axe, short_bow, long_bow]  # Simple + ranged
    return []

def get_armor_by_proficiency(archetype):
    """Returns armor the archetype can use."""
    if archetype == "Warrior":
        return ALL_ARMOR  # Can use all armor
    elif archetype == "Mage":
        return []  # No armor
    elif archetype == "Expert":
        return [leather_armor, studded_leather, scale_mail, chain_mail, wooden_shield, steel_shield]  # Light + medium
    return []