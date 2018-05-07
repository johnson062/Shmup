import pygame
import random
import os


#Windows and FPS
WIDTH = 480
HEIGHT = 600
FPS = 60

# Define Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


# Set up assets folders
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")

# Pygame Init
pygame.init()
# Music Init
pygame.mixer.init()
# Set Window display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmug")
# Define clock
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 21
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT
        self.speedx = 0

    def update(self):
        self.speedx = 0
        # Detect keys pressed
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -6
        if keystate[pygame.K_RIGHT]:
            self.speedx = 6

        self.rect.x += self.speedx
        # Set boundary
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width*.85/2)
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 5)
        self.speedx = random.randrange(-3, 3)
        # Rotate the Mob
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # Re-draw the Mob
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 30:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -100)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(1, 3)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # Kill it when off screen
        if self.rect.bottom < 0:
            self.kill()


# Load all game graphics
background = pygame.image.load(os.path.join(img_folder, "bg.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(os.path.join(img_folder, "ship.png")).convert()
#mob_img = pygame.image.load(os.path.join(img_folder, "meteor.png")).convert()
bullet_img = pygame.image.load(os.path.join(img_folder, "laser.png")).convert()
meteor_images = []
meteor_list = ['meteor1.png', 'meteor2.png', 'meteor3.png', 'meteor4.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(img_folder, img)).convert())


all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)
for i in range(8):
    m = Mob()
    all_sprites.add(mobs)
    mobs.add(m)

# Score
score = 0

# Game main loop
running = True
while running:
    # Keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # Check for closing Window
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Update
    all_sprites.update()
    # Check for collisions [Bullets]
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)
    # Check for collisions [Mobs]
    hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
    if hits:
        running = False

    #Draw / render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH/2, 10)

    # after drawing everything, flip the display
    pygame.display.flip()


pygame.quit()
