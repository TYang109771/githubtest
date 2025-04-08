import pygame
from pygame.locals import *
import random

#define fps
clock = pygame.time.Clock()
fps = 60


screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invaders')


#define game variables
rows = 5
cols = 5
alien_cooldown = 1000#bullet cooldown in milliseconds
last_alien_shot = pygame.time.get_ticks()

#define colours
red = (255, 0, 0)
green = (0, 255, 0)


#load image
bg = pygame.image.load("img/bg.png")

def draw_bg():
    screen.blit(bg, (0, 0))


#create spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/spaceship.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()


    def update(self):
        #set movement speed
        speed = 8
        #set a cooldown variable
        cooldown = 500 #milliseconds 

        #get key press
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -=  speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x +=  speed


        #record current time
        time_now = pygame.time.get_ticks()
        #shoot
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            bullet = Bullets(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

            
        #update mask
        self.mask = pygame.mask.from_surface(self.image)

        
        #draw health bar
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <= 0:
            explosion = Explosion(self.rect.centerx,self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()


#create Bullets class
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion = Explosion(self.rect.centerx,self.rect.centery, 2)
            explosion_group.add(explosion)


#create Aliens class
class Aliens(pygame.sprite.Sprite):
    def __init__(self, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien" + str(random.randint(1, 5)) + ".png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.move_counter = 0
        self.move_direction = 1
        
    def update(self):
        self.rect.x += 1 * self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction


#create Alien Bullets class
class Alien_Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y,):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/alien_bullet.png")
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self,spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            #reduce spaceship health
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.centerx,self.rect.centery, 1)
            explosion_group.add(explosion)

        
#create Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f"img/exp{num}.png")
            if size == 1:
                img = pygame.transform.scale(img, (20,20))
            if size == 2:
                img = pygame.transform.scale(img, (40,40))
            if size == 3:
                img = pygame.transform.scale(img, (160,160))
            #add the image to the list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0


    def update(self):
        explosion_speed = 3
        #update explosion animatio
        self.counter += 1

        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        #if the animation is complete, delete explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()


#create sprite groups
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


def create_aliens():
    #generate aliens
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(100 + item * 100, 100 + row * 70)
            alien_group.add(alien)

create_aliens()


#create player
spaceship = Spaceship(int(screen_width/2), screen_height - 100, 3)
spaceship_group.add(spaceship)


run = True
while run:

    clock.tick(fps)

    #draw background
    draw_bg()


    #create random alien bullets
    #record current time
    time_now = pygame.time.get_ticks()
    #shoot
    if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
        attacking_alien = random.choice(alien_group.sprites())
        alien_bullet = Alien_Bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
        alien_bullet_group.add(alien_bullet)
        last_alien_shot = time_now
        

    #event handlers
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    
    #update spaceship
    spaceship.update()


    #update sprite groups
    bullet_group.update()
    alien_group.update()
    alien_bullet_group.update()
    explosion_group.update()
    
    
    #update sprite groups
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)
    

    pygame.display.update()

pygame.quit()
