# PracticaDistribuida

tanques_sala.py es la sala en la que se ejecuta el juego, hay que inicializarlo con la IP del
ordenador, y le va mandando los datos de la partida al jugador.

Tanques_player.py es el archivo del jugador, se tiene que inicializar con la IP con la que 
se ha inicializado la sala, los controles son con las flechas, y se dispara con es espacio. Cada
jugador tiene 5 vidas y cuando alguno llega a 0 se acaba la partida.

Los bonus son :
S: es un escudo que aguanta un golpe
V: aumenta la velocidad del tanque
P: aumenta el daño de la bala del tanque





!!!!! OJO !!!!!!
Puede que haya un problema de que algunas de las balas no se manden a un jugador o no se eliminen nunca
revisad eso, creo que tengo una idea de como solucionarlo que es hacer esperar con un wait antes de eliminar 
la información a que ambos jugadores tengan los datos, es decir antes de entrar en las líneas 
336 y 346, y habrá que hacer algo parecido cuando añadamos si lo hacemos los PowerUps