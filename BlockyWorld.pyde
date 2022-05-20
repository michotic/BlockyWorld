'''
Blocky World

Made by Michael Taylor for Educational Purposes

GOAL: A voxel-based world/island in which a player will be able to break & place blocks that provides a base for building more complex voxel-based worlds
'''

# ---> GLOBAL CONSTANTS <---

# For debugging
SHOW_POSITION = False

WORLD_SIZE = 10 # How many blocks long & wide our world will be (square shape for x & y axis)
WORLD_HEIGHT = 8 # World height limit (z-axis)
TILE_SIZE = 32 # How many pixels wide will our sprites be displayed as

# Displayed width and height of sprites in game window
SPRITE_W = TILE_SIZE * 1
SPRITE_H = TILE_SIZE * 2 # NOTE : *2 because our sprites are 16*32, a 1:2 ratio
SPRITE_SHEET_PATH = "SpriteSheet.png" # File directory for sprite sheet

# Size of window game will be ran in
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

# Block offset (all blocks displayed positions will be offset by these values, used to center game world on screen 
BLOCK_X_OFFSET = WINDOW_WIDTH / 2 - SPRITE_W / 2
BLOCK_Y_OFFSET = WINDOW_HEIGHT / 3

# ---> GLOBAL VARIABLES <---

# sprites dictionary data structure
# USAGE: sprites["ITEM_NAME"] -> e.g. image(sprites["grass"], 0, 0, SPRITE_W, SPRITE_H)
#                                           ---------------- 
sprites = {} # Dictionary that will map name of object represented by sprite to image of sprite, ex. {"log" : ".../log.png"}
blocks_render_groups = {} # Data structure that will contain blocks based on render order


w_key_down = False
a_key_down = False 
s_key_down = False 
d_key_down = False

# FUNCTIONS BUILT INTO PROCESSING / PROCESSING.PY

'''
The setup() function is built into Processing and will run once at the beginning of the program
We will be using it to set up the game environment
'''
def setup():
    size(WINDOW_WIDTH, WINDOW_HEIGHT) # Defines our games window as 600x600 pixels wide & tall
    noSmooth() # Disables anti-aliasing (preserves sharp edges in pixel art)
    grabSpritesFromSheet() # Load up sprites
    
    #generateBlocks(0, 0, 0, "air", WORLD_SIZE, WORLD_SIZE, WORLD_HEIGHT) # Generate empty cube/empty world
    generateEmptyWorld(0, 0, 0, WORLD_SIZE, WORLD_SIZE, WORLD_HEIGHT)
    generatePlane(0, "grass") # Make a flat layer of grass
    
    for new_tree in range(WORLD_SIZE / 2):
        x = int(random(WORLD_SIZE))
        y = int(random(WORLD_SIZE))
        generateTree(x, y, 0)
        
    #generateArtech()
    #generateGameStop()
    
    global player_obj 
    player_obj = Player(0, 0, 1) # Add player into world
    
'''
draw() is a function built into Processing, it is the main "game loop" meaning it is called every update/frame/tick in the game
'''
def draw():
    background(165, 150, 255) # Sets the background of our window to a sky-like blue. Colour is defined as (red, green, blue) all ranging from 0-255
    renderBlocks()
 
def keyTyped():
    moveVector = PVector(0, 0, 0)
    if key.lower() == "w":
        moveVector.x -= 1
    if key.lower() == "s":
        moveVector.x += 1  
    if key.lower() == "a":
        moveVector.y += 1
    if key.lower() == "d":
        moveVector.y -= 1
    if key.lower() == " ":
        moveVector.z += 1
    if key.lower() == "c":
        moveVector.z -= 1
    
    target_x = player_obj._position.x + moveVector.x
    target_y = player_obj._position.y + moveVector.y
    target_z = player_obj._position.z + moveVector.z
    
    if target_x >= 0 and target_x < WORLD_SIZE:
        if target_y >= 0 and target_y < WORLD_SIZE:
            if target_z >= 0 and target_z < WORLD_HEIGHT:
                if getBlockWithPosition(target_x, target_y, target_z)._type == "air":
                    player_obj._position.x = target_x
                    player_obj._position.y = target_y
                    player_obj._position.z = target_z
                    player_obj.updateRenderOrder()

