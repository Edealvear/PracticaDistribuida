import os, pygame, time, random
from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

SIZE = (830, 884)

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



class Wall(pygame.sprite.Sprite):
    """
    Walls can't be passed by player.
    """
    def __init__(self, x, y, width, height):
        # Init.
        pygame.sprite.Sprite.__init__(self)
        self.pos = [x,y]
        self.height = height
        self.width = width
        #self.screen = screen
        # Create
        #self.image = pygame.Surface([width, height])
        #self.image.fill(color)
        #self.rect = self.image.get_rect()

    #def draw(self):
    #    pygame.draw.rect(self.screen, self.color, [self.pos[0], self.pos[1], self.width, self.height], 0)

class Power_UP():
    def __init__(self, type):
        self.type = type
        self.width = PowerUpSize
        self.height = PowerUpSize
        self.image = pygame.image.load(fr"bonus{type}.png")
        self.active=True
        self.pos = [383, 473]#Falta rellenar posicion
    
    def catched(self, player): 
        player.powerups[self.type] += 1
        self.active = False
    
class PowerUpImage(pygame.sprite.Sprite):
    def __init__(self, powerup):
        global screen
        self.width = PowerUpSize
        self.height = PowerUpSize
        super().__init__()
        self.pwup = powerup
        self.image = powerup.image
        screen.blip(self.image, powerup.pos)
    
    def update(self, powerup):
        if not powerup.active:
            self.image = pygame.image.load(r"nada.png")
            screen.blip(self.image, powerup.pos)
        
class Bullet():
    def __init__(self, NumP, position, direction, id, damage = 1, speed = 5):
        self.owner = NumP
        self.id = id
        self.width = BullSize
        self.height = BullSize
        self.active = True
        self.pos = position
        self.damage = damage
        self.speed = speed
        self.dir = direction#0 : izq; 1:arriba; 2:Der ; 3: abajo
        self.active = True

    def update(self):
        if self.dir == 0:
            self.pos[0] += self.speed
        elif self.dir == 1:
            self.pos[1] += self.speed
        elif self.dir == 2:
            self.pos[0] -= self.speed
        else:
            self.pos[1] -= self.speed	
    
    def getinfo(self):
        return [self.id, self.owner, self.pos, self.dir]
        
        
class Draw_bullet():
    def __init__(self, bullet):
        global screen
        self.width = BullSize
        self.height = BullSize
        super().__init__()
        self.pwup = bullet
        self.image = pygame.image.load(r"bullet.png")
        screen.blip(self.image, bullet.pos)
    
    def update(self, bullet):
        pass

# class Tank():
#     def __init__(self, pos):
#         self.pos = pos
#         self.width = PlayerSize
#         self.height = PlayerSize
    
#     def moveUp(self):
#         self.pos[1]-=3
#         self.dir = 1
#         if self.pos[1] < 0:
#             self.pos[1]=0
        

#     def moveDown(self):
#         self.dir = 3
#         self.pos[1]+=3
#         if self.pos[1] > SIZE[1]:
#             self.pos[1] = SIZE[1]
    
#     def moveLeft(self):
#         self.dir = 0
#         self.pos[0] -= 3
#         if self.pos[0]<0:
#             self.pos[0]=0

