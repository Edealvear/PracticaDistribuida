from multiprocessing.connection import Client
import time
import traceback
import pygame
import sys, os


WIDTH = 830
HEIGHT = 884
SIZE = (WIDTH, HEIGHT)

WHITE = (255,255,255)
FPS = 60

BullSize = 30
PlayerSize = 50

PLAYER = [1,2]



class Player():

    def __init__(self, num_P, pos =[None, None]):
        self.numP = num_P
        self.pos = pos

        self.direction = None

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
        self.screen.blit(self.image, self.player.pos) # Pinta el sprite image en la posicion pos el mundo
        self.update()
        #self.screen.blip(self.image, self.pos)
    
    def update(self):
        pos = self.player.get_pos()

        self.rect.centerx, self.rect.centery = pos

        self.screen.blit(self.image, pos)




class Game():

    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.running = True
    
    def getplayer(self, numP):
        return self.players[numP]
    
    def set_posplayer(self, numP, pos):
        self.players[numP].set_pos(pos)


    def update(self, game_info): 
        self.set_posplayer(0, game_info["pos_J1"])
        self.set_posplayer(1, game_info["pos_J2"])
        
        self.directions = game_info["dir"]
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

        self.collision_group = pygame.sprite.Group()
        self.all_sprites=pygame.sprite.Group()
        
        # No hace falta comprobarla colision manualmente, hay uncoando especifico que lo hace
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
        
        
        return events

    def refresh(self):
        self.all_sprites.update()
        self.screen.blit(self.background,(0,0))
        font = pygame.font.Font(None, 60)
        text = font.render(f"P1 || P2 ", True ,WHITE)
        self.screen.blit(text, (15,15))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

        

    def tick(self):
        self.clock.tick(FPS)
    
    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address):
    try:
        with Client((ip_address, 6000), authkey = b"password") as conn:
            game = Game()
            nplayer,gameinfo = conn.recv()
            print(f"I am player {PLAYER[nplayer]}")
            game.update(gameinfo)
            display = Display(game)
            
            while game.is_running():
                events = display.analyze_events(nplayer)
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

