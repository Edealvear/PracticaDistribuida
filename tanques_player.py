from multiprocessing.connection import Client
import time
import traceback
import pygame
import sys, os

SIZE = (700, 525)
FPS = 60
BullSize = 10
PowerUpSize = 30
POSPWUPX = 150
POSPWUPY = 200
PlayerSize = 30
PLAYER = [0,1]

class Wall(pygame.sprite.Sprite):
    """
    Walls can't be passed by player.
    """
    def __init__(self, x, y, width, height, color, screen):
        # Init.
        pygame.sprite.Sprite.__init__(self)
        self.pos [x,y]
        self.height = height
        self.width = width
        self.color = color
        self.screen = screen
        # Create
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def draw(self):
        pygame.draw.rect(self.screen, self.color, [self.pos[0], self.pos[1], self.width, self.height], 0)
    
    def update() -> None:
        pass

class Power_UP():
    def __init__(self, type, id):
        self.id = id
        self.type = type
        self.image = pygame.image.load(fr"bonus{type}.png")
        self.active=True
        self.pos = []#Falta rellenar posicion
    
    def get_id(self):
        return self.id
    
    def get_type(self):
        return self.type

class PowerUpImage(pygame.sprite.Sprite):
    def __init__(self, powerup, screen):
        self.screen = screen
        super().__init__()
        self.pwup = powerup
        self.rect = pygame.Surface( (PowerUpSize, PowerUpSize))
        self.rect.centerx, self.rect.centery = POSPWUPX, POSPWUPY
        pygame.transform.scale(powerup.image, self.rect.get_size, dest_surface=self.rect)
        #self.rect.blip(self.image, powerup.pos)
    
    def update(self) -> None:
        pass
        
class Bullet():
    def __init__(self, NumP, position, direction, id, damage = 1, speed = 5):
        self.id = id
        self.owner = NumP
        self.pos = position
        self.damage = damage
        self.speed = speed
        self.dir = direction#0 : izq; 1:arriba; 2:Der ; 3: abajo
        self.active = True
    
    def get_pos(self):
        return self.pos
    
    def get_dmg(self):
        return self.damage
    
    def get_id(self):
        return self.id
        
class Draw_bullet(pygame.sprite.Sprite):
    def __init__(self, bullet, screen):
        self.screen = screen
        super().__init__()
        self.bullet = bullet
        self.rect = pygame.Surface((BullSize, BullSize), pygame.SRCALPHA)
        self.rect.centerx, self.rect.centery = self.bullet.pos
        self.image_load = pygame.transform.scale(pygame.image.load(r"bullet.png"), self.rect.get_size(), dest_surface = self.rect)
        #self.rect.blit(self.image_load, (0,0))
        # self.screen.blit(self.rect, self.rect_pos)
        pygame.draw.rect(self.rect)

    def update(self) -> None:
        pos = self.bullet.get_pos
        self.rect.centerx, self.rect.centery = pos
  

class Player():
    def __init__(self, num_P, pos =[None, None]):
        self.numP = num_P
        self.image = pygame.image.load(rf"TanqueP{self.numP + 1}.png")
        self.pos = pos
        self.powerups = {
            "shield" : 0,
            "speed" : 0,
            "supershot" : 0
        }
        self.lives = 5
        self.direction  = None 

    
    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"Tank {self.numP}"
    

class Player_display(pygame.sprite.Sprite):
    def __init__(self, player, screen):
        self.screen = screen
        self.player = player 
        self.rect = pygame.Surface((PlayerSize, PlayerSize))
        self.image = self.player.image
        self.rect.centerx, self.rect.centery = self.player.pos
        pygame.transform.scale(self.image, self.rect.get_size, self.rect)
        #self.screen.blip(self.image, self.pos)
    
    def update(self, player):
        self.screen.blip(self.image, self.pos)

class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.bullets = []
        self.powerUps = []
        self.score = [0,0]
        self.running = True
    
    def getplayer(self, numP):
        return self.players[numP]
    
    def set_posplayer(self, numP, pos):
        self.players[numP].set_pos(pos)
    
    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def update(self, game_info):
        self.set_posplayer(0, game_info["pos_J1"])
        self.set_posplayer(1, game_info["pos_J2"])

        self.directions = game_info["dir"]
        self.set_score(game_info["score"])
        self.running = game_info["is_running"]
    
    def is_running(self):
        return self.running
    
    def stop(self):
        self.running = False
    
