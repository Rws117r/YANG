# config.py - Updated for Core Fantasy Engine
import pygame

# --- Screen and Display ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
ASPECT_RATIO = 16 / 9
FPS = 60
FONT_NAME = 'JetBrainsMonoNerdFontMono-Regular.ttf'
FONT_SIZE = 20
TILE_WIDTH = 12 
TILE_HEIGHT = 20

# --- Colors ---
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREY = (128, 128, 128)
COLOR_PLAYER = (255, 255, 0)
COLOR_GOBLIN = (100, 255, 100)
COLOR_SKELETON = (230, 230, 230)
COLOR_ORC = (255, 100, 100)
COLOR_SELECTED = (255, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_BROWN = (139, 69, 19)
COLOR_GOLD = (255, 215, 0)
COLOR_NPC = (0, 255, 255) # Cyan for NPCs
COLOR_ACTIVE_TAB = (0, 0, 0) # Black for active tab background
COLOR_INACTIVE_TAB = (0, 0, 0) # Black for inactive tabs as well
COLOR_FOCUS_BORDER = (255, 255, 0) # Yellow to show input focus
COLOR_HP_BAR = (200, 0, 0) # Red for health
COLOR_XP_BAR = (0, 200, 200) # Cyan for experience
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_PURPLE = (128, 0, 128)

# --- World Tile Colors ---
COLOR_DEEP_WATER = (0, 0, 100)
COLOR_SHALLOW_WATER = (25, 100, 150)
COLOR_SAND = (194, 178, 128)
COLOR_GRASS = (50, 150, 50)
COLOR_FOREST = (30, 110, 30)
COLOR_MOUNTAIN = (120, 120, 120)
COLOR_FARMLAND = (181, 147, 91)
COLOR_RUINS = (90, 90, 90)
COLOR_GATEWAY = (255, 0, 255)
COLOR_CORRUPT_FOREST = (120, 40, 150)
COLOR_SCORCHED = (50, 50, 50)
COLOR_GRAVESTONE = (110, 110, 110)
COLOR_PATH = (139, 119, 101)
COLOR_BUILDING = (160, 82, 45)
COLOR_FLOWER_YELLOW = (255, 255, 0)
COLOR_FLOWER_PINK = (255, 105, 180)
COLOR_TILLED_EARTH = (118, 86, 56)

# --- Map Characters ---
WALL_CHAR = '#'
FLOOR_CHAR = '.'
WATER_CHAR = '~'
FOREST_CHAR = 'T'
MOUNTAIN_CHAR = '^'
RUIN_CHAR = 'n'
DUNGEON_ENTRANCE_CHAR = '>'
TOWER_CHAR = 'I'
VILLAGE_CHAR = 'V'
LAIR_ENTRANCE_CHAR = 'O'
GRAVESTONE_CHAR = '+'
BURNT_TREE_CHAR = 't'
PATH_CHAR = ','
BUILDING_CHAR = 'B'
EXIT_CHAR = '<'
FLOWER_CHAR = '*'
FARMSTEAD_CHAR = '\U000F0B5E'
CROW_CHAR = '\uEDEA'
TILLED_EARTH_CHAR = '\U000F1AB2'
TENT_CHAR = '\uEEEC'
CAMPFIRE_CHAR = '\U000F0EDD'
SPIKE_BARRIER_CHAR = '\U000F1845'
TREASURE_CHEST_CHAR = '\U000F0726'
DENSE_TREE_CHAR = '\U000F1897'
NPC_CHAR = '&'
DOOR_CHAR = '+'

# --- UI Icons ---
EQUIPMENT_ICON = "\U000F18BE"
INVENTORY_ICON = "\U000F0E10"
SPELLS_ICON = "\U000F1477"
QUESTS_ICON = "\uEF0D"
CHARACTER_SHEET_ICON = "\U000F0128"
LOCATIONS_ICON = "\uEE69"
GOLD_ICON = "\uE26B"

# --- CFE Archetype Data ---
ARCHETYPES = {
    "Warrior": {
        "hp_die": 10,
        "attack_bonus_start": 1,
        "proficiencies": "All weapons, all armor, shields",
        "core_ability": "Power Attack"
    },
    "Mage": {
        "hp_die": 4,
        "attack_bonus_start": 0,
        "proficiencies": "Simple weapons only",
        "core_ability": "Spellcasting"
    },
    "Expert": {
        "hp_die": 6,
        "attack_bonus_start": 0,
        "proficiencies": "Light/medium armor, simple/ranged weapons",
        "core_ability": "Skill Expertise"
    }
}

# --- CFE Equipment Categories ---
WEAPON_CATEGORIES = {
    "Simple Melee": {
        "damage_dice": 1,
        "damage_sides": 4,
        "cost": 2,
        "properties": [],
        "item_type": "weapon",
        "equip_slot": "Weapon"
    },
    "Light Melee": {
        "damage_dice": 1,
        "damage_sides": 6,
        "cost": 10,
        "properties": [],
        "item_type": "weapon",
        "equip_slot": "Weapon"
    },
    "Heavy Melee": {
        "damage_dice": 1,
        "damage_sides": 8,
        "cost": 20,
        "properties": ["two_handed"],
        "item_type": "weapon",
        "equip_slot": "Weapon"
    },
    "Light Ranged": {
        "damage_dice": 1,
        "damage_sides": 6,
        "cost": 25,
        "properties": ["two_handed"],
        "item_type": "weapon",
        "equip_slot": "Weapon"
    },
    "Heavy Ranged": {
        "damage_dice": 1,
        "damage_sides": 8,
        "cost": 40,
        "properties": ["two_handed", "slow"],
        "item_type": "weapon",
        "equip_slot": "Weapon"
    }
}

ARMOR_CATEGORIES = {
    "Light Armor": {
        "ac_bonus": 2,  # Base AC 12 (10 + 2)
        "cost": 20,
        "properties": [],
        "item_type": "armor",
        "equip_slot": "Armor"
    },
    "Medium Armor": {
        "ac_bonus": 4,  # Base AC 14 (10 + 4)
        "cost": 50,
        "properties": ["stealth_disadvantage"],
        "item_type": "armor",
        "equip_slot": "Armor"
    },
    "Heavy Armor": {
        "ac_bonus": 6,  # Base AC 16 (10 + 6)
        "cost": 100,
        "properties": ["stealth_disadvantage"],
        "item_type": "armor",
        "equip_slot": "Armor"
    },
    "Shield": {
        "ac_bonus": 1,
        "cost": 10,
        "properties": [],
        "item_type": "armor",
        "equip_slot": "Shield"
    }
}

# --- CFE Monster Templates ---
MONSTER_TEMPLATES = {
    "Goblin": {
        "name": "Goblin",
        "char": "g",
        "color": COLOR_GOBLIN,
        "hp": 7,
        "ac": 13,
        "attack_bonus": 1,
        "damage_dice": 1,
        "damage_sides": 6,
        "speed": 30,
        "xp_value": 25,
        "special_abilities": ["horde_tactics"]
    },
    "Skeleton": {
        "name": "Skeleton",
        "char": "s",
        "color": COLOR_SKELETON,
        "hp": 13,
        "ac": 12,
        "attack_bonus": 2,
        "damage_dice": 1,
        "damage_sides": 8,
        "speed": 30,
        "xp_value": 50,
        "special_abilities": ["undead_nature", "blunt_vulnerability"]
    },
    "Ogre": {
        "name": "Ogre",
        "char": "O",
        "color": COLOR_ORC,
        "hp": 29,
        "ac": 11,
        "attack_bonus": 4,
        "damage_dice": 2,
        "damage_sides": 8,
        "speed": 40,
        "xp_value": 200,
        "special_abilities": ["brute_strength"]
    },
    "Giant Spider": {
        "name": "Giant Spider",
        "char": "S",
        "color": COLOR_BLACK,
        "hp": 22,
        "ac": 14,
        "attack_bonus": 3,
        "damage_dice": 1,
        "damage_sides": 8,
        "speed": 30,
        "xp_value": 150,
        "special_abilities": ["poison_bite"]
    }
}

# --- CFE Unified Level Progression ---
LEVEL_PROGRESSION = {
    1: {"xp_required": 0},
    2: {"xp_required": 2000},
    3: {"xp_required": 4000},
    4: {"xp_required": 8000},
    5: {"xp_required": 16000}
}

# --- CFE Spell Slot Progression ---
SPELL_SLOTS_BY_LEVEL = {
    1: {1: 2, 2: 0, 3: 0},
    2: {1: 3, 2: 0, 3: 0},
    3: {1: 3, 2: 2, 3: 0},
    4: {1: 3, 2: 3, 3: 0},
    5: {1: 3, 2: 3, 3: 2}
}