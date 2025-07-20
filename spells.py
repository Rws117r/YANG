# spells.py - Core Fantasy Engine Magic System (Updated)
import random
from config import *

def roll_dice(num_dice, sides):
    """Rolls a number of dice with a given number of sides."""
    return sum(random.randint(1, sides) for _ in range(num_dice))

class Spell:
    """Represents a single spell with all its properties and effects."""
    def __init__(self, name, level, range_ft, duration, description, effect_func, target_type="single", save_type=None, save_dc=None):
        self.name = name
        self.level = level
        self.range = range_ft
        self.duration = duration
        self.description = description
        self.effect = effect_func
        self.target_type = target_type  # "single", "area", "self", "touch"
        self.save_type = save_type  # "fortitude", "reflex", "will", None
        self.save_dc = save_dc

# --- Spell Effect Functions ---

def cast_light(caster, target, game_engine=None):
    """Creates a magical light source."""
    if game_engine:
        game_engine.add_message("A magical light illuminates the area.", COLOR_WHITE)
    return "You create a magical light that illuminates a 30-foot radius."

def cast_magic_missile(caster, target, game_engine=None):
    """Automatically hitting magical dart."""
    if not target:
        return "Magic Missile requires a target!"
    
    damage = roll_dice(1, 4) + 1
    target.take_damage(damage)
    
    if game_engine:
        game_engine.add_message(f"Magic missile hits {target.name} for {damage} force damage!", COLOR_PURPLE)
    
    return f"Magic missile strikes {target.name} for {damage} force damage!"

def cast_shield(caster, target, game_engine=None):
    """Grants AC bonus to the caster."""
    # Apply shield effect (in full implementation, this would be a temporary effect)
    if hasattr(caster, 'temporary_ac_bonus'):
        caster.temporary_ac_bonus += 2
    else:
        caster.temporary_ac_bonus = 2
    
    if game_engine:
        game_engine.add_message("A shimmering magical barrier appears around you.", COLOR_BLUE)
    
    return "A magical shield grants you +2 Armor Class for 5 minutes."

def cast_sleep(caster, target, game_engine=None):
    """Puts creatures to sleep in an area."""
    if not target:
        return "Sleep requires a target area!"
    
    # Simplified: affects single target with < 4 HD
    if hasattr(target, 'hp') and target.hp <= 32:  # Roughly 4 HD worth
        target.sleeping = True
        if game_engine:
            game_engine.add_message(f"{target.name} falls into a magical sleep!", COLOR_PURPLE)
        return f"{target.name} falls asleep!"
    else:
        if game_engine:
            game_engine.add_message(f"{target.name} resists the sleep effect.", COLOR_GREY)
        return f"{target.name} is too powerful to be affected by sleep."

def cast_invisibility(caster, target, game_engine=None):
    """Makes target invisible."""
    target_creature = target if target else caster
    target_creature.invisible = True
    
    if game_engine:
        name = target_creature.name if target else "You"
        game_engine.add_message(f"{name} become{'s' if target else ''} invisible!", COLOR_PURPLE)
    
    return f"{'You become' if not target else target.name + ' becomes'} invisible for 10 minutes."

def cast_scorching_ray(caster, target, game_engine=None):
    """Fires a ray of fire requiring an attack roll."""
    if not target:
        return "Scorching Ray requires a target!"
    
    # Make attack roll using caster's spell attack bonus
    attack_roll = roll_dice(1, 20) + caster.spell_attack_bonus
    
    if attack_roll >= target.ac:
        damage = roll_dice(3, 6)
        target.take_damage(damage)
        if game_engine:
            game_engine.add_message(f"Scorching ray hits {target.name} for {damage} fire damage!", COLOR_RED)
        return f"Scorching ray burns {target.name} for {damage} fire damage!"
    else:
        if game_engine:
            game_engine.add_message(f"Scorching ray misses {target.name}.", COLOR_GREY)
        return f"Scorching ray misses {target.name}."

def cast_web(caster, target, game_engine=None):
    """Creates sticky webs in an area."""
    if not target:
        return "Web requires a target area!"
    
    # Make Reflex save
    save_roll = roll_dice(1, 20) + getattr(target, 'reflex_save', 0)
    save_dc = 12 + caster.modifiers.get('INT', 0)
    
    if save_roll < save_dc:
        target.restrained = True
        if game_engine:
            game_engine.add_message(f"{target.name} is caught in sticky webs!", COLOR_GREEN)
        return f"{target.name} is restrained by sticky webs!"
    else:
        if game_engine:
            game_engine.add_message(f"{target.name} dodges the web!", COLOR_GREY)
        return f"{target.name} avoids the web."

