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

PlayerSize = 50

PLAYER = [0,1]

NWALL= 31  # Numero de muros en el tablero


def collide_player(a,b): 
    """
    a: tipo Bullet()
    b: Player()
    
    devuelve: True si una bala que no sea de b, colisiona con b
              False en otro caso
    """
    col = False
    if a.owner != b.numP:
        if a.pos[0] >= b.pos[0] and a.pos[1] >= b.pos[1]:
            col = (a.pos[0]-b.pos[0] < a.width) and (a.pos[1]- b.pos[1] < a.height)
        elif a.pos[0] >= b.pos[0] and a.pos[1] < b.pos[1]:
            col = (a.pos[0]-b.pos[0] < a.width) and (b.pos[1]- a.pos[1] < b.height)
        elif a.pos[1] >= b.pos[1]:
            col = (b.pos[0]-a.pos[0] < b.width) and (a.pos[1]- b.pos[1] < a.height)
        else:
            col = (b.pos[0]-a.pos[0] < b.width) and (b.pos[1]- a.pos[1] < b.height)
    return col


class Bullet():#Clase de las balas 
    def __init__(self, NumP, position, direction, id, speed = 30):
        self.owner = NumP
        self.id = id
        self.width = BullSize
        self.height = BullSize
        self.pos = position
        self.speed = speed
        self.dir = direction # 0: izq ; 1: arriba; 2: der ; 3: abajo
        self.active = True


    def update(self):#Hace avanzar a las balas segun su direccion
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



class Player():#clase del objeto controlado por el jugador, el tanque
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



    def collide(self,b,dx,dy):#para ver si el Player colisiona con el objeto b

        col = False
        if self.pos[0]+dx >= b.pos[0] and self.pos[1]+dy >= b.pos[1]:
            col = (self.pos[0]+dx-b.pos[0] < self.width) and (self.pos[1]+dy- b.pos[1] < self.height)
        elif self.pos[0]+dx >= b.pos[0] and self.pos[1]+dy < b.pos[1]:
            col = (self.pos[0]+dx-b.pos[0] < self.width) and (b.pos[1]- (self.pos[1]+dy) < b.height)
        elif self.pos[1]+dy >= b.pos[1]:
            col = (b.pos[0]-(self.pos[0]+dx) < b.width) and (self.pos[1]+dy- b.pos[1] < self.height)
        else:
            col = (b.pos[0]-(self.pos[0]+dx) < b.width) and (b.pos[1]- (self.pos[1]+dy) < b.height)
        return col


    def collide_with_walls(self, dx=0, dy=0):#Usar la funcion collide anterior para ver si el Player chocara con alguna pared al moverse
        for wall in self.game.walls:
            if self.collide(wall,dx,dy):
                return True
        return False


    def moveLeftP(self):#metodo para mover al Player a la izq
        if not self.collide_with_walls(-15,0):
            self.direction = 0
            self.pos[0] -= (15)
            if self.pos[0] < 30:#Para que no se salga de la pantalla
                self.pos[0] = 30


    def moveUpP(self):#Mover arriba al Player
        if not self.collide_with_walls(0,-15):
            self.pos[1]-= (15)
            self.direction= 1
            if self.pos[1] < 120:    # No puede entrar a la cabecera del tablero
                self.pos[1] = 120



    def moveRightP(self):#mover a la derecha
        if not self.collide_with_walls(15,0):
            self.direction = 2
            self.pos[0] += (15 )
            if self.pos[0] > WIDTH - 30:#Para que no se salga de la pantalla
                self.pos[0] = WIDTH - 30

    def moveDownP(self):#mover hacia abajo
        if not self.collide_with_walls(0,15):
            self.direction = 3
            self.pos[1]+= (15)
            if self.pos[1] > HEIGHT - 30:#Para que no se salga de la pantalla
                self.pos[1] = HEIGHT - 30


    def __str__(self):
        return f"Tank"

    def hit(self, bullet):#Pérdida de vida cuando una bala colisione 
        self.lives -= 1

