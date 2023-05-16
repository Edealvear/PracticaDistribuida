import os, pygame, time, random
from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock, Condition
import traceback
import sys

WIDTH = 830
HEIGHT = 884
SIZE = (WIDTH, HEIGHT)

MinMapa = 87

BullSize = 30

PowerUpSize = 50

PlayerSize = 50

PLAYER = [0,1]

NWALL= 41



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
        self.width = BullSize
        self.height = BullSize
        
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
        


class Player():
    def __init__(self, num_P,game):

        self.game = game
        self.numP = num_P
        self.width = PlayerSize
        self.height = PlayerSize
        if num_P == 0:
            self.pos = [195, 442]
            self.direction = 0
        else:
            self.pos = [635, 442]
            self.direction  = 2
       
        self.lives = 5
          

    def get_pos(self):
        return self.pos
    
    def set_pos(self, pos):
        self.pos = pos

    def collide(self,a,b,dx,dy):
        
        col = False
        if a.pos[0]+dx >= b.pos[0] and a.pos[1]+dy >= b.pos[1]: 
            col = (a.pos[0]+dx-b.pos[0] < a.width) and (a.pos[1]+dy- b.pos[1] < a.height)
        elif a.pos[0]+dx >= b.pos[0] and a.pos[1]+dy < b.pos[1]:
            col = (a.pos[0]+dx-b.pos[0] < a.width) and (b.pos[1]- (a.pos[1]+dy) < b.height)
        elif a.pos[1]+dy >= b.pos[1]:
            col = (b.pos[0]-(a.pos[0]+dx) < b.width) and (a.pos[1]+dy- b.pos[1] < a.height)
        else:
            col = (b.pos[0]-(a.pos[0]+dx) < b.width) and (b.pos[1]- (a.pos[1]+dy) < b.height)
        return col
    
    def collide_with_walls(self, dx=0, dy=0):
        for wall in self.game.walls:
            if self.collide(self,wall,dx,dy):
                return True
        return False
    def moveLeftP(self):
        if not self.collide_with_walls(-15,0):
            self.direction = 0
            self.pos[0] -= (15)
            if self.pos[0] < 30:
                self.pos[0] = 30
        

    def moveUpP(self):
        if not self.collide_with_walls(0,-15):
            self.pos[1]-= (15)
            self.direction= 1
            if self.pos[1] < 30:    # No puede entrar a la cabecera del tablero
                self.pos[1] = 30
        
            

    def moveRightP(self):
        if not self.collide_with_walls(15,0):
            self.direction = 2
            self.pos[0] += (15 ) 
            if self.pos[0] > WIDTH - 30:
                self.pos[0] = WIDTH - 30

    def moveDownP(self):
        if not self.collide_with_walls(0,15):
            self.direction = 3
            self.pos[1]+= (15)
            if self.pos[1] > HEIGHT - 30: 
                self.pos[1] = HEIGHT - 30


    def __str__(self):
        return f"Tank"

    def hit(self, bullet):
        self.lives -= 1

class Wall():
    def __init__(self, num_W):
        
        self.width = PlayerSize
        self.height = PlayerSize
        self.numW = num_W

        #Creacion de muros
        if num_W == 0:
            self.pos = [305, 442] # centrales
        elif num_W == 1:
            self.pos = [360, 442]
        elif num_W == 2:
            self.pos = [415, 442]
        elif num_W == 3:
            self.pos = [470, 442]
        elif num_W == 4:
            self.pos = [525, 442]

        elif num_W == 5:
            self.pos = [90, 90] # Esquina superior izquierda horizontal
        elif num_W == 6:
            self.pos = [145, 90]
        elif num_W == 7:
            self.pos = [200, 90]
        elif num_W == 8:
            self.pos = [255, 90]
        elif num_W == 9:
            self.pos = [310, 90]

        elif num_W == 10:
            self.pos = [90, 794] # Esquina inferior izquierda horizontal
        elif num_W == 11:
            self.pos = [145, 794]
        elif num_W == 12:
            self.pos = [200, 794]
        elif num_W == 13:
            self.pos = [255, 794]
        elif num_W == 14:
            self.pos = [310, 794]
            
        elif num_W == 15:
            self.pos = [740, 90] # Esquina superior der horizontal
        elif num_W == 16:
            self.pos = [685, 90]
        elif num_W == 17:
            self.pos = [630, 90]
        elif num_W == 18:
            self.pos = [575, 90]
        elif num_W == 19:
            self.pos = [520, 90] 

        elif num_W == 20:
            self.pos = [740, 794] # Esquina inferior der horizontal
        elif num_W == 21:
            self.pos = [685, 794]
        elif num_W == 22:
            self.pos = [630, 794]
        elif num_W == 23:
            self.pos = [575, 794]
        elif num_W == 24:
            self.pos = [520, 794]

        elif num_W == 25:           # C izq
            self.pos = [145, 210] 
        elif num_W == 26:
            self.pos = [200, 210]
        elif num_W == 27:
            self.pos = [255, 210]
        elif num_W == 28:           
            self.pos = [255, 267]
        elif num_W == 29:
            self.pos = [255, 324]
        elif num_W == 30:
            self.pos = [200, 324] 
        elif num_W == 31:
            self.pos = [145, 324]

        elif num_W == 32:           # C der
            self.pos = [685, 210]
        elif num_W == 33:
            self.pos = [630, 210]
        elif num_W == 34:
            self.pos = [575, 210]
        elif num_W == 35:           
            self.pos = [575, 267]
        elif num_W == 36:
            self.pos = [575, 324]
        elif num_W == 37:
            self.pos = [630, 324] 
        elif num_W == 38:
            self.pos = [685, 324]

        elif num_W == 39:           # solo izq
            self.pos = [200, 622]

        else:                       # solo der   
            self.pos = [630, 622]
        

       
    def get_pos(self):
        return self.pos
    
    def __str__(self):
        return f"Wall"

   