def cast_fireball(caster, target, game_engine=None):
    """Creates a fiery explosion."""
    if not target:
        return "Fireball requires a target area!"
    
    # Area effect - simplified to single target for MVP
    save_roll = roll_dice(1, 20) + getattr(target, 'reflex_save', 0)
    save_dc = 12 + caster.modifiers.get('INT', 0)
    
    damage = roll_dice(6, 6)
    if save_roll >= save_dc:
        damage = damage // 2  # Half damage on successful save
        save_msg = "takes half damage"
    else:
        save_msg = "takes full damage"
    
    target.take_damage(damage)
    
    if game_engine:
        game_engine.add_message(f"Fireball explodes! {target.name} {save_msg} ({damage} fire damage)!", COLOR_RED)
    
    return f"Fireball deals {damage} fire damage to {target.name}!"

def cast_fly(caster, target, game_engine=None):
    """Grants flight to target."""
    target_creature = target if target else caster
    target_creature.flying = True
    
    if game_engine:
        name = target_creature.name if target else "You"
        game_engine.add_message(f"{name} {'gains' if target else 'gain'} the power of flight!", COLOR_BLUE)
    
    return f"{'You gain' if not target else target.name + ' gains'} the ability to fly for 10 minutes."

def cast_haste(caster, target, game_engine=None):
    """Makes target faster and more effective in combat."""
    if not target:
        target = caster
    
    target.hasted = True
    if hasattr(target, 'temporary_ac_bonus'):
        target.temporary_ac_bonus += 1
    else:
        target.temporary_ac_bonus = 1
    
    if game_engine:
        name = target.name if target != caster else "You"
        game_engine.add_message(f"{name} {'begins' if target != caster else 'begin'} moving with supernatural speed!", COLOR_GOLD)
    
    return f"{'You are' if target == caster else target.name + ' is'} hasted! +1 AC and extra actions."

# --- The Core Spell Dictionary ---
CORE_SPELLS = {
    "Light": Spell(
        "Light", 1, 60, "1 hour",
        "Creates a magical light source on an object or creature, illuminating a 30' radius.",
        cast_light, "self"
    ),
    "Magic Missile": Spell(
        "Magic Missile", 1, 150, "Instant",
        "Fires a dart of magical energy that automatically hits one visible target, dealing 1d4+1 force damage.",
        cast_magic_missile, "single"
    ),
    "Shield": Spell(
        "Shield", 1, None, "5 min",
        "A magical barrier grants the caster a +2 bonus to their Armor Class.",
        cast_shield, "self"
    ),
    "Sleep": Spell(
        "Sleep", 1, 120, "1 min",
        "Puts 2d8 Hit Dice of creatures to sleep in a 30' area. Creatures with more than 4 HD are unaffected.",
        cast_sleep, "single"
    ),
    "Invisibility": Spell(
        "Invisibility", 2, None, "10 min",
        "Touched creature becomes invisible. The spell ends if the creature attacks or casts a spell.",
        cast_invisibility, "self"
    ),
    "Scorching Ray": Spell(
        "Scorching Ray", 2, 90, "Instant",
        "Hurls a ray of fire at a target. Requires an attack roll. On a hit, deals 3d6 fire damage.",
        cast_scorching_ray, "single"
    ),
    "Web": Spell(
        "Web", 2, 60, "10 min",
        "Creates a 20' cube of sticky webs. Creatures in the area must make a Reflex save or become restrained.",
        cast_web, "single"
    ),
    "Fireball": Spell(
        "Fireball", 3, 150, "Instant",
        "A fiery explosion in a 20' radius. All creatures in the area take 6d6 fire damage (Reflex save for half).",
        cast_fireball, "area"
    ),
    "Fly": Spell(
        "Fly", 3, None, "10 min",
        "Touched creature gains the ability to fly at its normal movement speed.",
        cast_fly, "self"
    ),
    "Haste": Spell(
        "Haste", 3, 30, "1 min",
        "One creature moves and acts twice as fast. It gains a +1 bonus to AC and can make one extra attack action on its turn.",
        cast_haste, "self"
    )
}

def get_spells_by_level(level):
    """Returns all spells of a given level."""
    return [spell for spell in CORE_SPELLS.values() if spell.level == level]

def get_spell_by_name(name):
    """Returns a spell by name, or None if not found."""
    return CORE_SPELLS.get(name)

# --- Updated Starting Spell List - ALL SPELLS FOR TESTING ---
STARTING_MAGE_SPELLS = [
    "Light", "Magic Missile", "Shield", "Sleep",           # Level 1
    "Invisibility", "Scorching Ray", "Web",                # Level 2  
    "Fireball", "Fly", "Haste"                            # Level 3
]