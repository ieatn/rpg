import pygame, random, button
pygame.init()
clock = pygame.time.Clock()
fps = 60

panel = 150
screen_width = 800
screen_height = 400+panel
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Battle')

current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 15
clicked = False
game_over = 0

#define fonts
font = pygame.font.SysFont('Times New Roman', 26)
#define colors
red = (255, 0, 0)
green = (0, 255, 0)

bg = pygame.image.load('bg.png').convert_alpha()
panel = pygame.image.load('menu.png').convert_alpha()
sword = pygame.image.load('sword.png').convert_alpha()
potion = pygame.image.load('potion.jpg').convert_alpha()
restart = pygame.image.load('restart.png').convert_alpha()
restart = pygame.image.load('restart.png').convert_alpha()
victory = pygame.image.load('victory.png').convert_alpha()
defeat = pygame.image.load('defeat.png').convert_alpha()

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

def draw_bg():
    screen.blit(bg, (0,0))
def draw_panel():
    #draw panel rectangle
    screen.blit(panel, (0, screen_height-150))
    #show knight stats
    draw_text(f'{knight.name} HP: {knight.hp}', font, red, 100, screen_height-150+10)
    for count, i in enumerate(bandit_list):
        draw_text(f'{i.name} HP: {i.hp}', font, red, 550, (screen_height - 150 + 10)+count*60)


class Fighter():
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True

        self.animation_list = []
        self.frame_index = 0
        self.action = 1 #0:idle, 1:atk, 2:hurt, 3:dead
        self.update_time = pygame.time.get_ticks()
        #load idle images
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/idle/{i}.png')
            img = pygame.transform.scale(img, (img.get_width()*3, img.get_height()*3))
            temp_list.append(img)
        self.animation_list.append(temp_list)
        #load atk images
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/attack/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # load hurt images
        temp_list = []
        for i in range(3):
            img = pygame.image.load(f'img/{self.name}/hurt/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # load death images
        temp_list = []
        for i in range(10):
            img = pygame.image.load(f'img/{self.name}/death/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    def update(self):
        animation_cooldown = 100
        #update image
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time passed since last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if animation reaches last one 8 then reset
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) -1
            else:
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        r = random.randint(-5, 5)
        damage = self.strength + r
        target.hp -= damage
        target.hurt()
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
        damage_text_group.add(damage_text)
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def reset(self):
        self.alive = True
        self.potions = self.start_potions
        self.hp = self.max_hp
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)

class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
    def draw(self, hp):
        #update with new health
        self.hp = hp
        ratio = self.hp/self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150*ratio, 20))

class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0
    def update(self):
        self.rect.y -= 1
        self.counter += 1
        if self.counter > 30:
            self.kill()

damage_text_group = pygame.sprite.Group()


knight = Fighter(200, 260, 'Knight', 30, 10, 3)
bandit1 = Fighter(550, 270, 'Bandit', 20, 6, 1)
bandit2 = Fighter(700, 270, 'Bandit', 20, 6, 1)
bandit_list = []
bandit_list.append(bandit1)
bandit_list.append(bandit2)
knight_health_bar = HealthBar(100, screen_height-150+40, knight.hp, knight.max_hp)
bandit1_health_bar = HealthBar(550, screen_height-150+40, bandit1.hp, bandit1.max_hp)
bandit2_health_bar = HealthBar(550, screen_height-150+100, bandit2.hp, bandit2.max_hp)


potion_button = button.Button(screen, 100, screen_height-150+70, potion, 64, 64)
restart_button = button.Button(screen, 330, 120, restart, 120, 30)

run = True
while run:
    clock.tick(fps)
    draw_bg()
    draw_panel()
    knight_health_bar.draw(knight.hp)
    bandit1_health_bar.draw(bandit1.hp)
    bandit2_health_bar.draw(bandit2.hp)
    knight.update()
    knight.draw()
    for bandit in bandit_list:
        bandit.update()
        bandit.draw()

    damage_text_group.update()
    damage_text_group.draw(screen)


    attack = False
    potion = False
    target = None
    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()
    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos):
            pygame.mouse.set_visible(False)
            screen.blit(sword, pos)
            if clicked == True and bandit.alive == True:
                attack = True
                target = bandit_list[count]
    if potion_button.draw():
        potion = True
    draw_text(str(knight.potions), font, red, 150, screen_height-150+70)
    if game_over == 0:
        #player action
        if knight.alive == True:
            if current_fighter == 1:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    if attack == True and target != None:
                        knight.attack(target)
                        current_fighter += 1
                        action_cooldown = 0
                    if potion == True:
                        if knight.potions > 0:
                            if knight.max_hp - knight.hp > potion_effect:
                                heal_amount = potion_effect
                            else:
                                heal_amount = knight.max_hp - knight.hp
                            knight.hp += heal_amount
                            damage_text = DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), green)
                            damage_text_group.add(damage_text)
                            knight.potions -= 1
                            current_fighter += 1
                            action_cooldown = 0
        else:
            game_over = -1
        #enemy action
        for count, bandit in enumerate(bandit_list):
            if current_fighter == 2 + count:
                if bandit.alive == True:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        if bandit.hp/bandit.max_hp < 0.5 and bandit.potions > 0:
                            if bandit.max_hp - bandit.hp > potion_effect:
                                heal_amount = potion_effect
                            else:
                                heal_amount = bandit.max_hp - bandit.hp
                            bandit.hp += heal_amount
                            bandit.potions -= 1
                            damage_text = DamageText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), green)
                            damage_text_group.add(damage_text)
                            current_fighter += 1
                            action_cooldown = 0
                        bandit.attack(bandit)
                        current_fighter += 1
                        action_cooldown = 0
                else:
                    current_fighter += 1

        if current_fighter > total_fighters:
            current_fighter = 1

    #check if bandits dead
    alive_bandits = 0
    for bandit in bandit_list:
        if bandit.alive == True:
            alive_bandits += 1
    if alive_bandits == 0:
        game_over = 1

    #check game over
    if game_over != 0:
        if game_over == 1:
            screen.blit(victory, (250, 50))
        if game_over == -1:
            screen.blit(defeat, (290, 50))
        if restart_button.draw():
            knight.reset()
            for bandit in bandit_list:
                bandit.reset()
            current_fighter = 1
            action_cooldown
            game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False
    pygame.display.update()
pygame.quit()