# items.py

class Item:
    """A base class for all items."""
    def __init__(self, name, description="", item_type='misc', equip_slot=None, bonuses=None, healing=None, damage_dice=None, damage_sides=None):
        self.name = name
        self.description = description
        self.item_type = item_type
        self.equip_slot = equip_slot
        self.bonuses = bonuses if bonuses else {}
        self.healing = healing
        self.damage_dice = damage_dice
        self.damage_sides = damage_sides

# --- Item Definitions ---

# Consumables
health_potion = Item("Health Potion", "A vial of glowing red liquid. Heals 1d8 HP.", item_type='consumable', healing=(1,8))

# Misc
rope = Item("Rope", "A 50-foot coil of sturdy rope.", item_type='misc')

# Weapons
short_sword = Item("Short Sword", "A simple, one-handed blade.", item_type='weapon', equip_slot='Weapon', damage_dice=1, damage_sides=6)
iron_sword = Item("Iron Sword", "A well-made iron sword.", item_type='weapon', equip_slot='Weapon', damage_dice=1, damage_sides=8, bonuses={'attack': 1})

# Armor
leather_armor = Item("Leather Armor", "Hardened leather plates.", item_type='armor', equip_slot='Armor', bonuses={'ac': 2})
wooden_shield = Item("Wooden Shield", "A simple, round shield.", item_type='armor', equip_slot='Shield', bonuses={'ac': 1})