class Wall():#Clase de las paredes
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
            self.pos = [90, 794] # Esquina inferior izquierda horizontal
        elif num_W == 6:
            self.pos = [145, 794]
        elif num_W == 7:
            self.pos = [200, 794]
        elif num_W == 8:
            self.pos = [255, 794]
        elif num_W == 9:
            self.pos = [310, 794]
        

        elif num_W == 10:
            self.pos = [740, 794] # Esquina inferior der horizontal
        elif num_W == 11:
            self.pos = [685, 794]
        elif num_W == 12:
            self.pos = [630, 794]
        elif num_W == 13:
            self.pos = [575, 794]
        elif num_W == 14:
            self.pos = [520, 794]

        elif num_W == 15:           # C izq
            self.pos = [145, 210]
        elif num_W == 16:
            self.pos = [200, 210]
        elif num_W == 17:
            self.pos = [255, 210]
        elif num_W == 18:
            self.pos = [255, 267]
        elif num_W == 19:
            self.pos = [255, 324]
        elif num_W == 20:
            self.pos = [200, 324]
        elif num_W == 21:
            self.pos = [145, 324]

        elif num_W == 22:           # C der
            self.pos = [685, 210]
        elif num_W == 23:
            self.pos = [630, 210]
        elif num_W == 24:
            self.pos = [575, 210]
        elif num_W == 25:
            self.pos = [575, 267]
        elif num_W == 26:
            self.pos = [575, 324]
        elif num_W == 27:
            self.pos = [630, 324]
        elif num_W == 28:
            self.pos = [685, 324]

        elif num_W == 29:           # solo izq
            self.pos = [200, 622]

        else:                       # solo der
            self.pos = [630, 622]



    def get_pos(self):
        return self.pos

    def __str__(self):
        return f"Wall"