# Renders block by render groups
def renderBlocks():
    counter = 0
    for render_group in blocks_render_groups.keys():
        if abs(player_obj._render_order - render_group) >= 0:
            for block_object in blocks_render_groups[render_group]:
                # Grabs block type and position
                type = block_object._type
                position = block_object._position
            
                # Converts blocks position data to how it will be rendered on screen
                render_position = CartesionToIsometric(position.x, position.y)
                render_x = render_position.x * (SPRITE_W / 2) + BLOCK_X_OFFSET
                render_y = render_position.y * (SPRITE_W / 2) - ((position.z / 2 * TILE_SIZE)) + BLOCK_Y_OFFSET
                
                if block_object._position.x == player_obj._position.x and block_object._position.y == player_obj._position.y and block_object._position.z == player_obj._position.z:
                    render_position = CartesionToIsometric(player_obj._position.x, player_obj._position.y)
                    render_x = render_position.x * (SPRITE_W / 2) + BLOCK_X_OFFSET
                    render_y = render_position.y * (SPRITE_W / 2) - ((position.z / 2 * TILE_SIZE)) + BLOCK_Y_OFFSET
                    image(sprites["player"], render_x, render_y, SPRITE_W, SPRITE_H)
                
                if block_object._position.x == player_obj._position.x and block_object._position.y == player_obj._position.y and block_object._position.z < player_obj._position.z:
                    render_position = CartesionToIsometric(player_obj._position.x, player_obj._position.y)
                    render_x = render_position.x * (SPRITE_W / 2) + BLOCK_X_OFFSET
                    render_y = render_position.y * (SPRITE_W / 2) - ((position.z / 2 * TILE_SIZE)) + BLOCK_Y_OFFSET
                    image(sprites["feet"], render_x, render_y, SPRITE_W, SPRITE_H)
                
                # Displays block texture corresponding to type
                if (type != "air"):
                    image(sprites[type], render_x, render_y, SPRITE_W, SPRITE_H)
                    # Displays block position if enabled
                    if (SHOW_POSITION):
                        position_string = str(position)
                        fill(0)
                        text(position_string, render_x, render_y + SPRITE_H / 1.75)
        
'''
The grabSpritesFromSheet() function creates a global sprites dictionary with assets from a sprite sheet
the sprites dictionary allows textures for in game objects to be loaded by using sprites["ITEM_NAME"] -> e.g. image(sprites["grass"], 0, 0, SPRITE_W, SPRITE_H)
'''
def grabSpritesFromSheet():
    sprite_sheet = loadImage(SPRITE_SHEET_PATH) # Loads sprite sheet from specified directory
    
    # Width and height of each sprite in the actual sprite sheet file (in pixels)
    ASSET_W = 16#256#16
    ASSET_H = 32#512#32
    
    # Assigns sprites from sprite sheet to keys
    sprites["player"] = (sprite_sheet.get(ASSET_W*0, ASSET_H*0, ASSET_W, ASSET_H))
    sprites["grass"] = (sprite_sheet.get(ASSET_W*1, ASSET_H*0, ASSET_W, ASSET_H))
    sprites["plank"] = (sprite_sheet.get(ASSET_W*2, ASSET_H*0, ASSET_W, ASSET_H))
    sprites["log"] = (sprite_sheet.get(ASSET_W*3, ASSET_H*0, ASSET_W, ASSET_H))
    sprites["leaves"] = (sprite_sheet.get(ASSET_W*0, ASSET_H*1, ASSET_W, ASSET_H))
    sprites["outline"] = (sprite_sheet.get(ASSET_W*1, ASSET_H*1, ASSET_W, ASSET_H))
    sprites["feet"] = (sprite_sheet.get(ASSET_W*2, ASSET_H*1, ASSET_W, ASSET_H))
    sprites["legs"] = (sprite_sheet.get(ASSET_W*3, ASSET_H*1, ASSET_W, ASSET_H))

