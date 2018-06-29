# bg_music: Ove - Earth Is All We Have written and produced by Ove Melaa (Omsofware@hotmail.com)

import pygame
import random
import os


# Windows and FPS
WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000
HIDE_TIME = 2000
SPAWN_TIME = 2000
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
snd_folder = os.path.join(game_folder, "snd")

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


def new_mob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def draw_hp_bar(surf, x, y, pct):
    if pct <= 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct/100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "SHMUP!", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "Arrow key to move, Space key to fire", 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, "Press a key to start", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 21
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT
        self.speedx = 0
        self.hp = 100
        self.shoot_delay = 350
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power_lv = 1
        self.power_timer = pygame.time.get_ticks()
        self.spawn = False
        self.spawn_time = pygame.time.get_ticks()
        self.count = 0

    def update(self):
        # timeout for powerups
        if self.power_lv >= 2 and pygame.time.get_ticks() - self.power_timer > POWERUP_TIME:
            self.power_lv -= 1
            self.power_timer = pygame.time.get_ticks()
        # unhide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > HIDE_TIME:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT
            self.spawn = True
            self.spawn_time = pygame.time.get_ticks()
        if self.spawn and pygame.time.get_ticks() - self.spawn_time > SPAWN_TIME:
            self.spawn = False
        self.speedx = 0
        # Detect keys pressed
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -6
        if keystate[pygame.K_RIGHT]:
            self.speedx = 6
        if keystate[pygame.K_SPACE] and self.hidden == False:
            self.shoot()
        self.rect.x += self.speedx
        # Set boundary
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power_lv == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power_lv >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        # hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+200)

    def powerup(self):
        self.power_lv += 1
        self.power_timer = pygame.time.get_ticks()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width*.85/2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 5)
        self.speedx = random.randrange(-3, 3)
        # Rotate the Mob
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        self.mob_lv = 1

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
        # Increase Game Difficulty
        if int(score / 2000) == 0:
            self.mob_lv = 1

        else:
            self.mob_lv = int(score // 2000)
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # Re-draw the Mob
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 30:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -100)
            self.speedy = random.randrange(1*self.mob_lv, 7*self.mob_lv)
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


class Powerup(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_img[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        # Kill it when off screen
        if self.rect.top > HEIGHT:
            self.kill()


# Load all game graphics

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


background = pygame.image.load(os.path.join(img_folder, "bg.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(os.path.join(img_folder, "ship.png")).convert()
player_lives_img = pygame.transform.scale(player_img, (25, 19))
player_lives_img.set_colorkey(BLACK)
# mob_img = pygame.image.load(os.path.join(img_folder, "meteor.png")).convert()
bullet_img = pygame.image.load(os.path.join(img_folder, "laser.png")).convert()

# Meteor images
meteor_images = []
meteor_list = ['meteor1.png', 'meteor2.png', 'meteor3.png', 'meteor4.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(img_folder, img)).convert())

# Explosion images
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []

for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    # Player explosion
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

powerup_img = {}
powerup_img['shield'] = pygame.image.load(os.path.join(img_folder, "shield_gold.png")).convert()
powerup_img['gun'] = pygame.image.load(os.path.join(img_folder, "bolt_gold.png")).convert()
# Load all game sounds
shoot_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'laser.wav'))
shoot_sound.set_volume(0.1)
powerup_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'Powerup.wav'))
powerup_sound.set_volume(0.2)
shieldup_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'shieldUp.ogg'))
# shieldup_sound.set_volume(0.5)
exp_sounds = []
exp_list = ['Explosion.wav', 'Explosion1.wav', 'Explosion2.wav']
for exp in exp_list:
    exp_sounds.append(pygame.mixer.Sound(os.path.join(snd_folder, exp)))

for sound in exp_sounds:
    sound.set_volume(0.25)

pygame.mixer.music.load(os.path.join(snd_folder, 'bg_sound.ogg'))
pygame.mixer.music.set_volume(0.6)


# bg music
pygame.mixer.music.play(loops=-1)
# Game main loop

game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()

        player = Player()
        all_sprites.add(player)
        for i in range(8):
            new_mob()
        # Score
        score = 0
        powerup_drop = 0.9
    # Keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # Check for closing Window
        if event.type == pygame.QUIT:
            running = False

    # Update
    all_sprites.update()
    # Check for collisions [Mobs & Bullets]
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(exp_sounds).play()

        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > powerup_drop:
            pow = Powerup(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        new_mob()

    # Check for collisions [Player & Mobs]
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    if player.spawn == False:
        for hit in hits:
            player.hp -= hit.radius * 2
            player.shoot_delay += 30
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            random.choice(exp_sounds).play()
            new_mob()
            if player.hp <= 0:
                death_exp = Explosion(player.rect.center, 'player')
                all_sprites.add(death_exp)
                player.hide()
                player.lives -= 1
                player.hp = 100
                player.shoot_delay = 350

    # Check for collisions [Player & Powerups]
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            shieldup_sound.play()
            player.hp += random.randrange(15, 30)
            if player.hp >= 100:
                player.hp = 100
        if hit.type == 'gun':
            player.powerup()
            powerup_sound.play()
            # if player.shoot_delay <= 80:
            #     player.shoot_delay = 80
            # else:
            #     player.shoot_delay -= 30

            # if the player's dead, and the explosion done
    if player.lives == 0 and not death_exp.alive():
        game_over = True

    # Draw / render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_hp_bar(screen, 5, 5, player.hp)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_lives_img)

    # after drawing everything, flip the display
    pygame.display.flip()


pygame.quit()
