import os, pygame, time, random
from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

WIDTH = 830
HEIGHT = 884
SIZE = (WIDTH, HEIGHT)

MinMapa = 87

BullSize = 16

PowerUpSize = 50

PlayerSize = 50

PLAYER = [0,1]

def collide(a,b):
    col = False
    if a.pos[0] >= b.pos[0] and a.pos[1] >= b.pos[1]: 
        col = (a.pos[0]-b.pos[0] < a.width) and (a.pos[1]- b.pos[1] < a.height)
    elif a.pos[0] >= b.pos[0] and a.pos[1] < b.pos[1]:
        col = (a.pos[0]-b.pos[0] < a.width) and (b.pos[1]- a.pos[1] < b.height)
    elif a.pos[1] >= b.pos[1]:
        col = (b.pos[0]-a.pos[0] < b.width) and (a.pos[1]- b.pos[1] < a.height)
    else:
        col = (b.pos[0]-a.pos[0] < b.width) and (b.pos[1]- a.pos[1] < b.height)
    return col



        
class Bullet():
    def __init__(self, NumP, position, direction, id, speed = 30):
        self.owner = NumP
        self.id = id
        #self.width = BullSize
        #self.height = BullSize
        
        self.pos = position
        self.speed = speed
        self.dir = direction # 0: izq ; 1: arriba; 2: der ; 3: abajo
        self.active = True

    def update(self):
        if self.dir == 0:
            self.pos[0] -= self.speed

        elif self.dir == 1:
            self.pos[1] -= self.speed

        elif self.dir == 2:
            self.pos[0] += self.speed

        else:
            self.pos[1] += self.speed	
        
        

    
    def getinfo(self):
        return [self.id, self.owner, self.pos, self.dir]
    
    def get_pos(self):
        return self.pos   
        
'''
class Draw_bullet(pygame.sprite.Sprite):
    def __init__(self, bullet, screen):
        super().__init__()
        self.screen = screen
        
        self.image = pygame.image.load(r"bullet.png")
        screen.blip(self.image, bullet.pos)
    
   
    def update(self, bullet):
        pos = self.bullet.get_pos()
        self.rect.centerx, self.rect.centery = pos
        self.screen.blit(self.image, pos)
'''        
        

class Player():
    def __init__(self, num_P):
        
        self.numP = num_P
        self.width = PlayerSize
        self.height = PlayerSize
        if num_P == 0:
            self.pos = [30, 495]
            self.direction = 2
        else:
            self.pos = [350,495]
            self.direction  = 0
       
        self.lives = 5
          

    def get_pos(self):
        return self.pos
    
    def set_pos(self, pos):
        self.pos = pos
    
    
    def moveLeftP(self):
        self.direction = 0
        self.pos[0] -= (15)
        if self.pos[0] < 30:
            self.pos[0] = 30

    def moveUpP(self):
        self.pos[1]-= (15)
        self.direction= 1
        if self.pos[1] < 120:    # No puede entrar a la cabecera del tablero
            self.pos[1] = 120

    def moveRightP(self):
        self.direction = 2
        self.pos[0] += (15 ) 
        if self.pos[0] > WIDTH - 30:
            self.pos[0] = WIDTH - 30

    def moveDownP(self):
        self.direction = 3
        self.pos[1]+= (15)
        if self.pos[1] > HEIGHT - 30: 
            self.pos[1] = HEIGHT - 30


    



    def __str__(self):
        return f"Tank"

    def hit(self, bullet):
        self.lives -= 1

   
