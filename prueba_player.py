from multiprocessing.connection import Client
import time
import traceback
import pygame
import sys, os

SIZE = (830, 884)
WHITE = (255,255,255)
FPS = 60
BullSize = 16
PowerUpSize = 50
POSPWUPX = 150
POSPWUPY = 200
PlayerSize = 50
PLAYER = [1,2]

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
        self.image = pygame.image.load(r"bullet.png")
        self.screen.blit(self.image, self.bullet.pos)
        self.rect = self.image.get_rect()
        self.update()
        #self.rect.blit(self.image_load, (0,0))
        #self.screen.blit(self.rect, self.rect_pos)


    def update(self) -> None:
        pos = self.bullet.get_pos()
        #self.rect.centerx, self.rect.centery = pos
        self.screen.blit(self.image, pos)
class Player():
    def __init__(self, num_P, pos =[None, None]):
        self.numP = num_P
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
        super().__init__()
        self.screen = screen
        self.player = player 
        self.image = pygame.image.load(rf"TanqueP{self.player.numP + 1}.png")
        self.rect = self.image.get_rect()
        self.screen.blit(self.image, self.player.pos)
        self.update()
        #self.screen.blip(self.image, self.pos)
    
    def update(self):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos
        self.screen.blit(self.image, pos)


class Game():
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.bullets = []
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
        if "bullets" in game_info.keys():
            for bull in self.bullets:
                for b in game_info["bullets"]:
                    if bull.id == b[0]:
                        bull.pos = b[2]
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
        self.tanks = [game.getplayer(i) for i in range(2)]
        self.tanks_sprites = [Player_display(self.tanks[i], self.screen) for i in range(2)]
        self.bullets = {}
        self.bullets_sprites = {}
        self.collision_group = pygame.sprite.Group()
        self.all_sprites=pygame.sprite.Group()
        for i in range(2):
            self.collision_group.add(self.tanks_sprites[i])
            self.all_sprites.add(self.tanks_sprites[i])
        self.background = pygame.image.load("Mapa.png")
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
        for bullet in self.bullets_sprites.values():
            for wall in self.walls:
                if pygame.sprite.collide_rect(wall, bullet):
                    events.append("ColBW")
                    events.append(str(bullet.bullet.id))
            for player in self.tanks_sprites:
                if player.player.numP != bullet.bullet.owner and pygame.sprite.collide_rect(player, bullet):
                    events.append("Playerhit")
        
        return events

    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background,(0,0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 60)
        text = font.render(f"lives P1 {score[0]} || lives P2 {score[1]}", True ,WHITE)
        self.screen.blit(text, (15,15))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def new_sprites(self, gameinfo):
        if 'new_bullets' in gameinfo.keys():
            for bullet in gameinfo["new_bullets"]:
                self.bullets[bullet[0]] = Bullet(bullet[1], bullet[2], bullet[3], bullet[0])
                self.bullets_sprites[bullet[0]] = Draw_bullet(self.bullets[bullet[0]], self.screen)
                self.all_sprites.add(self.bullets_sprites[bullet[0]])
        

    def delete_sprites(self, game_info):
        for (elem, elem_id) in game_info["delete"]:
            if elem == "bullet":
                print(elem_id)
                for k, sprite in self.bullets_sprites.items():
                    if k == elem_id:
                        k1 = k
                        sprite.kill()
                del self.bullets[k1]
                del self.bullets_sprites[k1]
            
            
    

    def tick(self):
        self.clock.tick(FPS)
    
    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey = b"password") as conn:
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
                game.update(gameinfo)
                
                
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