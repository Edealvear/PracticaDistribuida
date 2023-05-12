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
    def __init__(self, NumP, position, direction, id, speed = 50):
        self.id = id
        self.owner = NumP
        self.pos = position
        self.speed = speed
        self.dir = direction #0 : izq; 1:arriba; 2:Der ; 3: abajo
        self.active = True
    
    def get_pos(self):
        return self.pos
    

    
    def get_id(self):
        return self.id
        
class Draw_bullet(pygame.sprite.Sprite):
    def __init__(self, bullet, screen):
        super().__init__()
        self.screen = screen
        self.bullet = bullet
        self.image = pygame.image.load(r"bullet.png")
        self.screen.blit(self.image, self.bullet.pos)
        self.rect = self.image.get_rect()
        self.update()
        #self.rect.blit(self.image_load, (0,0))
        #self.screen.blit(self.rect, self.rect_pos)

    def update(self) -> None:
        pos = self.bullet.get_pos()
        self.rect.centerx, self.rect.centery = pos
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
        self.dir = 0
        self.image = pygame.image.load(rf"TanqueP{self.player.numP + 1}_right.png")
        self.rect = self.image.get_rect()
        self.screen.blit(self.image, self.player.pos)
        self.update()
        #self.screen.blip(self.image, self.pos)
    
    def update(self):
        pos = self.player.get_pos()
        self.rect.centerx, self.rect.centery = pos
        self.screen.blit(self.image, pos)

        if self.dir == 0:
            self.image = pygame.image.load(rf"TanqueP{self.player.numP + 1}_left.png")
        elif self.dir == 1:
            self.image = pygame.image.load(rf"TanqueP{self.player.numP + 1}_up.png")
        elif self.dir == 2:
            self.image = pygame.image.load(rf"TanqueP{self.player.numP + 1}_right.png")
        elif self.dir == 3:
            self.image = pygame.image.load(rf"TanqueP{self.player.numP + 1}_down.png")



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
    '''
    def update(self, game_info):
        self.set_posplayer(0, game_info["pos_J1"])
        self.set_posplayer(1, game_info["pos_J2"])
        if 'bullets' in game_info.keys():
            for bull in self.bullets:

                for b in game_info["bullets"]:
                    if bull.id == b[0]:
                        bull.pos = b[2]
                print(f'POSIBALA: {bull.pos}')
        self.directions = game_info["dir"]
        self.set_score(game_info["score"])
        self.running = game_info["is_running"]
    '''
    
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
                    self.tanks_sprites[NumP].dir = 3
                    events.append("Down")
                elif event.key == pygame.K_UP:
                    self.tanks_sprites[NumP].dir = 1
                    events.append("Up")
                elif event.key == pygame.K_LEFT:
                    self.tanks_sprites[NumP].dir = 0
                    events.append("Left")
                elif event.key == pygame.K_RIGHT:
                    self.tanks_sprites[NumP].dir = 2
                    events.append("Right")
                elif event.key == pygame.K_SPACE:
                    events.append("Space")
                    
                

            elif event.type == pygame.QUIT:
                events.append("quit")
        for bullet in self.bullets_sprites.values():
            for player in self.tanks_sprites:
                if player.player.numP != bullet.bullet.owner and pygame.sprite.collide_rect(player, bullet):
                    
                    events.append("Playerhit")
        
        return events

    def refresh(self, gameinfo):
        self.all_sprites.update()
        self.screen.blit(self.background,(0,0))
        self.new_sprites(gameinfo)
        score = self.game.get_score()
        font = pygame.font.Font(None, 60)
        text = font.render(f"lives P1 {score[0]} || lives P2 {score[1]}", True ,WHITE)
        self.screen.blit(text, (15,15))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
    
    
    def new_sprites(self, gameinfo):
        if 'new_bullets' in gameinfo.keys():
            for bullet in gameinfo["new_bullets"]:
                bull =  Bullet(bullet[1], bullet[2], bullet[3], bullet[0])
                self.game.bullets.append(bull)
                self.bullets[bull.id] = self.game.bullets[-1]
                self.bullets_sprites[bullet[0]] = Draw_bullet(self.game.bullets[-1], self.screen)
                self.all_sprites.add(self.bullets_sprites[bullet[0]])
                #self.collision_group.add(self.bullets[i[0]]) # AÑADIDO
                
    '''
    def new_sprites(self, gameinfo):
        if 'new_bullets' in gameinfo.keys():
            for i in gameinfo["new_bullets"]:
                self.bullets[i[0]] = Bullet(i[1], i[2], i[3], i[0])
                self.bullets_sprites[i[0]] = Draw_bullet(self.bullets[i[0]], self.screen)
                self.all_sprites.add(self.bullets_sprites[i[0]])
                #self.collision_group.add(self.bullets[i[0]]) # AÑADIDO
        
    
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
    '''

    def delete_sprites(self, game_info):
        for (elem, elem_id) in game_info["delete"]:
            if elem == "bullet":
                print(elem_id)
                k1 = []
                for k, sprite in self.bullets_sprites.items():
                    if k == elem_id:
                        k1.append(k)
                        sprite.kill()
                for i in k1:
                    del self.bullets[i]
                    del self.bullets_sprites[i]
                 
            
    

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
            print(f"I am player {PLAYER[side]}")
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
                if gameinfo["is_running"] == False:
                    Win = gameinfo["WINNER"] 
                    font = pygame.font.Font(None, 90)
                    text = font.render(f"Winner player N {Win + 1}", True ,WHITE)
                    display.screen.blit(display.background, (0,0))
                    display.screen.blit(text, (SIZE[0]-250, 10))
                    time.sleep(10)
                    game.running = False
                else:
                    game.update(gameinfo)
                    display.new_sprites(gameinfo)
                    if 'delete' in gameinfo.keys():
                        display.delete_sprites(gameinfo)                
                
                display.refresh(gameinfo)
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