#     def moveRight(self):
#         self.dir = 2
#         self.pos[0] += 3 
#         if self.pos[0]>SIZE[0]:
#             self.pos[0] = SIZE[0]
        

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
            self.direction  = 2
        self.powerups = {
            "shield" : 0,
            "speed" : 0,
            "supershot" : 0
        }
        self.lives = 5
          

    
    def get_pos(self):
        return self.pos
    
    def set_pos(self, pos):
        self.pos = pos
    
    def moveUp(self):
        self.pos[1]-= (3 + self.powerups["speed"])
        self.dir = 1
        if self.pos[1] < 0:
            self.pos[1]=0
        

    def moveDown(self):
        self.dir = 3
        self.pos[1]+= (3 + self.powerups["speed"])
        if self.pos[1] > SIZE[1]:
            self.pos[1] = SIZE[1]
    
    def moveLeft(self):
        self.dir = 0
        self.pos[0] -= (3 + self.powerups["speed"])
        if self.pos[0]<0:
            self.pos[0]=0

    def moveRight(self):
        self.dir = 2
        self.pos[0] += (3 + self.powerups["speed"]) 
        if self.pos[0]>SIZE[0]:
            self.pos[0] = SIZE[0]

    def __str__(self):
        return f"Tank"

    def hit(self, bullet):
        if self.powerups["shield"] > 0:
            self.powerups["shield"] -= 1
        else:
            self.lives -= bullet.damage
    
    def add_Powerup(self, powerUp):
        if powerUp.type == 0:
            self.powerups["shield"] += 1
        elif powerUp.type == 1:
            self.powerups["speed"] += 1
        else:
            self.powerups["damage"] += 1

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

    def inic_walls(self):
        for i in range(12):
            if i == 0:
                self.walls.append(Wall(60, 155, 63, 273))
            elif i == 1:
                self.walls.append(Wall(186, 155, 63, 273))
            elif i == 2:
                self.walls.append(Wall(315, 155, 63, 213))
            elif i == 3:
                self.walls.append(Wall(439, 155, 63, 213))
            elif i == 4:
                self.walls.append(Wall(565, 155, 63, 273))
            elif i == 5:
                self.walls.append(Wall(690, 155, 63, 273))
            elif i == 6:
                self.walls.append(Wall(60, 554, 63, 273))
            elif i == 7:
                self.walls.append(Wall(186, 554, 63, 273))
            elif i == 8:
                self.walls.append(Wall(315, 610, 63, 213))
            elif i == 9:
                self.walls.append(Wall(439, 610, 63, 213))
            elif i == 10:
                self.walls.append(Wall(565, 554, 63, 273))
            else:
                self.walls.append(Wall(690, 554, 63, 273))

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
        p.moveUp()
        for wall in self.walls:
            if collide(wall, p):
                p.moveDown()
        self.players[player] = p
        self.lock.release()

    def moveDown(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveDown()
        for wall in self.walls:
            if collide(wall, p):
                p.moveUp()
        self.players[player] = p
        self.lock.release()

    def moveRight(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveRight()
        for wall in self.walls:
            if collide(wall, p):
                p.moveLeft()
        self.players[player] = p
        self.lock.release()

    def moveLeft(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveLeft()
        for wall in self.walls:
            if collide(wall, p):
                p.moveRight()
        self.players[player] = p
        self.lock.release()

    def get_info(self):
        self.lock.acquire()
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
            for i in self.new_bullets:
                self.new_bullets.remove(i)
            print("newbullets:",info["new_bullets"])
        if len(self.new_powerUps) > 0:
            info['new_powerUps'] = self.new_powerUps
        if len(self.elim) > 0:
            elim = []
            for i in self.elim:
                elim.append(i)
            info['delete'] = elim
            for i in self.elim:
                self.elim.remove(i)
        print(info)
        self.lock.release()
        return info

    def move_bullet(self):
        self.lock.acquire()
        for bull in self.bullets.values():
            bull.update()
            if bull.pos[0] < 0:
                self.elimbull(bull)
            elif bull.pos[0] > SIZE[0]:
                self.elimbull(bull)
            elif bull.pos[1] < 0:
                self.elimbull(bull)
            elif bull.pos[1] > SIZE[1]:
                self.elimbull(bull)
        self.lock.release()

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
        damage = self.players[numP].powerups["supershot"] + 1
        id = str(random.randint(0,1000))
        bullet = Bullet(owner, pos, dir, id, damage)
        self.bullets[id] = bullet
        self.new_bullets.append([id, owner, pos, dir])
        self.lock.release()

    def createPWUP(self, PWUP):
        self.lock.acquire()
        id = random.randint(0,1000)
        self.powerUps.append(Power_UP(id, PWUP))
        self.new_powerUps.append(id)
        self.lock.release()

    def getPWUP(self):
        self.lock.acquire()
        for player in self.players:
            if collide(player, self.powerUps[0]):
                player.add_Powerup(self.powerUps[0])
                self.delPWUP()
        self.lock.release()

    def delPWUP(self):
        self.lock.acquire()
        self.elim.append(("powerUp", self.powerUps[0].id))
        self.powerUps.pop()
        self.lock.release()

    def __str__(self):
        return f"G{self.running.value}>"


def player(nplayer, conn, game):
    try:
        print(f"starting player {PLAYER[nplayer]}:{game.get_info()}")
        conn.send( (nplayer, game.get_info()) )
        print("AAAAAAAAAAAAAAAAAAAAAAAAA")
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
                elif command == "ColPW":
                    pass #Puede que necesitemos hacer la funcion para la colision, no debería porque lo arreglo en el move del tanque 
                elif command == "getPWUP":
                    game.getPWUP()
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

def pUpManager(game):
    try:
        while game.is_running():
            time.sleep(5)
            game.createPWUP(random.randint(1,3))
            time.sleep(10)
            if game.pwUP != []:
                game.delPWUP
    finally:
        pass
            
def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address, 6000), authkey = b"password") as listener:
            n_player = 0
            players = [None, None]
            game = Game(manager)
            game.inic_walls()
            while True:
                print(f"accepting connection {n_player}")
                conn = listener.accept()
                players[n_player] = Process(target=player,
                                            args=(n_player, conn, game))
                n_player += 1
                if n_player == 2:
                    powerUpManager = Process(target = pUpManager,
                                             args = (game,))
                    players[0].start()
                    players[1].start()
                    
                    n_player = 0
                    players = [None, None]
                    game = Game(manager)
                    game.inic_walls()

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address)
