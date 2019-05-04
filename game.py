import pygame as pg # shortens how much we type
vec = pg.math.Vector2 # player velocity stored in a vector 2
import random # tiles
import sys # generic
from os import path # for opening the text files

# Code based on:
# https://github.com/Mekire/pygame-samples/blob/master/platforming/moving_platforms.py
# the formatting is similar to the above source as it is a clean way to setup the game

# keeps the physics separate
class Physics:
    def __init__(self):
        self.vel = vec(0,0)
        self.gravity = 0.25
        self.falling = True

    def physicsUpdate(self):
        if self.falling:
            self.vel.y += self.gravity
        else:
            self.vel.y = 0

# builds our player
class Player(Physics, pg.sprite.Sprite):
    def __init__(self, game, position, speed):
        Physics.__init__(self)
        pg.sprite.Sprite.__init__(self)
        self.image = PLAYER_IMAGE
        self.speed = speed
        self.jumpForce = -8.5
        self.rect = self.image.get_rect(topleft=position)
        self.game = game
        self.position = position
        self.alive = True
        self.lives = LIVES
        # to keep track of if we are loading a new map, so we don't error out and attempt to load a map that
        # doesn't exist
        self.loading = False
        # "False" means we draw the normal image, "True" means we flip the image
        self.flip = False

    # checks the position of the player, which calls to check for collision for all block types
    def checkPosition(self, tiles, portals, traps):
        if not self.falling:
            self.checkFalling(tiles)
        else:
            self.falling = self.checkCollision((0, self.vel.y), 1, tiles)

        if self.vel.x:
            self.checkCollision((self.vel.x, 0), 0, tiles)
            #self.checkInvis((self.vel.x, -1), 0, invis)

        # TODO BUG 1: We have a temp fix found in Game, however we need to make sure this is only called a single time
        # checking is we hit a portal
        if pg.sprite.spritecollideany(self, portals, False) and not self.loading:
            self.loading = True
            self.game.currentLevel += 1
            self.game.load_data()

        if pg.sprite.spritecollideany(self, traps, False):
            self.alive = False
            #print("DEAD")

        # for wrapping around the screen
        if self.rect.x < 0:
            self.rect.x = WIDTH
        if self.rect.x > WIDTH:
            self.rect.x = 0

        # checking if we end up too far down the screen, if so we are dead
        if self.rect.y > HEIGHT:
            #print("YOU ARE DEAD!")
            self.alive = False


    # this a fancy way to check collision grabbed from our source on github, as my first (and all attempts after)
    # method of implementation was lengthy and very inefficient
    def checkCollision(self, offset, index, tiles):
        unaltered = True
        self.rect.move_ip(offset)
        while pg.sprite.spritecollideany(self, tiles):
            self.rect[index] += (1 if offset[index] < 0 else -1)
            unaltered = False
        return unaltered

    # we check if we are falling but checking the next square "down"
    def checkFalling(self, tiles):
        # go down a square to verify whats next
        self.rect.move_ip((0, 1))
        if not pg.sprite.spritecollideany(self, tiles):
            self.falling = True
        # move our rect back up
        self.rect.move_ip((0, -1))

    # Just checks the keys that the player clicks, jump is handled elsewhere
    def checkKeys(self, keys):
        self.vel.x = 0
        # we need to flip the image, as the player is default to the right
        if keys[pg.K_LEFT]:
            self.vel.x -= self.speed
            self.flip = True
        # we keep the same image
        if keys[pg.K_RIGHT]:
            self.vel.x += self.speed
            self.flip = False
        # resets the player position, doesn't kill the player
        if keys[pg.K_r]:
            self.rect.x = self.position[0]
            self.rect.y = self.position[1]

    # updates the player
    def update(self, tiles, portals, traps, keys):
        self.checkKeys(keys)
        self.checkPosition(tiles, portals, traps)
        self.physicsUpdate()

    # draw the player, based on whether the image should be flipped or not
    def draw(self, surface):
        # if the image shouldn't be flipped
        if not self.flip:
            surface.blit(self.image, self.rect)
        else:
            surface.blit(pg.transform.flip(self.image, True, False), self.rect)

    # called when the events in game is equal to space
    def jump(self):
        if not self.falling:
            self.vel.y = self.jumpForce
            self.falling = True
        else:
            self.falling = False


