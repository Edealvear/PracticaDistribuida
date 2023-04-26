import os, pygame, time, random
from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys

SIZE = (830, 884)

MinMapa = 87

PlayerSize = 50
BullSize = 30

PLAYER = [0,1]




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
    
    def moveUp(self):
        self.pos[1]-= (15)
        self.dir = 1
        if self.pos[1] < 0:
            self.pos[1]=0
        

    def moveDown(self):
        self.dir = 3
        self.pos[1]+= (15)
        if self.pos[1] > SIZE[1]:
            self.pos[1] = SIZE[1]
    
    def moveLeft(self):
        self.dir = 0
        self.pos[0] -= (15)
        if self.pos[0]<0:
            self.pos[0]=0

    def moveRight(self):
        self.dir = 2
        self.pos[0] += (15 ) 
        if self.pos[0]>SIZE[0]:
            self.pos[0] = SIZE[0]


    def __str__(self):
        return f"Tank"



   
class Game():
    def __init__(self, manager):
        self.players = manager.list( [Player(0), Player(1)] )
        self.walls = manager.list([])

        self.running = Value('i', 1) # 1 running
        self.lock = Lock()
        self.winner = Value('i',0) 

    

    def get_player(self, side):
        return self.players[side]


    def is_running(self):
        return self.running.value == 1

    def stop(self):
        self.running.value = 0

    def moveUp(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveUp()
        self.players[player] = p
        self.lock.release()

    def moveDown(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveDown()
        self.players[player] = p
        self.lock.release()

    def moveRight(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveRight()
        self.players[player] = p
        self.lock.release()

    def moveLeft(self, player):
        self.lock.acquire()
        p = self.players[player]
        p.moveLeft()
        self.players[player] = p
        self.lock.release()

    def get_info(self):
        
        info = {
            'pos_J1': self.players[0].get_pos(),
            'pos_J2': self.players[1].get_pos(),
            'dir': [self.players[0].direction, self.players[1].direction],
            'is_running': self.running.value == 1,
            'WINNER': self.winner.value
        }

        
        return info

    

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

                #elif command == "Playerhit":
                    #game.HitPlayer()
                
                elif command == "quit":
                    game.stop()
            if game.winner.value == 1:
                game.running.value = 0

            
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
