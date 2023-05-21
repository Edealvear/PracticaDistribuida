from multiprocessing.connection import Client
import time
import traceback
import pygame
import sys, os

SIZE = (830, 884)
WHITE = (255,255,255)
FPS = 60


BullSize = 30

PlayerSize = 50

PLAYER = [1,2]

NWALL= 31   # Numero de muros en el tablero


class Bullet():#Clase de las balas
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
        


class Draw_bullet(pygame.sprite.Sprite):#Clase para dibujar las balas
    def __init__(self, bullet, screen):
        super().__init__()
        self.screen = screen
        self.bullet = bullet
        self.image = pygame.image.load(r"bullet.png")#Cargamos la imagen
        self.screen.blit(self.image, self.bullet.pos)#La dibujamos
        self.rect = self.image.get_rect()
        self.update()


    def update(self) -> None: #Para actualizar la posicion del sprite 
        pos = self.bullet.get_pos()
        self.rect.centerx, self.rect.centery = pos
        self.screen.blit(self.image, pos)


class Player():#Clase del jugador
    def __init__(self, num_P, pos =[None, None]):
        self.numP = num_P
        self.pos = pos
        self.lives = 5
        self.direction  = None 

    
    def get_pos(self):
        return self.pos
    
    def get_dir(self):
        return self.direction
        

    def set_pos(self, pos):
        self.pos = pos

    def set_dir(self,dir):
        self.direction = dir
        

    def __str__(self):
        return f"Tank {self.numP}"
    

class Player_display(pygame.sprite.Sprite):#Clase para dibujar el sprite del jugador
    def __init__(self, player, screen):
        super().__init__()
        self.dir = 0
        self.screen = screen
        self.player = player 
        self.image = pygame.image.load(rf"TanqueP{self.player.numP + 1}_left.png")#Cargamos la imagen
        self.rect = self.image.get_rect()
        self.screen.blit(self.image, self.player.pos)
        self.update()
    
    def update(self):#Para actualizar la posicion del sprite 
        pos = self.player.get_pos()
        dir = self.player.get_dir()
        self.rect.centerx, self.rect.centery = pos
        self.screen.blit(self.image, pos)
        #si cambia la direccion a la que apunta el jugador cambiamos la imagen para que este a corde con la direccion 
        if dir == 0:
            
            self.image = pygame.image.load(rf"TanqueP{self.player.numP + 1}_left.png")
        elif dir == 1:
            
            self.image = pygame.image.load(rf"TanqueP{self.player.numP + 1}_up.png")
        elif dir == 2:
            
            self.image = pygame.image.load(rf"TanqueP{self.player.numP + 1}_right.png")
        elif dir == 3:
        
            self.image = pygame.image.load(rf"TanqueP{self.player.numP + 1}_down.png")



class Wall():#Clase de las paredes
    def __init__(self, num_W, pos = [None, None]):
        self.numW = num_W
        self.pos = pos

    def get_pos(self):
        return self.pos        

    def set_pos(self, pos):
        self.pos = pos

    def __str__(self):
        return f"Wall {self.numW}"

class Wall_display(pygame.sprite.Sprite):#Clase para dibujar las paredes
    def __init__(self, wall, screen):
        super().__init__()

        self.screen = screen
        self.wall = wall
        self.image = pygame.image.load(r"Wall.png")#Cargamos la imagen
        self.screen.blit(self.image, self.wall.pos)        
        self.rect = self.image.get_rect()
        self.update()

    def update(self):#Para que se recarguen las paredes en el siguiente frame
        pos = self.wall.get_pos()
        self.rect.centerx, self.rect.centery = pos
        self.screen.blit(self.image, pos)        




class Game():#Clase del juego 
    def __init__(self):
        self.players = [Player(i) for i in range(2)]
        self.walls = [Wall(i) for i in range(NWALL)]

        self.bullets = []
        self.new_bullets = []
        self.to_erase_bullets = [] 

        self.score = [5,5]
    
        self.running = True
    
    def getplayer(self, numP):
        return self.players[numP]
    
    def set_posplayer(self, numP, pos):
        self.players[numP].set_pos(pos)

    def set_poswalls(self, numW, pos):
        self.walls[numW].set_pos(pos)

    def set_dirplayer(self,numP,dir):
        self.players[numP].set_dir(dir)

    
    def getwall(self, numW):
        return self.walls[numW]

    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score
    
    def update(self, game_info):#metodo que actualiza la informacion del juego segun lo que le llega de la sala
        self.set_posplayer(0, game_info["pos_J1"])
        self.set_posplayer(1, game_info["pos_J2"])

        self.set_dirplayer(0, game_info["dir"][0])
        self.set_dirplayer(1, game_info["dir"][1])
        self.score = game_info["score"]

        for i in range(NWALL):#util para inicializar las paredes 
            self.set_poswalls(i, game_info["pos_walls"][i])

        #para actualizar las balas 
        self.update_bullets(game_info)


    def update_bullets(self, game_info): #Para actualizar las balas 
        self.new_bullets= [] # Reinicio la lista de nuevas en el frame anterior

        is_erased_bullet = True
        is_new_bullet = True

        # Bucle para actualizar posicion de balas y detectar las que no estan
        for old_bull in self.bullets:                   # Las que habia
            for actual_bull in game_info["bullets"]:    # Las que hay
                if old_bull.id == actual_bull[0]:
                    old_bull.pos = actual_bull[2]
                    is_erased_bullet = False  
                        
            if is_erased_bullet:        #Si la bala anterior no esta en la lista nueva la metemos en una lista para borrarlas juntas despues
                self.to_erase_bullets.append(old_bull)

            is_erased_bullet = True     # Lo reiniciamos para la siguiente vuelta

        # Bucle para crear balas nuevas
        for actual_bull in game_info["bullets"]:     # Las que hay 
            for old_bull in self.bullets:            # Las que habia
                if old_bull.id == actual_bull[0]:
                    is_new_bullet = False  

            if is_new_bullet:
                new_bull =  Bullet(actual_bull[1], actual_bull[2], actual_bull[3], actual_bull[0])
                self.bullets.append(new_bull)
                self.new_bullets.append(new_bull)

            is_new_bullet = True        # Lo reiniciamos para la siguiente vuelta
   
    def is_running(self):
        return self.running
    
    def stop(self):
        self.running = False


    