# our "invisible" tile, just the same color as our background
class InvisTile(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.screen = pg.display.get_surface()
        self.group = game.tiles
        pg.sprite.Sprite.__init__(self, self.group)
        self.rect = pg.Rect((x, y), (40, 40))
        self.image = pg.Surface((40, 40)).convert()
        self.image.fill(pg.Color("lightblue"))

# our classic tile with nothing special about it
class Tile(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.screen = pg.display.get_surface()
        self.group = game.tiles
        pg.sprite.Sprite.__init__(self, self.group)
        self.rect = pg.Rect((x, y), (40, 40))

        # randomness added to make the game more colorful
        color = [random.randint(0, 255) for i in range(3)]
        self.image = pg.Surface((40, 40)).convert()
        self.image.fill(color)
        self.image.blit(BLOCK_IMAGE, (5, 5))

# not a solid tile, so once we fall through the player dies. Appears the same as a normal block
class Trap(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.screen = pg.display.get_surface()
        self.groups = game.traps
        pg.sprite.Sprite.__init__(self, self.groups)
        self.rect = pg.Rect((x, y), (40, 40))

        color = [random.randint(0, 255) for i in range(3)]
        self.image = pg.Surface((40, 40)).convert()
        self.image.fill(color)
        self.image.blit(BLOCK_IMAGE, (5, 5))

# a tile that gets drawn but the player falls through, much like the Trap except no death
class FalseTile(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.screen = pg.display.get_surface()
        self.group = game.falseTiles
        pg.sprite.Sprite.__init__(self, self.group)
        self.rect = pg.Rect((x, y), (40, 40))

        color = [random.randint(0, 255) for i in range(3)]
        self.image = pg.Surface((40, 40)).convert()
        self.image.fill(color)
        self.image.blit(BLOCK_IMAGE, (5, 5))

# tile that when collided with we add one to the current level and reload the next map
class Portal(pg.sprite.Sprite):
    def __init__(self, game,  x, y, next):
        self.screen = pg.display.get_surface()
        self.group = game.portals
        pg.sprite.Sprite.__init__(self, self.group)
        self.rect = pg.Rect((x, y), (40, 40))
        color = [random.randint(0, 255) for i in range(3)]
        self.image = pg.Surface((40, 40)).convert()
        self.nextLevel = next
        self.image.fill(color)

# main game class
class Game:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        # key events for the player
        self.keys = pg.key.get_pressed()
        self.done = False
        self.player = Player(self, (50, -25), 4)
        self.viewport = self.screen.get_rect()
        # the level is bigger than the viewport that is rendered
        self.level = pg.Surface((WIDTH, HEIGHT)).convert()
        self.level_rect = self.level.get_rect()
        # holds the current map info
        self.map_data = []
        self.currentLevel = 0
        self.load = False
        # for delaying the death screen
        self.counter = 0
        self.playerLives = 3
        self.load_data()
        

    # used for calculating for what the camera sees when following the player
    def updateViewport(self):
        self.viewport.center = self.player.rect.center
        self.viewport.clamp_ip(self.level_rect)

    # loads the proper map
    def load_data(self):
        # clear the map_data from any past maps
        self.map_data.clear()
        # we declare the sprite groups here so they get wiped when we move on from one map to another
        self.tiles = pg.sprite.Group()
        self.portals = pg.sprite.Group()
        self.falseTiles = pg.sprite.Group()
        self.traps = pg.sprite.Group()
        self.invis = pg.sprite.Group()
        game_folder = path.dirname(__file__)
        with open(path.join(game_folder, 'map' + str(self.currentLevel) + '.txt'), 'rt') as f:
            for line in f:
                self.map_data.append(line)
        self.createMap()

    # takes the data loaded in from load_data and sets up each Tile
    def createMap(self):
        # for each index found in our file we set it up to the proper "Tile"
        for row, amount in enumerate(self.map_data):
            for col, tile in enumerate(amount):
                if tile == '1':
                    Tile(self, col * 40, row * 40)
                if tile == '2':
                    FalseTile(self, col * 40, row * 40)
                if tile == '3':
                    Portal(self, col * 40, row * 40, self.currentLevel + 1)
                if tile == '4':
                    Trap(self, col * 40, row * 40)
                if tile == '5':
                    self.player = Player(self, (col * 40, row * 40), 4)
                if tile == '6':
                    InvisTile(self, col * 40, row * 40)

        self.player.loading = False

    # checks for key presses from the player, calls jump when needed
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()

    # check for keys, updates the game which updates the player and the viewport
    def update(self):
        self.keys = pg.key.get_pressed()
        self.player.update(self.tiles, self.portals, self.traps, self.keys)
        self.updateViewport()

    # draws everything related to the game, even the invisible tiles as they are just the same color as the background
    def draw(self):
        deathScore = myFont.render('YOU ARE DEAD', False, (0, 0, 0))
        text = "Lives: " + str(self.playerLives)
        playerLives = myFont.render(text, False, (0, 0, 0))

        # Draws the game if the player is alive
        if self.player.alive:
            self.level.fill(pg.Color("lightblue"))
            self.screen.fill((50, 50 ,50))
            self.tiles.draw(self.level)
            self.falseTiles.draw(self.level)
            self.portals.draw(self.level)
            self.invis.draw(self.level)
            self.traps.draw(self.level)
            self.player.draw(self.level)
            self.screen.blit(self.level, (0,0), self.viewport)
            self.screen.blit(playerLives, (0, 0))

        # The player is dead, now we draw a blank screen and some text
        else:
            # making sure we only decremented lives if the counter is 0
            if self.counter == 0:
                self.playerLives -= 1

            self.counter += 1

            self.level.fill(pg.Color("lightblue"))
            self.screen.fill((50, 50, 50))

            self.screen.blit(self.level, (0,0), self.viewport)
            self.screen.blit(deathScore, (275, 225))
            self.screen.blit(playerLives, (275, 275))

            # couldn't get wait or delay to work, so this is a work around
            if self.counter >= 175:
                self.counter = 0
                self.player.alive = True
                self.load_data()

    # does as it says, formats in the FPS; as knowing this is actually important (physics/position is calculated per frame
    def display_fps(self):
        caption = "{} - FPS: {:.2f}".format("Well, that's fair...", self.clock.get_fps())
        pg.display.set_caption(caption)

    def loop(self):
        # main game loop, we continue to loop
        while not self.done:
            self.events()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)
            self.display_fps()


# Set up the title screen and loop it much like the game
class Title:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.keys = pg.key.get_pressed()
        self.done = False
        self.quit = False
        pg.display.set_caption("Well that's fair...")

    # draw the screen and all text required
    def draw(self):
        title = myFont2.render("Well, that's fair...", False, (255, 255, 255))
        instructions = myFont.render("Press space to start the game!", False, (255, 255, 255))
        self.screen.fill((0, 0, 0))
        self.screen.blit(title, (200, 150))
        self.screen.blit(instructions, (200, 200))

    # "Player" events
    def events(self):
        for event in pg.event.get():
            # this exits the game, so set done and quit to True
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True
                self.quit = True
            # advance to the game
            if self.keys[pg.K_SPACE]:
                self.done = True

    # just updates the main screen, its somewhat needed
    def update(self):
        self.keys = pg.key.get_pressed()

    # main loop of the title screen
    def loop(self):
        while not self.done:
            self.events()
            self.update()
            self.draw()
            pg.display.update()

# Whole program
if __name__ == "__main__":
    # start up pygame and fonts
    pg.init()
    myFont = pg.font.SysFont('Comic Sans MS', 30)
    myFont2 = pg.font.SysFont('Arial', 52)
    pg.display.set_caption("Well, that's fair...")
    pg.display.set_mode((800, 600))
    LIVES = 3
    # load up the images we need
    PLAYER_IMAGE = pg.image.load("images/player.png").convert_alpha()
    BLOCK_IMAGE = pg.image.load("images/ground.png").convert_alpha()
    WIDTH = 1920
    HEIGHT = 1080
    # title screen until we hit space
    t = Title()
    t.loop()
    # if we don't quit out of the title (using escape) then we move on to the game
    if not t.quit:
        g = Game()
        g.loop()
    pg.quit()
    sys.exit()




