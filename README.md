# Practica 3 - Programacion Distribuida (PRPA)

Clon de una pantalla sencilla del mítico juego Battle City, realizado en Python con programacion paralela, apoyandonos en la librería pygame.

Integrantes del equipo:
- Enrique Ernesto de Albear
- Lucía Roldán
- Laura Cano Gómez

## Archivos e inicialización del juego 
tanques_sala.py es la sala en la que se ejecuta el juego, hay que inicializarlo con la IP del
ordenador, y le va mandando los datos de la partida al jugador.

Tanques_player.py es el archivo del jugador, se tiene que inicializar con la IP con la que 
se ha inicializado la sala, los controles son con las flechas, y se dispara con el espacio. Cada
jugador tiene 5 vidas y cuando alguno llega a 0 se acaba la partida.

# PENDIENTE ARREGLAR:


- Las balas se generan delante de los tanques segun su direccion


- Las balas se eliminan al tocar los limites del tablero 

- Gestionar la colision de bala-jugador para fin de partida o descuento de vida

- Crear los muros en las posiciones correctas
- Gestionar la colision de muro-jugador para no permitir el movimiento sobre ellos
- Gestionar la colision de muro-bala para eliminar la bala 



- Extras:
  - Poner los fondos de los sprite transparentes
  - Poner un sprite de animacion cuando las balas se eliminen, como en el tutorial
  - Musica y efectos de sonido al disparar, morir o eliminar balas
  
