#!/usr/bin/python3
import socket
import select
import sys

class PlayerError(Exception):
   pass

# create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# get local machine name
#host = "192.168.86.38"
host = "SAL-1908-KJ"
port = 9999

# bind to the port
server.bind((host, port))

# queue up to 5 requests
server.listen(5)

UP = True

while UP:

   GAMEON = False

   print("Starting new session...")
   print("Waiting for 2 players to join")

   players = list()

   # Wait until 2 players have joined #
   while (len(players) != 2):

      try:
         print(str(len(players)), "Players connected...")
         print("Waiting for a player connection...")
         # Accept connection and add to list
         player, addr = server.accept()
         print("Player connected...")
         greeting = "You are connected!".encode('ascii')
         print("Sending ack to player...")
         player.send(greeting)
         print("Adding player to roster...")
         players.append((player, addr))
      except KeyboardInterrupt:
         print("[Keyboard Interrupt] Server was halted")
         ### KILL SERVER ###
         UP = False
         try:
            for p in players:
               p[0].close()
         except:
            pass
         break

      # Check to see if all players are still present
      print("Checking to see if all players are still connected")
      for p in players:
         try:
            print("Unblocking socket")
            p[0].setblocking(0)
            print("Testing connection")
            test = p[0].recv(1024)
            print("Blocking socket")
            p[0].setblocking(1)
         except BlockingIOError:
            p[0].setblocking(1)
         except:
            print("Player connection lost, removing from roster...")
            p[0].close()
            players.remove(p)
            continue

   if (len(players) == 2):
      # Assign player positions and start game
      print("2 Players connected, sending player assignments")
      for n,p in enumerate(players):
         assignment = "PLAYER " + str(n+1)
         print("Sending assignment to", assignment)
         assignment = assignment.encode('ascii')
         p[0].send(assignment)

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
               raise PlayerError("Connection lost from player")

            # SHOT SENT
            print("received:", shot.decode('ascii'), "from shooter")
            print("sending shot to enemy...")
            enemy.send(shot)

            # HIT RECEIVED
            print("waiting for enemy response...")
            hit = enemy.recv(1024)
            if not hit:
               raise PlayerError("Connection lost from player")
            print("received:", hit.decode('ascii'), "from enemy")
            
            # HIT SENT
            print("sending hit to shooter...")
            shooter.send(hit)
            
         except KeyboardInterrupt:
            print("[Keyboard Interrupt] Server was halted")
            ### END GAME ###
            GAMEON = False
            try:
               shooter.close()
               enemy.close()
            except:
               pass
            break
         except ConnectionResetError:
            print("[Reset Connection Error] Connection lost from player!")
            ### END GAME ###
            GAMEON = False
            try:
               shooter.close()
               enemy.close()
            except:
               pass
            break
         except PlayerError:
            print("[Player Error] Connection lost from player!")
            ### END GAME ###
            GAMEON = False
            try:
               shooter.close()
               enemy.close()
            except:
               pass
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