class Display():
    def __init__(self, game):
        self.screen = pygame.display.set_mode(SIZE)
        self.game = game
        self.tanks = [game.players.getplayer(i) for i in range(2)]
        self.tanks_sprites = [Player_display(self.tanks[i]) for i in range(2)]
        self.bullets = {}
        self.bullets_sprites = {}
        self.powerups = []
        self.powerups_sprites = []
        self.walls = [Wall(), Wall()]#Falta añadir las paredes
        self.collision_group = pygame.sprite.Group()
        self.all_sprites=pygame.sprite.Group()
        for i in range(2):
            self.collision_group.add(self.tanks_sprites[i])
            self.all_sprites.add(self.tanks_sprites[i])
        for wall in self.walls:
            self.collision_group.add(wall)
            self.all_sprites(wall)
        self.background = pygame.image.load("mapa.png")
        self.clock = pygame.time.Clock()
        pygame.init()

    def analyze_events(self, NumP):
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key == pygame.K_DOWN:
                    events.append("Down")
                elif event.key == pygame.K_UP:
                    events.append("Up")
                elif event.key == pygame.K_LEFT:
                    events.append("Left")
                elif event.key == pygame.K_RIGHT:
                    events.append("Right")
                elif event.key == pygame.K_SPACE:
                    events.append("Space")
            elif event.type == pygame.QUIT:
                events.append("quit")
        for bullet in self.bullets_sprites:
            for wall in self.walls:
                if pygame.sprite.collide_rect(wall, bullet):
                    events.append("Col_BW")
            for player in self.tanks_sprites:
                if player.numP != bullet.owner and pygame.sprite.collide_rect(player, bullet):
                    events.append(f"Player_hit")
        for player in self.tanks_sprites:
            if pygame.sprite.collide_rect(player, self.powerups_sprites[0]):
                events.append("getPWUP")
        for wall in self.walls:
            for player in self.tanks_sprites:
                if pygame.sprite.collide_rect(player, wall):
                    events.append("Col_PW")
        return events

    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background,(0,0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 74)
        text = font.render(f"lives P1 {score[0]} || lives P2 {score[1]}")
        self.screen.blit(text, (SIZE[0]-250, 10))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
            
    def new_sprites(self, gameinfo):
        for bullet in gameinfo["new_bullets"]:
            self.bullets[bullet[0]] =Bullet(bullet[0], bullet[2], bullet[3], bullet[0])
            self.bullets_sprites[bullet[0]] = Draw_bullet(self.bullets[-1], self.screen)
            self.all_sprites.add(self.bullets_sprites[-1])
        for powerUps in gameinfo["new_powerUps"]:
            self.powerups.append(Power_UP(powerUps))
            self.powerups_sprites.append(PowerUpImage(self.powerups[-1], self.screen))
            self.all_sprites.add(self.powerups_sprites[-1])

    def delete_sprites(self, game_info):
        for (elem, elem_id) in game_info["delete"]:
            if elem == "bullet":
                sprite = self.bullets_sprites[elem_id]
                self.all_sprites.remove(sprite)
                del self.bullets[elem_id]
                del self.bullets_sprites[elem_id]
            if elem == "powerUp":
                self.all_sprites.remove(self.powerups_sprites[0])
                self.powerups.pop()
                self.powerups_sprites.pop()

    def tick(self):
        self.clock.tick(FPS)
    
    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am playing {PLAYER[side]}")
            game.update(gameinfo)
            display = Display(game)
            while game.is_running():
                events = display.analyze_events(side)
                for ev in events:
                    conn.send(ev)
                    if ev == 'quit':
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                if gameinfo["END"] == True:
                    Win = gameinfo["Winner"]
                    font = pygame.font.Font(None, 90)
                    text = font.render(f"Winner player N {Win}")
                    display.screen.blit(display.background, (0,0))
                    display.screen.blit(text, (SIZE[0]-250, 10))
                    time.sleep(10)
                    game.running = False
                else:
                    game.update(gameinfo)
                    display.new_sprites(gameinfo)
                    display.delete_sprites(gameinfo)
                    display.refresh()
                    display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)