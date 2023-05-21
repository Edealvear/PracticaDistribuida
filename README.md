# Practica 3 - Programacion Distribuida (PRPA)

Clon de una pantalla sencilla del juego Battle City, realizado en Python con programacion paralela, apoyandonos en la librería pygame.

Integrantes del equipo:
- Enrique Ernesto de Alvear
- Lucía Roldán Rodríguez
- Laura Cano Gómez

## Archivos e inicialización del juego 
sala.py es la sala en la que se ejecuta el juego, hay que inicializarlo con la IP del
ordenador, y le va mandando los datos de la partida al jugador.

player.py es el archivo del jugador, se tiene que inicializar con la IP con la que 
se ha inicializado la sala, los controles son con las flechas, y se dispara con el espacio. Cada
jugador tiene 5 vidas y cuando alguno llega a 0 se acaba la partida. Se pierde una vida cuando 
una bala disparada por un jugador le da al otro.