class Game():
    def __init__(self, manager):
        self.players = manager.list( [Player(0), Player(1)] )
        self.bullets = manager.dict({})
        self.walls = manager.list([])
        self.new_bullets = manager.list([])
        self.powerUps = manager.list([])
        self.new_powerUps = manager.list([])
        self.elim = manager.list([])
        self.score = manager.list( [5,5] )
        self.running = Value('i', 1) # 1 running
        self.lock = Lock()
        self.winner = Value('i',0) 

        self.check = Value('i',0)

    

    def get_player(self, side):
        return self.players[side]


    def get_score(self):
        return list(self.score)

    def is_running(self):
        return self.running.value == 1

    def stop(self):
        self.running.value = 0

    def moveUp(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveUpP()
        self.players[player] = p
        self.lock.release()

    def moveDown(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveDownP()
        self.players[player] = p
        self.lock.release()

    def moveRight(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveRightP()
        self.players[player] = p
        self.lock.release()

    def moveLeft(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveLeftP()
        self.players[player] = p
        self.lock.release()

    def get_info(self):
        
        info = {
            'pos_J1': self.players[0].get_pos(),
            'pos_J2': self.players[1].get_pos(),
            'dir': [self.players[0].direction, self.players[1].direction],
            'score': list(self.score),
            'is_running': self.running.value == 1,
            'WINNER': self.winner.value
        }
        if len(self.bullets.keys()) > 0:
            dicbull = []
            for key in self.bullets.keys():
                dicbull.append(self.bullets[key].getinfo())
            info['bullets'] = dicbull
            print(info["bullets"])

        if len(self.new_bullets) > 0:
            newbull = []
            for i in self.new_bullets:
                newbull.append(i)
            info['new_bullets'] = newbull

            if self.check.value >= 1:
                for i in self.new_bullets:
                    self.new_bullets.remove(i)
            print("newbullets:",info["new_bullets"])
            
        if len(self.elim) > 0:
            elim = []
            for i in self.elim:
                elim.append(i)
            info['delete'] = elim
            if self.check.value >= 1:
                for i in self.elim:
                    self.elim.remove(i)
        
        if self.check.value ==1:
            self.check.value = 0
        else:
            self.check.value += 1

        return info

    def move_bullet(self):
        self.lock.acquire()
        for (id, bull) in self.bullets.items():
            bull.update()
            self.bullets[id] = bull 
            if bull.pos[0] < 0:
                self.elimbull(bull)
            elif bull.pos[0] > SIZE[0]:
                self.elimbull(bull)
            elif bull.pos[1] < 0:
                self.elimbull(bull)
            elif bull.pos[1] > SIZE[1]:
                self.elimbull(bull)
            print(f'POSI NUEVA: {bull.pos}')
        self.lock.release()
    '''
    def move_bullet(self):
        self.lock.acquire()
        for bull in self.bullets.values():
            bull.update()
            print(f'POSI NUEVA: {bull.pos}')
            if bull.pos[0] < 0:
                self.elimbull(bull)
            elif bull.pos[0] > SIZE[0]:
                self.elimbull(bull)
            elif bull.pos[1] < 0:
                self.elimbull(bull)
            elif bull.pos[1] > SIZE[1]:
                self.elimbull(bull)
            print(f'POSI NUEVA: {bull.pos}')
        self.lock.release()
    '''
    def elimbull(self, bull):
        self.elim.append(("bullet", bull.id))
        del self.bullets[bull.id]
    
    def HitPlayer(self):
        self.lock.acquire()
        for bull in self.bullets.values:
            for player in self.players:
                if collide(bull, player):
                    player.hit(bull)
                    self.elimbull(bull)
                    self.score[player.numP] = player.lives
        self.lock.release()

    def collide_BW(self, id):
        self.lock.acquire()
        for idn, bull in self.bullets.items():
            if idn == id:   

        #     for wall in self.walls:
        #         if collide(bull, wall):
        #             self.elimbull(bull)
                print(self.bullets, flush = True )
                self.elimbull(bull)
        self.lock.release()

    def shoot(self, numP):
        self.lock.acquire()
        owner = numP
        pos = self.players[numP].pos
        dir = self.players[numP].direction
        
        id = str(random.randint(0,1000))

        # Creacion de las balas delante del tanque segun la direccion que tenga
        if dir == 0:
            pos[0] = pos[0] - 45
            bullet = Bullet(owner, pos, dir, id)

        elif dir == 1:
            pos[1] = pos[1] - 45
            bullet = Bullet(owner, pos, dir, id)

        elif dir == 2:
            pos[0] = pos[0] + 45
            bullet = Bullet(owner, pos, dir, id)

        else:
            pos[1] = pos[1] + 45
            bullet = Bullet(owner, pos, dir, id)    
        

        self.bullets[id] = bullet
        self.new_bullets.append([id, owner, pos, dir])
        self.lock.release()

    

    

    def __str__(self):
        return f"G{self.running.value}>"


def player(nplayer, conn, game):
    try:
        print(f"starting player {PLAYER[nplayer]}:{game.get_info()}")
        conn.send( (nplayer, game.get_info()) )
        while game.is_running():
            command = ""
            while command != "next":
                command = conn.recv()
                print(command)
                if command == "Up":
                    game.moveUp(nplayer)
                elif command == "Down":
                    game.moveDown(nplayer)
                elif command == "Left":
                    game.moveLeft(nplayer)
                elif command == "Right":
                    game.moveRight(nplayer)
                elif command == "Space":
                    game.shoot(nplayer)
                elif command == "ColBW":
                    id = conn.recv()
                    game.collide_BW(id)
                elif command == "Playerhit":
                    game.HitPlayer()
                
                elif command == "quit":
                    game.stop()
            if nplayer == 1:
                game.move_bullet()
                if game.score[0] == 0:
                    game.running.value = 0
                    game.winner.value = 1
                elif game.score[1] == 0:
                    game.running.value = 0
                    game.winner.value = 0
            
            conn.send(game.get_info())
    except:
        traceback.print_exc()
        conn.close()
    finally:
        game.running.value = 0
        print(f"Game ended {game}")

         
def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000), authkey = b"password") as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                   
                    players[0].start()
                    players[1].start()
                    
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)


    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