# Generates a cube of air blocks, a blank template for a world
def generateEmptyWorld(x, y, z, l, w, h):
    for dep in range(h):
        for col in range(w):
            for row in range(l):
                render_group = (x + col) + (y + row) + (z + dep)
                new_block = Block(x + col, y + row, z + dep, "air")
                addBlockToRenderGroup(new_block, render_group)

# Sets a whole z-level/flat plane to a given type, useful for creating flat terrain 
def generatePlane(z, type):
    for col in range(WORLD_SIZE):
        for row in range(WORLD_SIZE):
            getBlockWithPosition(row, col, z)._type = type
            
# Generates a cube of blocks
def generateBlocks(x, y, z, type, l, w, h):
    for dep in range(h):
        for col in range(w):
            for row in range(l):
                if (x+col < WORLD_SIZE) and (y+row < WORLD_SIZE) and (z+dep < WORLD_HEIGHT):
                    if (x+col >= 0) and (y+row >= 0) and (z+dep >= 0):
                        getBlockWithPosition(x+col, y+row, z+dep)._type = type

# Generates trees
def generateTree(x, y, z):
    leaves_origin_x = x - 1
    leaves_origin_y = y - 1
    tree_height = int(random(3,WORLD_HEIGHT))
    generateBlocks(leaves_origin_x, leaves_origin_y, tree_height - 2, "leaves", 3,3,3)
    generateBlocks(x, y, 0, "log", 1, 1, tree_height)
        
    

# Adds given block object to specified render group, creates new render group if non-existent
def addBlockToRenderGroup(new_block, render_group):
    if render_group in blocks_render_groups.keys():
        blocks_render_groups[render_group].append(new_block)
    else:
        blocks_render_groups[render_group] = []
        blocks_render_groups[render_group].append(new_block)

# Returns a reference to a block object given its x, y, and z coordinates
def getBlockWithPosition(x, y, z):
    render_group = x + y + z
    target_position = PVector(x, y, z)
    if render_group in blocks_render_groups.keys():
        for block_object in blocks_render_groups[render_group]:
            if block_object._position == target_position:
                return block_object
                
'''
Converts x & y coordinates from the default cartesian plane perspective to a custom isometric pespective 
'''
def CartesionToIsometric(x, y):
    isometric_x = x - y
    isometric_y = (x + y) / 2
    isometric_position = PVector(isometric_x, isometric_y)
    return isometric_position

'''
Converts x & y coordinates from a custom isometric pespective to the default cartesian plane perspective
'''
def IsometricToCartesian(x, y):
    cartesian_x = (2 * y + x) / 2
    cartesian_y = (2 * y - x) / 2
    cartesian_position = PVector(cartesian_x, cartesian_y)
    return cartesian_position

'''
CLASS FOR BLOCK OBJECT

Parameters:
    x, y, z {integer} # x, y, and z coordinates to spawn block
    type, {key in sprites.keys()}

'''
class Block(object):
    
    # Constructor (called upon creation of block instance), takes x, y, and z coordinates as well as a block "type" + unique ID #
    def __init__(self, x, y, z, type):
        self._position = PVector(x,y,z)
        self._type = type
        self._render_order = x + y + z
'''
CLASS FOR PLAYER OBJECT
Extends Block object

Parameters:
    x, y, z {integer} # x, y, and z coordinates to spawn player
'''
class Player(object):
    def __init__(self, x, y, z):
        self._position = PVector(x,y,z)
        self._type = "player"
        self._render_order = x + y + z
        
    def updateRenderOrder(self):
        self._render_order = self._position.x + self._position.y + self._position.z
