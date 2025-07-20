# world_generation.py
import noise
import numpy as np
import random
from config import *
from entities import Monster, Crow, NPC
from quest import Quest

# --- MODIFICATION: Add missing color definitions to resolve NameError ---
COLOR_FLOWER_YELLOW = (255, 255, 0)
COLOR_FLOWER_PINK = (255, 105, 180)
COLOR_DUNGEON_WALL = (80, 80, 80)
COLOR_DUNGEON_FLOOR = (40, 40, 40)

# --- MODIFICATION: Override characters from config.py with Unicode glyphs ---
VILLAGE_CHAR = "\U000F0DD4"
BUILDING_CHAR = "\U000F02DC"
TOWER_CHAR = "\uE263"
DUNGEON_ENTRANCE_CHAR = "\U000F183E"
FOREST_CHAR = "\U000F0405"
GRAVESTONE_CHAR = "\U000F0BA2"
FLOWER_CHAR = "\U000F024A"
FARMSTEAD_CHAR = "\U000F0B5E"
CROW_CHAR = "\uEDEA"
TILLED_EARTH_CHAR = "\U000F1AB2"
TENT_CHAR = "\uEEEC"
CAMPFIRE_CHAR = "\U000F0EDD"
SPIKE_BARRIER_CHAR = "\U000F1845"
MOUNTAIN_CHAR = "\uE2A6"
TREASURE_CHEST_CHAR = "\U000F0726"
DENSE_TREE_CHAR = "\U000F1897"


class Tile:
    """A tile on the map. It may or may not be blocked."""
    def __init__(self, blocked, char=' ', color=COLOR_WHITE, name="tile", glyph_color=None):
        self.blocked = blocked
        self.char = char
        self.color = color
        self.name = name
        self.glyph_color = glyph_color
        self.is_interactive = (name == "a chest") # Mark chests as interactive
        self.explored = False
        self.is_gateway_to = None # Links to a Place object
        self.is_exit = False # Marks a tile as an exit back to a previous map

class Place:
    """Represents a significant location on the map, like a village or dungeon."""
    def __init__(self, x, y, name, gateway_char, generator_func):
        self.x = x
        self.y = y
        self.name = name
        self.gateway_char = gateway_char
        self.generator_func = generator_func
        self.generated_map = None
        self.player_start_pos = None

def _create_path(game_map, x1, y1, x2, y2):
    """Creates an L-shaped path between two points."""
    for x in range(min(x1, x2), max(x1, x2) + 1):
        if game_map[x, y1].name == "grass":
            game_map[x, y1] = Tile(False, ' ', COLOR_PATH, "a path")
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if game_map[x2, y].name == "grass":
            game_map[x2, y] = Tile(False, ' ', COLOR_PATH, "a path")

def generate_dungeon(width, height):
    """Generates a simple dungeon map using a random walk algorithm."""
    game_map = np.full((width, height), fill_value=Tile(True, ' ', COLOR_DUNGEON_WALL, "stone wall"))
    entities = []
    
    max_tunnels = 50
    max_length = 8
    
    x, y = width // 2, height // 2
    game_map[x,y] = Tile(False, FLOOR_CHAR, COLOR_DUNGEON_FLOOR, "dungeon floor")
    
    for _ in range(max_tunnels):
        length = random.randint(1, max_length)
        dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
        for _ in range(length):
            x, y = x + dx, y + dy
            if 1 <= x < width -1 and 1 <= y < height -1:
                game_map[x,y] = Tile(False, FLOOR_CHAR, COLOR_DUNGEON_FLOOR, "dungeon floor")
            else:
                break # Hit map edge
    
    # Add exit
    exit_x, exit_y = width // 2, height // 2
    game_map[exit_x, exit_y] = Tile(False, EXIT_CHAR, COLOR_GATEWAY, "path to the overworld")
    game_map[exit_x, exit_y].is_exit = True
    player_start = (exit_x + 1, exit_y)

    # Add monsters
    for _ in range(10):
        mx, my = random.randint(1, width-2), random.randint(1, height-2)
        if game_map[mx, my].name == "dungeon floor":
            entities.append(Monster(mx, my, 's', COLOR_SKELETON, "Skeleton", 13, 12, 2, 50))

    return game_map, player_start, entities, []


# Updated generate_village function for world_generation.py