class Game():
    def __init__(self, manager):
        self.walls = manager.list( [Wall(i) for i in range(NWALL)] )
        self.players = manager.list( [Player(0,self), Player(1,self)] )
        self.bullets = manager.dict({})

        

        self.new_bullets = manager.list([])

        self.powerUps = manager.list([])
        self.new_powerUps = manager.list([])

        self.elim = manager.list([])
        self.score = manager.list( [5,5] )

        self.running = Value('i', 1) # 1 running
        self.lock = Lock()
        
        self.turn = Condition(self.lock)
        self.winner = Value('i',0) 

        self.check = Value('i',0)
        self.sendnbull = Value('i',0)
        self.senddelbull = Value('i', 0)

    
    def get_player(self, side):
        return self.players[side]

    def get_wall(self, side):
        return self.walls[side]

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

    def get_info(self, num):
        self.lock.acquire()
        self.turn.wait_for(lambda: num != self.check.value)
        
        info = {
            'pos_J1': self.players[0].get_pos(),
            'pos_J2': self.players[1].get_pos(),
            'dir': [self.players[0].direction, self.players[1].direction],
            'pos_walls': [self.walls[i].get_pos() for i in range(NWALL)],
            
            'score': list(self.score),
            'is_running': self.running.value,
            'WINNER': self.winner.value
        }
        if len(self.bullets.keys()) > 0:
            dicbull = []
            for key in self.bullets.keys():
                dicbull.append(self.bullets[key].getinfo())
            info['bullets'] = dicbull
            print(info['bullets'])

        if len(self.new_bullets) > 0:
            newbull = []
            for i in self.new_bullets:
                newbull.append(i)
            info['new_bullets'] = newbull

            if self.sendnbull.value == 1:
                for i in self.new_bullets:
                    self.new_bullets.remove(i)
                self.sendnbull.value = 0
            else:
                self.sendnbull.value = 1
            
        if len(self.elim) > 0:
            elim = []
            for i in self.elim:
                elim.append(i)
            info['delete'] = elim
            print(info['delete'])
            if self.senddelbull.value == 1:
                for i in self.elim:
                    self.elim.remove(i)
                self.senddelbull.value = 0
            else:
                self.senddelbull.value = 1
                 
        self.check.value = 1 - self.check.value
        
        self.turn.notify()
        self.lock.release()
        return info

    def collide(self,a,b,dx,dy):
        
        col = False
        if a.pos[0]+dx >= b.pos[0] and a.pos[1]+dy >= b.pos[1]: 
            col = (a.pos[0]+dx-b.pos[0] < a.width) and (a.pos[1]+dy- b.pos[1] < a.height)
        elif a.pos[0]+dx >= b.pos[0] and a.pos[1]+dy < b.pos[1]:
            col = (a.pos[0]+dx-b.pos[0] < a.width) and (b.pos[1]- (a.pos[1]+dy) < b.height)
        elif a.pos[1]+dy >= b.pos[1]:
            col = (b.pos[0]-(a.pos[0]+dx) < b.width) and (a.pos[1]+dy- b.pos[1] < a.height)
        else:
            col = (b.pos[0]-(a.pos[0]+dx) < b.width) and (b.pos[1]- (a.pos[1]+dy) < b.height)
        return col
    
    def collide_with_walls(self,object, dx=0, dy=0):
        for wall in self.walls:
            if self.collide(object,wall,dx,dy):
                return True
        return False

    def move_bullet(self):
        self.lock.acquire()
        for (id, bull) in self.bullets.items():
            if bull.dir == 0:
                if not self.collide_with_walls(bull,-bull.speed,0):
                    bull.update()
                else:
                    self.elimbull(bull)

            elif bull.dir == 1:
                if not self.collide_with_walls(bull,0,-bull.speed):
                    bull.update()
                else:
                    self.elimbull(bull)

                            
            elif bull.dir == 2:
                if not self.collide_with_walls(bull,bull.speed,0):
                    bull.update()
                else:
                    self.elimbull(bull)


            else:
                if not self.collide_with_walls(bull, 0,bull.speed):
                    bull.update()
                else:
                    self.elimbull(bull)
            
            self.bullets[id] = bull 
            if bull.pos[0] < -50:
                self.elim.append(("bullet", bull.id))
                del self.bullets[bull.id]
            elif bull.pos[0] > SIZE[0] +50:
                self.elimbull(bull)
            elif bull.pos[1] < -50:
                self.elimbull(bull)
            elif bull.pos[1] > SIZE[1]+50:
                self.elimbull(bull)
        self.lock.release()



    def elimbull(self, bull):
        self.elim.append(("bullet", bull.id))
        del self.bullets[bull.id]
        self.bullets = self.bullets
    


    def HitPlayer(self):
        self.lock.acquire()
        for bull in self.bullets.values():
            for player in self.players:
                if collide(bull, player):
                    player.lives -= 1
                    self.players[player.numP] = player
                    self.elimbull(bull)
                    self.score[player.numP] = player.lives
                    print(player.lives)
                if player.lives == 0:
                    self.running.value = 0
                    self.winner.value = 1 - player.numP 
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
        print(f"starting player {PLAYER[nplayer]}:{game.get_info(nplayer)}")
        conn.send( (nplayer, game.get_info(nplayer)) )
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
            
            conn.send(game.get_info(nplayer))
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
            #game.inic_walls()
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
                    #game.inic_walls()


    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
