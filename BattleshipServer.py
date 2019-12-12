#!/usr/bin/python3      # This is server.py file
import socket
import select
import sys

# create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# get local machine name
host = "192.168.1.71"
port = 9999

# bind to the port
server.bind((host, port))

# queue up to 5 requests
server.listen(5)

UP = True

while UP:

   try:
      print("waiting for player 1 to connect...")
      player1, addr1 = server.accept()
      greeting = "Hello PLAYER 1, you are connected!".encode('ascii')
      player1.send(greeting)

      print("waiting for player 2 to connect...")
      player2, addr2 = server.accept()
      greeting = "Hello PLAYER 2, you are connected!".encode('ascii')
      player2.send(greeting)

   except KeyboardInterrupt:
      print("Keyboard Interrupt")
      ### END GAME ###
      UP = False
      try:
         player1.close()
      except:
         pass
      try:
         player2.close()
      except:
         pass
      break

   players = [(player1, addr1),(player2, addr2)]

   GAMEON = True

   print("starting game...")
   while GAMEON:

      for i in range(2):

         shooter = players[i][0]
         enemy = players[(i + 1) % 2][0]

         try:
            # SHOT RECEIVED
            print("waiting for shooter...")
            shot = shooter.recv(1024)
            if not shot:
               ### END GAME ###
               print("Connection lost from shooter!")
               GAMEON = False
               shooter.close()
               enemy.close()
               break

            # SHOT SENT
            print("received:", shot.decode('ascii'), "from shooter")
            print("sending shot to enemy...")
            enemy.send(shot)

            # HIT RECEIVED
            print("waiting for enemy response...")
            hit = enemy.recv(1024)
            print("received:", hit.decode('ascii'), "from enemy")
            if not hit:
               print("Connection lost from enemy!")
               ### END GAME ###
               GAMEON = False
               shooter.close()
               enemy.close()
               break
            
            # HIT SENT
            print("sending hit to shooter...")
            shooter.send(hit)
            
         except KeyboardInterrupt:
            print("Keyboard Interrupt")
            ### END GAME ###
            GAMEON = False
            shooter.close()
            enemy.close()
            break

   """ TEMP STOPPER WHEN TROUBLESHOOTING
   print("Enter STOP to kill server")
   temp = input()
   if temp == "STOP":
      print("Shutting down server...")
      UP = False
   """

### SHUTDOWN SERVER ###
server.close()
print("END")
