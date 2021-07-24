"""
Hunt The Wumpus
See the wikipedia for info: https://en.wikipedia.org/wiki/Hunt_the_Wumpus

This translation translates: https://github.com/kingsawyer/wumpus/blob/master/wumpus.basic
Not really a translation, but content is based on the basic version.

This version should be portable and work anywhere python runs.
"""

import contextlib
import random

DEBUG_MODE = False
CHEATS_ENABLED = False

class Room(object):
    def __init__(self, paths, number):
        self.paths = paths
        self.visible_paths = []
        self.near_bat = False
        self.near_wumpus = False
        self.near_pit = False
        self.pit = False
        self.bat = False
        self.number = number # This was added waay late so there are some ugly loops lying around still

    def __repr__(self) -> str:
        return "<Room number=" + str(self.number) + "\n" + \
               " paths=" + repr(self.paths) + "\n" + \
               " near_bat=" + str(self.near_bat) + "\n" + \
               " near_wumpus=" + str(self.near_wumpus) + "\n" + \
               " near_pit=" + str(self.near_pit) + "\n" + \
               " pit=" + str(self.pit) + "\n" + \
               " bat=" + str(self.bat) + "\n" + \
               ">"

class Game(object):
    def __init__(self):
        self.set_up_cave()
        self.set_up_placement()
        self.arrows = 5
        self.wumpus_dead = False
        self.player_dead = False

    def set_up_cave(self) -> None:
        cave_data = [2,5,8,1,3,10,2,4,12,3,5,14,1,4,6,5,7,15,6,8,17,1,7,9,8,10,18,2,9,11,10,12,19,3,11,13,12,14,20,4,13,15,6,14,16,15,17,20,7,16,18,9,17,19,11,18,20,13,16,19]
        # Yes the original data was ugly
        self.rooms = []
        if DEBUG_MODE:
            print()
            print("Setting up rooms")
        for i in range(20):
            self.rooms.append(Room([r - 1 for r in cave_data[i*3:i*3+3]], i))
            # Remember to account for zero indexed lists
            if DEBUG_MODE:
                print("Adding room", i, "with paths to", [r - 1 for r in cave_data[i*3:i*3+3]])
        if DEBUG_MODE:
            print()

    def set_up_placement(self) -> None:
        regenerate = True
        regens = 0
        while regenerate:
            regens += 1
            if regens > 100: # Just a safeguard
                print("Position generation took too long. Aborting.")
                raise RuntimeError("Position generation too too many tries. Did someone mess with the code?")
            regenerate = False
            # Comment copied from the BASIC version because it might be useful
            # 0210  REM-1-YOU,2-WUMPUS,3&4-PITS,5&6-BATS
            # Probably means what index means what
            positions = []
            for i in range(6):
                positions.append(self.random_fna())

            # Check for overlaps
            for i in range(6):
                for j in range(i, 6):
                    if i == j:
                        continue # I can probably get rid of this by changing the params to range() but I'm already confused enough
                    if positions[i] == positions[j]:
                        regenerate = True
                        break
                else:
                    continue
                break

        # Actually since lists are zero indexed in python we decrement all indexes in the key (in the BASIC comment) by one
        self.rooms[positions[2]].pit = True # So this is the first pit
        self.rooms[positions[3]].pit = True # This is the second
        self.rooms[positions[4]].bat = True # Bat 1
        self.rooms[positions[5]].bat = True # Bat 2

        # Now I get the neighbors of the rooms with bats and pits and set the near_bat/near_pit
        near_bats, near_pits = [], []
        near_pits += self.rooms[positions[2]].paths
        near_pits += self.rooms[positions[3]].paths
        near_bats += self.rooms[positions[4]].paths
        near_bats += self.rooms[positions[5]].paths

        for pos in near_pits:
            self.rooms[pos].near_pit = True

        for pos in near_bats:
            self.rooms[pos].near_bat = True

        # Don't forget the wumpus
        self.wumpus = positions[1]
        for pos in self.rooms[positions[1]].paths:
            self.rooms[pos].near_wumpus = True
            
        # Don't forget the player either
        self.player_pos = positions[0]

    def random_fna(self) -> int:
        return int(20 * random.random())# + 1 # I would have to -1 since list indexes are 0 based in Python

    def random_fnb(self) -> int:
        return int(3 * random.random())# + 1 # See above

    def random_fnc(self) -> int:
        return int(4 * random.random())# + 1 # See above

    def run(self) -> bool:
        """
        Runs the game. Returns whether or not the player chose to play again.
        """

        print("Hunt The Wumpus")

        end = False
        while not end:
            self.print_location_and_warnings()
            self.move_or_shoot()
            end = self.check_win_lose()
        return self.ask_replay()

    def check_win_lose(self) -> None:
        if self.player_dead:
            print("You lose!")
        elif self.wumpus_dead:
            print("The Wumpus'll getcha next time!!")
            self.print_all_locations()
        else:
            return False
        return True

    def print_all_locations(self) -> None:
        bat_pos = []
        pit_pos = []

        for i in range(20):
            room = self.rooms[i]
            if room.bat:
                bat_pos.append(i)
            if room.pit:
                pit_pos.append(i)

        print()
        print("Locations of everything")
        print("You - Room", self.player_pos + 1)
        print("Wumpus - Room", self.wumpus + 1)
        print("Bats - Rooms", ", ".join([str(r + 1) for r in bat_pos]))
        print("Pits - Rooms", ", ".join([str(p + 1) for p in pit_pos]))

    def print_location_and_warnings(self) -> None:
        """
        Prints information about the current player position.
        """

        print()
        current_room = self.rooms[self.player_pos]
        if current_room.near_bat:
            print("Bats nearby!")
        if current_room.near_pit:
            print("I feel a draft")
        if current_room.near_wumpus:
            print("I smell a Wumpus!")

        print("You are in room", self.player_pos + 1)
        print("Tunnels lead to", ", ".join([str(p + 1) for p in current_room.paths]))
        print("Arrows left:", self.arrows) # This isn't in the BASIC version but its a nice qol feature that shouldn't change gameplay much
        print()
        if DEBUG_MODE:
            print("Debug Information")
            print("Wumpus - Room", self.wumpus + 1)
            for i in range(20):
                room = self.rooms[i]
                features = []
                if room.bat:
                    features.append('bat')
                if room.pit:
                    features.append('pit')
                if len(features) == 0:
                    features.append('empty')

                print("Room", i + 1, "has", ",".join(features), "and connects to", ",".join([str(r + 1) for r in room.paths]))
            print()

    def move_or_shoot(self) -> None:
        while True: # We exit this loop by returning from the function
            choice = input("Shoot or Move? (s/m) ")
            if choice.lower().startswith("s"):
                return self.shoot() # Does python use tail call optimization?
            elif choice.lower().startswith("m"):
                return self.move()
            elif DEBUG_MODE and choice.lower().startswith("d"):
                print(repr(self))
            print("Invalid choice.")

    def move(self) -> None:
        while True:
            next_pos = input("Where to? ")
            try:
                next_pos = int(next_pos)
            except ValueError:
                print("Not a number")
            else:
                if 1 <= next_pos <= 20:
                    next_pos -= 1 # Zero indexed lists
                    # Check if theres a path
                    if next_pos in self.rooms[self.player_pos].paths:
                        self.player_pos = next_pos
                        break
                print("Not possible -")

        self.check_hazards()

    def check_hazards(self) -> None:
        if self.player_pos == self.wumpus:
            print("...Oops! Bumped a Wumpus!")
            self.player_dead = True
            return
        current_room = self.rooms[self.player_pos]
        if current_room.pit:
            print("Yyyiiiieeee . . . Fell in pit")
            self.player_dead = True
            return

        if current_room.bat:
            print("Zap -- Super bat snatch! Elsewhereville for you!")
            self.player_pos = self.random_fna()
            return self.check_hazards() # If python doesn't do tail call optimization this *could* cause a stack overflow

    def shoot(self) -> None:
        while True:
            numrooms = input("No. of rooms (1-5) ")
            try:
                numrooms = int(numrooms)
            except ValueError:
                print("That's not a number")
            else:
                if 1 <= numrooms <= 5:
                    break
                print("An arrow can only travel 1-5 rooms")
        rooms = []
        for i in range(numrooms):
            while True:
                roomnum = input("Room # ")
                try:
                    roomnum = int(roomnum)
                except ValueError:
                    print("That's not a room")
                else:
                    #if roomnum in self.rooms[current_arrow_room].paths:
                    if 1 <= roomnum <= 20:
                        rooms.append(roomnum - 1)
                        break
                    print("Arrows aren't that crooked - try another room")

        # Actually shoot the arrow
        current_arrow_pos = self.player_pos
        for i in range(len(rooms)):
            if rooms[i] in self.rooms[current_arrow_pos].paths:
                current_arrow_pos = rooms[i]
            else:
                # No path, choosing a random direction
                current_arrow_pos = self.rooms[current_arrow_pos].paths[self.random_fnb()]

            if current_arrow_pos == self.wumpus:
                self.wumpus_dead = True
                print("Aha! You got the Wumpus!")
                return
            if current_arrow_pos == self.player_pos:
                self.player_dead = True
                print("Ouch! Arrow got you!")
                return
        print("Missed")

        self.move_wumpus()
        self.arrows -= 1
        if self.arrows <= 0:
            self.player_dead = True
            print("No more arrows")

    def move_wumpus(self) -> None:
        next_pos = self.random_fnc()
        if next_pos == 4:
            return
        self.wumpus = self.rooms[self.wumpus].paths[next_pos]
        if self.wumpus == self.player_pos:
            print("Tsk tsk tsk - Wumpus got you!")
            self.player_dead = True
            return

        for room in self.rooms:
            room.near_wumpus = False

        for rn in self.rooms[self.wumpus].paths:
            self.rooms[rn].near_wumpus = True

    def ask_replay(self) -> None:
        replay = input("Would you like to try again? ")
        return not replay.lower().startswith('n')

    def exit(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<Game" + "\n" + \
               " wumpus=" + str(self.wumpus) + "\n" + \
               " player_pos=" + str(self.player_pos) + "\n" + \
               " arrows=" + str(self.arrows) + "\n" + \
               " wumpus_dead=" + str(self.wumpus_dead) + "\n" + \
               " player_dead=" + str(self.player_dead) + "\n" + \
               " rooms=" + repr(self.rooms) + "\n" + \
               ">"

def show_instructions() -> None:
    ins = input("Would you like to read the instructions? (y/n) ")
    if ins.lower().startswith('n'):
        return
    print("Welcome to \"Hunt The Wumpus\"")
    print("  The Wumpus lives in a cave of 20 rooms. Each room")
    print("has 3 tunnels leading to other rooms. (Look at a")
    print("dodecahedron to see how this works - if you don't know")
    print("what a dodecahedron is, ask someone)")
    print()
    input("Press Enter to continue reading. ")
    print()
    print()
    print("     Hazards:")
    print(" Bottomless Pits - Two rooms have bottomless pits in them")
    print("     If you go there, you fall into the pit (& lose!)")
    print(" Super Bats - Two other rooms have super bats. If you")
    print("     go there, a bat grabs you and takes you to some other")
    print("     room at random. (Which might be troublesome)")
    print()
    input("Press Enter to continue reading. ")
    print()
    print()
    print("     Wumpus:")
    print(" The Wumpus is not bothered by the hazards (He has sucker")
    print(" feet and is too big for a bat to lift). Usually")
    print(" he is asleep. Two things wake him up: your entering")
    print(" his room or your shooting an arrow.")
    print("     If the Wumpus wakes, he moves (P=.75) one room")
    print(" or stays still (P=.25). After that, if he is where you")
    print(" are, he eats you up (& you lose!)")
    print()
    print("     You:")
    print(" Each turn you may move or shoot a crooked arrow")
    print("   Moving: You can go one room (thru one tunnel)")
    print("   Arrows: You have 5 arrows. You lose when you run out.")
    print("   Each arrow can go from 1 to 5 rooms. You aim by telling")
    print("   the computer the room#s you want to arrow to go to.")
    print("   If the arrow can't go that way (ie no tunnel) it moves")
    print("   at random to the next room.")
    print("     If the arrow hits the Wumpus, you win.")
    print("     If the arrow hits you, you lose.")
    print()
    input("Press Enter to continue reading. ")
    print()
    print()
    print("     Warnings:")
    print("      When you are one room away from Wumpus or Hazard,")
    print("     the computer says:")
    print(" Wumpus-  'I smell a Wumpus'")
    print(" Bat   -  'Bats nearby'")
    print(" Pit   -  'I feel a draft'")
    print()
    input("Press Enter to start the game. ")
    print()
    print()

# Only run the game if this file is ran directly

if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        replay = True
        show_instructions()
        while replay:
            game = Game()
            replay = game.run()
        game.exit()