class Display():#Clase que controla el display del juego 
    def __init__(self, game):#inicializamos todo
        self.screen = pygame.display.set_mode(SIZE)
        self.game = game

        self.tanks = [game.getplayer(i) for i in range(2)]
        self.tanks_sprites = [Player_display(self.tanks[i], self.screen) for i in range(2)]
        
        self.bullets = {}
        self.bullets_sprites = {}
        
        self.walls = [game.getwall(i) for i in range(NWALL)] 
        self.walls_sprites = [Wall_display(self.walls[i], self.screen) for i in range(NWALL)]

        self.collision_group = pygame.sprite.Group()
        self.all_sprites=pygame.sprite.Group()
        
        #metemos los tanques y las paredes en los grupos de colision y de todos los sprites
        for i in range(2):
            self.collision_group.add(self.tanks_sprites[i])
            self.all_sprites.add(self.tanks_sprites[i])

        for i in range(NWALL):
            self.collision_group.add(self.walls_sprites[i])
            self.all_sprites.add(self.walls_sprites[i])

        self.background = pygame.image.load("Mapa.png")#Cargamos la imagen del mapa
        self.clock = pygame.time.Clock()
        pygame.init()
    


    def analyze_events(self, NumP):#Analiza los eventos del juego para mandarle la informacion a la sala
        events = []
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:#cerrar la partida
                    events.append("quit")
                elif event.key == pygame.K_DOWN:#mover el tanque hacia abajo
                    self.tanks_sprites[NumP].dir = 3
                    events.append("Down")
                elif event.key == pygame.K_UP:#mover el tanque arriba
                    self.tanks_sprites[NumP].dir = 1
                    events.append("Up")
                elif event.key == pygame.K_LEFT:#mover el tanque a la izq
                    self.tanks_sprites[NumP].dir = 0
                    events.append("Left")
                elif event.key == pygame.K_RIGHT:#mover el tanque a la derecha
                    self.tanks_sprites[NumP].dir = 2
                    events.append("Right")
                elif event.key == pygame.K_SPACE:#disparar
                    events.append("Space")

            elif event.type == pygame.QUIT:
                events.append("quit")
        #Para ver si algun jugador recibe un disparo
        for bullet in self.bullets_sprites.values():
            for player in self.tanks_sprites:
                if player.player.numP != bullet.bullet.owner and pygame.sprite.collide_rect(player, bullet):
                    
                    events.append("Playerhit")
                    
        
        return events

    def refresh(self):#Actualiza la pantalla
        self.paint_new_bullets()#Si hay que crear nuevas balas las crea
        self.erase_old_bullets()#si hay que eliminar otras las elimina
        #Actualiza el resto de los sprites y los pinta
        self.all_sprites.update()
        self.screen.blit(self.background,(0,0))
        score = self.game.get_score()
        font = pygame.font.Font(None, 60)
        text = font.render(f"       Lives P1: {score[0]}        ||        Lives P2: {score[1]}", True ,WHITE)#Pinta la cabecera con las vidas que les quedan a cada jugador
        self.screen.blit(text, (15,15))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
    

    def paint_new_bullets(self):#Crea las nuevas balas
        for bullet in self.game.new_bullets:

            self.bullets_sprites[bullet.id] = Draw_bullet(bullet, self.screen)
            self.all_sprites.add(self.bullets_sprites[bullet.id])

    def erase_old_bullets(self):#Elimina las antiguas
        for bullet in self.game.to_erase_bullets:
            self.bullets_sprites[bullet.id].kill()
          

    def tick(self):
        self.clock.tick(FPS)
    
    @staticmethod
    def quit():
        pygame.quit()



def main(ip_address):#crea la conexion con la sala y va mandando y recibiendo informacion
    try:
        with Client((ip_address, 6000), authkey = b"password") as conn:
            game = Game()
            side,gameinfo = conn.recv()
            print(f"I am player {PLAYER[side]}")
            game.update(gameinfo)
            display = Display(game)
            
            while game.is_running():#mientras el juego esta corriendo en la sala
                events = display.analyze_events(side)#Recopilamos toda la info mandada por el jugador y el display
                for ev in events:
                    conn.send(ev)#La mandamos 
                    if ev == 'quit':#Si es terminar la partida la terminamos
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()#Recibimos la informacion de la sala
                if gameinfo["is_running"] == 0:#Si la sala dice que ha terminado la partida
                    if gameinfo["is_over"] == 1:#si dice que ha terminado de forma correcta, es decir que uno de los jugadores se ha quedado sin vidas
                        Win = gameinfo["WINNER"] #Vemos quien es el ganador
                        font = pygame.font.Font(None, 90)
                        display.all_sprites.clear(display.screen, display.background)
                        display.screen.blit(display.background, (0,0))
                        #muestra por la pantalla del juego si eres el ganador o el perdedor 
                        if side == Win:
                            text = font.render("You Win", True ,WHITE)
                        else:
                            text = font.render("You Lose", True ,WHITE)
                        display.screen.blit(text, ( SIZE[0]/2,SIZE[1]/2))
                        pygame.display.flip()
                        time.sleep(5)
                        game.running = False
                        
                else:
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