class Game():#Clase del juego 
    def __init__(self, manager):#Usaremos un manager para compartir entre los procesos de los jugadores la informacion del juego
        self.walls = manager.list( [Wall(i) for i in range(NWALL)] )
        self.players = manager.list( [Player(0,self), Player(1,self)] )
        self.bullets = manager.dict({})


        self.score = manager.list( [5,5] )
        self.id = Value('i',0) #Entero que representa el numero id de cada bala

        self.running = Value('i', 1) # 1 running
        self.lock = Lock()#Lock a modo de mutex para evitar errores en la concurrencia

        self.winner = Value('i',0)#Para guardar el ganador, inicializado a 0 por poner algo
        self.is_over = Value('i',0) #1 si se ha terminado de forma correcta la partida

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

    def moveUp(self, player):#Mover arriba el jugador
        self.lock.acquire()
        p = self.players[player]
        p.moveUpP()
        self.players[player] = p
        self.lock.release()

    def moveDown(self, player):#Mover abajo el jugador
        self.lock.acquire()
        p = self.players[player]
        p.moveDownP()
        self.players[player] = p
        self.lock.release()

    def moveRight(self, player):#Mover a la derecha el jugador
        self.lock.acquire()
        p = self.players[player]
        p.moveRightP()
        self.players[player] = p
        self.lock.release()

    def moveLeft(self, player):#Mover izquierda el jugador
        self.lock.acquire()
        p = self.players[player]
        p.moveLeftP()
        self.players[player] = p
        self.lock.release()

    def get_info(self, num):#funcion para recoger en un diccionario la informacion de la partida
        self.lock.acquire()

        info = {
            'pos_J1': self.players[0].get_pos(),
            'pos_J2': self.players[1].get_pos(),
            'dir': [self.players[0].direction, self.players[1].direction],
            'pos_walls': [self.walls[i].get_pos() for i in range(NWALL)],
            'is_over' : self.is_over.value,

            'score': list(self.score),
            'is_running': self.running.value,
            'WINNER': self.winner.value,
            'bullets': [self.bullets[key].getinfo() for key in self.bullets.keys()]
        }
        
        self.lock.release()
        return info


    def collide(self,a,b,dx,dy):# para ver si el objeto a colisionara con el b al moverse dx en la primera 
                                # coordenada y dy en la segunda

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



    def collide_with_walls(self,obj, dx=0, dy=0):#Para ver si obj va a colisionar con alguna de las paredes
        for wall in self.walls:
            if self.collide(obj,wall,dx,dy):
                return True
        return False


    def move_bullet(self):#Metodo para mover las balas
        self.lock.acquire()
        for (id, bull) in self.bullets.items():
            if bull.dir == 0:
                if not self.collide_with_walls(bull,-bull.speed,0):#Si no colisionan con una pared que se mueva en la direccion  0 
                    bull.update()
                    self.bullets[id] = bull
                else:#Si colisionan con una pared que se elimine
                    self.elimbull(bull)

            elif bull.dir == 1:
                if not self.collide_with_walls(bull,0,-bull.speed):#Si no colisionan con una pared que se mueva en la direccion  1 
                    bull.update()
                    self.bullets[id] = bull
                else:#Si colisionan con una pared que se elimine
                    self.elimbull(bull)


            elif bull.dir == 2:
                if not self.collide_with_walls(bull,bull.speed,0):#Si no colisionan con una pared que se mueva en la direccion  2 
                    bull.update()
                    self.bullets[id] = bull
                else:#Si colisionan con una pared que se elimine
                    self.elimbull(bull)


            else:
                if not self.collide_with_walls(bull, 0,bull.speed):#Si no colisionan con una pared que se mueva en la direccion  3 
                    bull.update()
                    self.bullets[id] = bull
                else:#Si colisionan con una pared que se elimine
                    self.elimbull(bull)

            #Si se sale de la pantalla que se elimine 
            if bull.pos[0] < -50: 
                self.elimbull(bull)

            elif bull.pos[0] > SIZE[0] +50: 
                self.elimbull(bull)

            elif bull.pos[1] < 90:
                self.elimbull(bull)

            elif bull.pos[1] > SIZE[1] +50:
                self.elimbull(bull)

        self.lock.release()



    def elimbull(self, bull):#Metodo para eliminar la bala del juego 
        del self.bullets[bull.id]


    def HitPlayer(self):#Funcion para ver que bala ha colisionado con que jugador para restarle la vida y eliminar la bala
        self.lock.acquire()
        for bull in self.bullets.values():
            for player in self.players:

                if collide_player(bull, player):
                    player.lives -= 1
                    self.players[player.numP] = player
                    self.elimbull(bull)
                    self.score[player.numP] = player.lives
                    print(player.lives)

                if player.lives == 0:#Si no le quedan vidas al jugador se termina la partida 
                    self.is_over.value = 1 #Para ver que se ha terminado de forma correcta
                    self.winner.value =  1 - player.numP   #Para ver cual es el ganador
                    
        self.lock.release()


    def shoot(self, numP):#metodo que crea una nueva bala cuando el jugador dispara
        self.lock.acquire()
        owner = numP
        pos = self.players[numP].pos
        dir = self.players[numP].direction

        id = self.id.value 
        self.id.value = id +1

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
        self.lock.release()


    def __str__(self):
        return f"G{self.running.value}>"




def player(nplayer, conn, game):#Funcion que sera el proceso de cada uno de los jugadores
    try:
        print(f"starting player {PLAYER[nplayer]}:{game.get_info(nplayer)}")
        conn.send( (nplayer, game.get_info(nplayer)) )
        while game.is_running():
            if game.is_over == 1:
                
                time.sleep(20) #Tiempo mediante el cual saldra por pantalla el resultado de la partida
                game.is_running.value = 0

            command = ""
            while command != "next": #Recibe los input que mandan los jugadores y segun cual le dice al juego que haga una cosa u otra
                command = conn.recv()
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
                elif command == "Playerhit":
                    game.HitPlayer()

                elif command == "quit":
                    game.stop()

            if nplayer == 1:
                game.move_bullet()#Movemos las balas

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


def main(ip_address): #Inicializa el juego con las conexiones de los jugadores
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
                                            args=(n_player, conn, game))#Nos creamos el proceso de los jugadores
                n_player += 1
                if n_player == 2:#Si ya hay 2 jugadores empezamos el juego

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