def generate_village(width, height):
    """Generates a small village map with a central square and specific buildings."""
    game_map = np.full((width, height), fill_value=None, order='F')
    entities = []
    
    # Create grass base
    for x in range(width):
        for y in range(height):
            game_map[x, y] = Tile(False, ' ', COLOR_GRASS, "grass")

    # Create forest border
    for x in range(width):
        game_map[x, 0] = Tile(True, DENSE_TREE_CHAR, COLOR_GRASS, "forest", glyph_color=COLOR_FOREST)
        game_map[x, height - 1] = Tile(True, DENSE_TREE_CHAR, COLOR_GRASS, "forest", glyph_color=COLOR_FOREST)
    for y in range(height):
        game_map[0, y] = Tile(True, DENSE_TREE_CHAR, COLOR_GRASS, "forest", glyph_color=COLOR_FOREST)
        game_map[width - 1, y] = Tile(True, DENSE_TREE_CHAR, COLOR_GRASS, "forest", glyph_color=COLOR_FOREST)

    # Create central town square
    square_x, square_y = width // 2, height // 2
    for i in range(-1, 2):
        for j in range(-1, 2):
            game_map[square_x + i, square_y + j] = Tile(False, ' ', COLOR_PATH, "town square")
    
    # Define specific building locations and details
    specific_buildings = [
        {
            "name": "The Salty Siren",
            "description": "a cozy inn",
            "glyph": "\uee18",  # 0xee18
            "position": (square_x - 8, square_y - 5),
            "npc": None
        },
        {
            "name": "Torvin's Smithy", 
            "description": "a busy smithy",
            "glyph": "\uf27c",  # 0xf27c
            "position": (square_x + 8, square_y - 3),
            "npc": NPC(square_x + 8, square_y - 2, "Torvin the Smith", "Welcome to my smithy! I can craft and repair weapons and armor.")
        },
        {
            "name": "The Elder's Hut",
            "description": "the elder's dwelling", 
            "glyph": "\ueed7",  # 0xeed7
            "position": (square_x - 3, square_y + 8),
            "npc": None  # Elder Maeve will be placed in the square
        }
    ]
    
    building_doors = []
    
    # Place specific buildings
    for building in specific_buildings:
        bx, by = building["position"]
        
        # Ensure building is within map bounds
        if 2 <= bx <= width - 3 and 2 <= by <= height - 3:
            # Place the building
            game_map[bx, by] = Tile(True, building["glyph"], COLOR_BUILDING, building["description"], glyph_color=COLOR_BROWN)
            
            # Create door in front of building
            door_x, door_y = bx, by + 1
            if door_y < height - 1:
                game_map[door_x, door_y] = Tile(False, ' ', COLOR_GRASS, "grass")
                building_doors.append((door_x, door_y))
            
            # Add NPC if specified
            if building["npc"]:
                # Adjust NPC position to be near the door
                npc = building["npc"]
                npc.x, npc.y = door_x, door_y
                entities.append(npc)
    
    # Add a few more random buildings to fill out the village
    for _ in range(3):
        placed = False
        attempts = 0
        while not placed and attempts < 50:
            attempts += 1
            bx, by = random.randint(5, width - 6), random.randint(5, height - 6)
            
            # Make sure it's not too close to the square or existing buildings
            if abs(bx - square_x) < 6 and abs(by - square_y) < 6:
                continue
                
            # Check if position is clear
            if game_map[bx, by].name == "grass":
                game_map[bx, by] = Tile(True, BUILDING_CHAR, COLOR_BUILDING, "a building")
                door_x, door_y = bx, by + 1
                if door_y < height - 1:
                    game_map[door_x, door_y] = Tile(False, ' ', COLOR_GRASS, "grass")
                    building_doors.append((door_x, door_y))
                placed = True

    # Create exit
    exit_x, exit_y = 1, height // 2
    game_map[exit_x, exit_y] = Tile(False, EXIT_CHAR, COLOR_GATEWAY, "path to the wilderness")
    game_map[exit_x, exit_y].is_exit = True
    
    # Create paths from buildings to town square and from square to exit
    for door_x, door_y in building_doors:
        _create_path(game_map, door_x, door_y, square_x, square_y)
        
    _create_path(game_map, square_x, square_y, exit_x, exit_y)

    # Place Elder Maeve in the town square with her quest
    serpent_quest = Quest("The Serpent Temple", "Investigate the strange happenings at the temple.", ["Find the temple", "Defeat the priestess"])
    entities.append(NPC(square_x, square_y, "Elder Maeve", "The Serpent Temple stirs... Please help us!", quest=serpent_quest))

    player_start = (exit_x + 1, exit_y)
    
    return game_map, player_start, entities, []

