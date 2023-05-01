# Practica 3 - Programacion Distribuida (PRPA)

Consiste en 

- Enrique Ernesto de Albear
- Lucía Roldán
- Laura Cano Gómez


tanques_sala.py es la sala en la que se ejecuta el juego, hay que inicializarlo con la IP del
ordenador, y le va mandando los datos de la partida al jugador.

Tanques_player.py es el archivo del jugador, se tiene que inicializar con la IP con la que 
se ha inicializado la sala, los controles son con las flechas, y se dispara con el espacio. Cada
jugador tiene 5 vidas y cuando alguno llega a 0 se acaba la partida.

# PENDIENTE ARREGLAR:

- Los sprite de los tanques rotan segun el movimiento
- Las balas se generan delante de los tanques segun su direccion

- Las balas se mueven segun la direccion en la que se generan
- Las balas se eliminan al tocar los limites del tablero 

- Gestionar la colision de bala-jugador para fin de partida o descuento de vida

- Crear los muros en las posiciones correctas
- Gestionar la colision de muro-jugador para no permitir el movimiento sobre ellos
- Gestionar la colision de muro-bala para eliminar la bala 



- Extras:
  - Poner los fondos de los sprite transparentes
  - Poner un sprite de animacion cuando las balas se eliminen, como en el tutorial
  - Musica y efectos de sonido al disparar, morir o eliminar balas
  



!!!!! OJO !!!!!!
Puede que haya un problema de que algunas de las balas no se manden a un jugador o no se eliminen nunca
revisad eso, creo que tengo una idea de como solucionarlo que es hacer esperar con un wait antes de eliminar 
la información a que ambos jugadores tengan los datos, es decir antes de entrar en las líneas 
336 y 346, y habrá que hacer algo parecido cuando añadamos si lo hacemos los PowerUps