def generate_overworld(width, height):
    """Generates a new overworld map using Perlin noise and places."""
    game_map = np.full((width, height), fill_value=None, order='F')
    places = []
    monsters = []
    
    # --- Step 1: Generate Base Terrain ---
    scale, octaves, persistence, lacunarity = 100.0, 6, 0.5, 2.0
    seed = np.random.randint(0, 100)
    for i in range(width):
        for j in range(height):
            value = noise.pnoise2(i / scale, j / scale, octaves, persistence, lacunarity, base=seed)
            if value < -0.2: game_map[i][j] = Tile(True, WATER_CHAR, COLOR_DEEP_WATER, "deep water")
            elif value < -0.1: game_map[i][j] = Tile(True, WATER_CHAR, COLOR_SHALLOW_WATER, "shallow water")
            elif value < 0.0: game_map[i][j] = Tile(False, ' ', COLOR_SAND, "sand")
            elif value < 0.3: game_map[i][j] = Tile(False, ' ', COLOR_GRASS, "grass")
            elif value < 0.5: game_map[i][j] = Tile(False, DENSE_TREE_CHAR, COLOR_GRASS, "forest", glyph_color=COLOR_FOREST)
            else: game_map[i][j] = Tile(True, MOUNTAIN_CHAR, COLOR_MOUNTAIN, "mountain", glyph_color=COLOR_GREY)

    # --- Step 1.5: Populate Plains with Features ---
    for i in range(width):
        for j in range(height):
            if game_map[i, j].name == "grass":
                if random.random() < 0.005:
                    feature_type = random.choice(["pond", "rocks", "flowers"])
                    if feature_type == "pond":
                        pond_radius = random.randint(1, 2)
                        for px in range(-pond_radius, pond_radius + 1):
                            for py in range(-pond_radius, pond_radius + 1):
                                if px*px + py*py < pond_radius*pond_radius and 0 <= i+px < width and 0 <= j+py < height:
                                    game_map[i+px, j+py] = Tile(True, WATER_CHAR, COLOR_SHALLOW_WATER, "a small pond")
                    elif feature_type == "rocks":
                        for _ in range(random.randint(1, 4)):
                            rx, ry = i + random.randint(-2, 2), j + random.randint(-2, 2)
                            if 0 <= rx < width and 0 <= ry < height and game_map[rx, ry].name == "grass":
                                game_map[rx, ry] = Tile(True, MOUNTAIN_CHAR, COLOR_GRASS, "a rock", glyph_color=COLOR_GREY)
                    elif feature_type == "flowers":
                        for _ in range(random.randint(5, 15)):
                            fx, fy = i + random.randint(-3, 3), j + random.randint(-3, 3)
                            if 0 <= fx < width and 0 <= fy < height and game_map[fx, fy].name == "grass":
                                game_map[fx, fy] = Tile(False, FLOWER_CHAR, COLOR_GRASS, "wildflowers", glyph_color=COLOR_FLOWER_YELLOW)

    # --- Step 2: Place Destinations and Landmarks ---
    place_definitions = {
        "Lone Farmstead": {"count": 2, "terrain": ["grass"], "landmark": "tilled_earth", "gateway": FARMSTEAD_CHAR, "generator": None},
        "Bandit Camp": {"count": 3, "terrain": ["grass", "sand"], "landmark": "bandit_camp", "gateway": None, "generator": None},
        "Saltwind Village": {"count": 1, "terrain": ["grass"], "landmark": "farmland", "gateway": VILLAGE_CHAR, "generator": generate_village},
        "Ancient Crypt": {"count": 2, "terrain": ["forest"], "landmark": "graveyard", "gateway": DUNGEON_ENTRANCE_CHAR, "generator": generate_dungeon},
        "Mage Tower": {"count": 1, "terrain": ["forest"], "landmark": "corrupt_forest", "gateway": TOWER_CHAR, "generator": None},
        "Dragon's Lair": {"count": 1, "terrain": ["mountain"], "landmark": "scorched_earth", "gateway": LAIR_ENTRANCE_CHAR, "generator": None}
    }

    for name, definition in place_definitions.items():
        for _ in range(definition["count"]):
            placed = False
            attempts = 0
            while not placed and attempts < 200:
                attempts += 1
                x, y = random.randint(10, width - 11), random.randint(10, height - 11)
                
                if game_map[x, y].name in definition["terrain"]:
                    
                    if definition["landmark"] == "tilled_earth":
                        field_size = 3
                        for i in range(x - field_size - 1, x - 1):
                            for j in range(y - field_size - 1, y - 1):
                                game_map[i,j] = Tile(False, TILLED_EARTH_CHAR, COLOR_TILLED_EARTH, "tilled earth", glyph_color=COLOR_BROWN)
                        for i in range(x + 2, x + field_size + 2):
                            for j in range(y - field_size - 1, y - 1):
                                game_map[i,j] = Tile(False, TILLED_EARTH_CHAR, COLOR_TILLED_EARTH, "tilled earth", glyph_color=COLOR_BROWN)
                        for i in range(x - field_size - 1, x - 1):
                            for j in range(y + 2, y + field_size + 2):
                                game_map[i,j] = Tile(False, TILLED_EARTH_CHAR, COLOR_TILLED_EARTH, "tilled earth", glyph_color=COLOR_BROWN)
                        for i in range(x + 2, x + field_size + 2):
                            for j in range(y + 2, y + field_size + 2):
                                game_map[i,j] = Tile(False, TILLED_EARTH_CHAR, COLOR_TILLED_EARTH, "tilled earth", glyph_color=COLOR_BROWN)
                        for _ in range(random.randint(1,2)):
                            monsters.append(Crow(x + random.randint(-4,4), y + random.randint(-4,4)))

                    elif definition["landmark"] == "bandit_camp":
                        landmark_radius = random.randint(3, 4)
                        opening_side = random.choice(['n', 's', 'e', 'w'])
                        
                        for i in range(-landmark_radius, landmark_radius + 1):
                            if not (opening_side == 'n' and i in [-1, 0, 1]):
                                game_map[x+i, y-landmark_radius] = Tile(True, SPIKE_BARRIER_CHAR, COLOR_GRASS, "a spike barrier", glyph_color=COLOR_BLACK)
                            if not (opening_side == 's' and i in [-1, 0, 1]):
                                game_map[x+i, y+landmark_radius] = Tile(True, SPIKE_BARRIER_CHAR, COLOR_GRASS, "a spike barrier", glyph_color=COLOR_BLACK)
                        for i in range(-landmark_radius + 1, landmark_radius):
                            if not (opening_side == 'w' and i in [-1, 0, 1]):
                                game_map[x-landmark_radius, y+i] = Tile(True, SPIKE_BARRIER_CHAR, COLOR_GRASS, "a spike barrier", glyph_color=COLOR_BLACK)
                            if not (opening_side == 'e' and i in [-1, 0, 1]):
                                game_map[x+landmark_radius, y+i] = Tile(True, SPIKE_BARRIER_CHAR, COLOR_GRASS, "a spike barrier", glyph_color=COLOR_BLACK)
                        
                        game_map[x,y] = Tile(False, CAMPFIRE_CHAR, COLOR_GRASS, "a campfire", glyph_color=COLOR_RED)
                        game_map[x, y-landmark_radius+1] = Tile(False, TREASURE_CHEST_CHAR, COLOR_GRASS, "a chest", glyph_color=COLOR_GOLD)

                        for _ in range(random.randint(2,3)):
                            tx, ty = x + random.randint(-landmark_radius+1, landmark_radius-1), y + random.randint(-landmark_radius+1, landmark_radius-1)
                            if game_map[tx,ty].name == "grass":
                                game_map[tx,ty] = Tile(True, TENT_CHAR, COLOR_GRASS, "a crude tent", glyph_color=COLOR_BLACK)
                        for _ in range(random.randint(3,5)):
                            monsters.append(Monster(x + random.randint(-landmark_radius+1, landmark_radius-1), y + random.randint(-landmark_radius+1, landmark_radius-1), 'b', COLOR_RED, "Bandit", 8, 12, 1, 20))

                    else:
                        landmark_radius = random.randint(5, 8)
                        for i in range(-landmark_radius, landmark_radius + 1):
                            for j in range(-landmark_radius, landmark_radius + 1):
                                if i*i + j*j < landmark_radius*landmark_radius:
                                    lx, ly = x + i, y + j
                                    if 0 <= lx < width and 0 <= ly < height and not game_map[lx, ly].blocked:
                                        if definition["landmark"] == "graveyard":
                                            if random.random() < 0.1:
                                                game_map[lx, ly] = Tile(False, GRAVESTONE_CHAR, COLOR_GRASS, "gravestone", glyph_color=COLOR_GRAVESTONE)
                    if definition["gateway"]:
                        bg_color = game_map[x,y].color
                        glyph_color = COLOR_RED if name == "Lone Farmstead" else COLOR_GATEWAY
                        place = Place(x, y, name, definition["gateway"], definition["generator"])
                        places.append(place)
                        game_map[x, y] = Tile(False, place.gateway_char, bg_color, f"entrance to {name}", glyph_color=glyph_color)
                        game_map[x, y].is_gateway_to = place
                    placed = True

    # --- Step 3: Find Player Start ---
    player_start = (0,0)
    for place in places:
        if place.name == "Saltwind Village":
            player_start = (place.x, place.y)
            break
    if player_start == (0,0):
        while True:
            x, y = random.randint(0, width-1), random.randint(0, height-1)
            if not game_map[x,y].blocked:
                player_start = (x,y)
                break

    return game_map, player_start, monsters, places
