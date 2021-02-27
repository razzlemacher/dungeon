import random
import logging
import os, time, sys
from numpy import random as nprandom

class Dungeon:
    """ Represents the dungeon which consists of rooms
        It contains rooms, how rooms are linked to each other and has methods that help navigate the dungeon
    """
    # list of rooms
    init_rooms = {0: ('ENTRY'), 1: ('MURKY', 'Beelzebub'), 2: ('MURKY', 'Gobblezebub'), 3: ('MURKY', 'Devilzebub'), 4: ('MURKY', 'Beetlejuice'), 5: ('EXIT')}

    # rooms linked to other rooms
    room_links = ((0, 1), (1, 2), (2, 3), (2, 4), (3, 4), (4, 5))

    dungeon_map = {}

    def __init__(self, player):
        """ Loads the dungeon map, i.e., creates Room objects and sets them in a list
            Creates and sets the monsters into the rooms, creates and sets treasures as well
            Sets the player location to the ENTRY room (note: player object is not set, just the location)
        """
        self.player_location = -1        # id of room that player is currently in
        self.player = player
        self.room_connections = None    # dictionary showing connection of room to other rooms
        self.rooms = []                 # unordered list of rooms in the dungeon

        # create and populate dungeon with rooms
        for k, v in Dungeon.init_rooms.items():

            # create the room with room id and type of room
            if isinstance(v, str):
                room = Room(k, v)       # ENTRY and EXIT rooms
            
                if  room.room_type == 'ENTRY':
                    pass
            else:
                room = Room(k, v[0])    # MURKY rooms are in a tuple with monster names

                # create monster or treasure
                if room.room_type == 'MONSTER':
                    room.monster = Monster(v[1])     # create monster and set its name
                    room.has_monster = True
                elif room.room_type == 'TREASURE':
                    room.treasure = Treasure()
                    room.has_treasure = True

            self.rooms.append(room)

        # for each room, add room to dictionary if not already there
        for kr in self.rooms:
            connected_rooms = []

            # get connected rooms for room from the dictionary
            if kr.id in Dungeon.dungeon_map.keys():
                connected_rooms = Dungeon.dungeon_map[kr.id]

            # get connected room id from tuple            
            for link in Dungeon.room_links:
                if kr.id != link[0]:
                    continue

                # get room object from room id link[1]
                for rm_obj in self.rooms:

                    # if room obj is found, and room is not itself (i.e. key and value must be different)
                    if rm_obj.id == link[1] and kr.id != link[1]:
                        connected_rooms.append(rm_obj)

            # add connections as list
            Dungeon.dungeon_map.update({kr.id:connected_rooms})

    def get_current_room(self):

        # user has not entered the dungeon
        if self.player_location == -1:
            return None
        return self.find_room(self.player_location)

    def find_room(self, room):
        """ Finds and returns the room with the room (accepts either str or room object)
            Returns None if no room found
        """
        for rm in self.rooms:
            if isinstance(room, int):
                if rm.id == room:
                    return rm
            elif isinstance(room, str):
                if rm.id == int(room):
                    return rm
            else:
                if rm.id == room.id:
                    return rm

        return None

    @property
    def monster(self):
        """ Gets the monster from the room that the player is in
            Returns None if there is no monster in the room
        """
        # find the room the player is in
        for room in self.rooms:
            if room.id == self.player_location:
                if room.has_monster:
                    return room.monster
        return None

    def next_rooms(self, current_room):
        """ Accepts room object or room id to return rooms it is connected to 
            Returns a list of rooms that the current room connects to
        """
        if isinstance(current_room, int):
            return Dungeon.dungeon_map[current_room]

        return Dungeon.dungeon_map[current_room.id]

class Room:
    """ Represents one room. A room can have either monsters or treasure in it.
        Whenever a room is created, there is a 75% chance that it will contain a monsther
        and 25% treasure in it. It appropriately sets the room type to be either
        "MONSTER" or "TREASURE"
    """
    def __init__(self, id, room_type):
        """ creates one room using the room type parameter
            If room type is MURKY, randomly sets room to room type MONSTER or TREASURE
        """
        self.id = id
        self.room_type = room_type      # room can be an entry, exit or murky (with monster or treasure)
        self.monster = None             # reference to the monster
        self.treasure = None            # reference to the treasure
        self.room_status = None         # if room has been visited or needs to be initialized
        self.description = ''           # colorful description of the room
        self.entry_door_desc = ''       # colorful description of the door 
        self.has_monster = False
        self.has_treasure = False

        if self.room_type == 'MURKY':
            # will this room have a monster or treasure? Monsters are more likely
            i = nprandom.choice([0, 1], p=[0.25, 0.75], size=(1))
            #i = random.randint(0, 1)
            if i == 1:
                self.room_type = 'MONSTER'
            else:
                self.room_type = 'TREASURE'

class Treasure:
    """ Simple object that has random agility and health rewards for the player
    """
    def __init__(self):
        self.agility_reward = random.randint(2, 8)
        self.health_reward = random.randint(2, 8)
        self.empty = False

class Creature:
    """ It represents any living thing in the dungeon. A creature can be a Monster or a Player.
        It contains the attributes common to any creature: name, health, agility and if it is alive.
    """
    def __init__(self, name):
        self.name = name
        self.agility = random.randint(2, 10)
        self.health = random.randint(2, 10)
        self.is_alive = True

    def __str__(self):
        return f'Name:{self.name}, Type:{type(self)}, Alive:{self.is_alive}, Health:{self.health}, Agility:{self.agility}'

class Player(Creature):
    """ Player class that contains the player's location in the dungeon and stats on the player
    """
    def __init__(self, name):
        super().__init__(name)
        self.runs_count = 0
        self.fights_count = 0

    def __str__(self):
        s = super().__str__()
        s += f', Runs count:{self.runs_count}, Fight count:{self.fights_count}'
        return s

class Monster(Creature):
    """ Monster class that contains the monster's location in the dungeon.
    """
    def __init__(self, name):
        super().__init__(name)
        self.current_room = 1

class BattleManager:
    """ Controls all the fights that take place in the dungeon
    """
    def run(self, player, monster):
        """ Executes the scenario where player runs away from the monster
            If player is faster than the monster, it is an easy escape
            If monster is same speed or faster than player, then player takes damage
            Returns 0 if player escapes unharmed, returns 1 if player was harmed
        """
        # set the running odds
        total_a = player.agility + monster.agility
        player_odds = player.agility/total_a
        monster_odds = monster.agility/total_a

        # run!! (0 means player won, 1 means monster won)
        i = nprandom.choice([0, 1], p=[player_odds, monster_odds], size=(1))
        player.runs_count += 1

        # player won the race, no change to health or agility
        if i[0] == 1:
            return GameController.PLAYER_RAN_UNHURT
        # if monster won, player loses agility and health but escapes
        else:
            player.health -= 2
            player.agility -= 2

            if player.agility < 0:
                player.agility = 0

            if player.health <= 0:
                player.health = 0
                player.is_alive = False
                return GameController.PLAYER_DIED

        return GameController.PLAYER_RAN_HURT

    def reward_player(self, player, dungeon):
        """ Player's health and agility are incremented by the values in the reward in the room
        """
        # find the current room and get the reward stats and add to player stats
        room = dungeon.get_current_room()
        hrw = room.treasure.health_reward
        arw = room.treasure.agility_reward
        player.health += hrw
        player.agility += arw
        if player.health > 10:
            player.health = 10
        if player.agility > 10:
            player.agility = 10

        return GameController.PICK_UP_REWARD        

    def fight(self, player, monster):
        """ executes the battle and probabilities between player and monster
            The loser loses 2 health points. If all health is lost, creature is marked dead with 0 health
            Also increments the players fight count
            Returns int 0 if player won, or int 1 if monster won
        """
        # set the fighting odds
        total_h = player.health + monster.health
        player_odds = player.health/total_h
        monster_odds = monster.health/total_h

        # fight!! (0 means player won, 1 means monster won)
        i = nprandom.choice([0, 1], p=[player_odds, monster_odds], size=(1))
        player.fights_count += 1

        # if monster won, player loses health
        if i[0] == GameController.MONSTER_WON:
            if player.health > 2:
                player.health -= 2
            else:
                player.health = 0
                player.is_alive = False
            return GameController.MONSTER_WON
        # player won, monster loses health
        else:
            if monster.health > 2:
                monster.health -= 2
            else:
                monster.health = 0
                monster.is_alive = False
            return GameController.PLAYER_WON

class Display:
    """ Renders the game (dungeon, stats, etc.) on the screen.
        There is only one display in the game hence all methods are static.
    """

    @staticmethod
    def help():
        """ Prints help in how to play the game
        """
        print('-----------------------------------------------------------------------')
        print('------------------------------HELP-------------------------------------')
        print('-----------------------------------------------------------------------')
        print('To START game: python dungeon.py                                     ')
        print('-----------------------------------------------------------------------')
        print('To EXIT the game at any time type "bye" without the quotes             ')
        print('-----------------------------------------------------------------------')
        print('Follow the instructions provided in the game and type commands such as:')
        print('      reward -- to pick up a reward')
        print('      fight  -- to fight a monster')
        print('      run    -- to run away from a monster')
        print('-----------------------------------------------------------------------')
        print('-----------------------------------------------------------------------')

    @staticmethod
    def show_rooms(rooms):
        """ Displays the room(s)
            It can accept either a list of rooms or a single room as parameters
            Does not return anything, it prints room details on the screen
        """
        if isinstance(rooms, Room):
            r = rooms
            print(f'Room Id:{r.id}, Type:{r.room_type}, Has monster:{r.has_monster}, Has treasure:{r.has_treasure}')
        elif  isinstance(rooms, list):
            for r in rooms:
                if isinstance(r, Room):
                    print(f'Room Id:{r.id}, Type:{r.room_type}, Has monster:{r.has_monster}, Has treasure:{r.has_treasure}')
                else:
                    print(f'Error: parameter expected was Room or list of rooms, received {type(r)}')        
        else:
            print(f'Error: parameter expected was Room or list of rooms, received {type(rooms)}')        

    @staticmethod
    def show_moves(next_moves):

        if len(next_moves) > 1:
            if next_moves[0] == 'move':
                print(f'You are ready to move to the next room. Pick your room number:')
                for m in range(1, len(next_moves)):
                    print(f'\t{next_moves[m]}')
                return

        if next_moves[0] == 'escape':
            print(f'You have reached the exit! Just open the door:')
            print(f'\t{next_moves[0]}')
            return

        print(f'What will you do:')
        for o in next_moves:
            print(f'\t{o}')

    stat_to_file = {1:'1.txt', 2:'2.txt', 3:'3.txt', 4:'4.txt',5:'5.txt',6:'6.txt',7:'7.txt',8:'8.txt',9:'9.txt',10:'10.txt'}

    @staticmethod
    def show_stats(player=None, monster=None):
        """ Displays the statistics in big graphics using the unicode files that contain numbers and screen prints
        """
        # print stat header
        Display.printfiles("bigspace.txt", "health.txt","agility.txt", repeats=1)

        if player != None:
            health_file = str(player.health) + '.txt'
            agility_file = str(player.agility) + '.txt'
            Display.printfiles("dave.txt", health_file, agility_file, repeats=1)

        if monster != None:
            health_file = str(monster.health) + '.txt'
            agility_file = str(monster.agility) + '.txt'
            Display.printfiles("monster.txt", health_file, agility_file, repeats=1)

    @staticmethod
    def printfiles(file1, file2, file3, delay = 1, repeats = 1):
        """ Takes 3 files as inputs, and appends the lines of each file to the next file
        """
        fh1 = open(file1, "r", encoding='utf8')
        fh2 = open(file2, "r", encoding='utf8')
        fh3 = open(file3, "r", encoding='utf8')

        all_lines = ""
        while True:
            line1 = fh1.readline()
            line2 = fh2.readline()
            line3 = fh3.readline()
            if not line1:
                break

            line1 = line1.replace('\n', ' ')
            line2 = line2.replace('\n', ' ')

            all_lines += line1
            all_lines += line2
            all_lines += line3

        fh1.close()
        fh2.close()
        fh3.close()
        print(all_lines)

    @staticmethod
    def show_final_screen():
        """ Shows the goodbye screen of the game """
        escape_file = ["escape.txt"]
        Display.ascii_screen(escape_file)


    @staticmethod
    def show_result(result, dungeon):
        """ Shows the outcome of the users action on the screen
        """
        rm = dungeon.get_current_room()
        p = dungeon.player
        if result == GameController.PLAYER_WON:
            m = rm.monster
            if m.is_alive == False:
                print("Player KILLS Monster")
            else:
                print("Player inflicts damage on Monster")
                Display.show_stats(player=p, monster=m)
        elif result == GameController.MONSTER_WON:
            if p.is_alive == False:
                print("Monster KILLS Player")
            else:
                print("Monster inflicts damage on Player")
                m = rm.monster
                Display.show_stats(player=p, monster=m)
        elif result == GameController.PICK_UP_REWARD:
            t = rm.treasure
            print(f'Treasure contained health:{t.health_reward} and agility:{t.agility_reward}')
            #print(f'Player stats updated to health:{p.health} and agility:{p.agility} updated')
            Display.show_stats(player=p)
        elif result == GameController.PLAYER_RAN_UNHURT:
            print("Player ran away with no damage. Lucky!")
            # if the new room has a monster then show the monster and the stats
            if rm.has_monster == True:
                monsterfiles = ['monster01.txt']
                m = rm.monster
                Display.ascii_screen(monsterfiles)
                Display.show_stats(player=p, monster=m)
            elif rm.has_treasure == True:
                treasurefiles = ['treasure01.txt']
                Display.ascii_screen(treasurefiles)
            else:
                Display.show_stats(player=p)
        elif result == GameController.PLAYER_RAN_HURT:
            print("Player ran away with some damage")
            Display.show_stats(player=p)
            # if the room has a monster then show the monster and the stats
            if rm.has_monster == True:
                monsterfiles = ['monster01.txt']
                m = rm.monster
                Display.ascii_screen(monsterfiles)
                Display.show_stats(player=p, monster=m)
            elif rm.has_treasure == True:
                treasurefiles = ['treasure01.txt']
                Display.ascii_screen(treasurefiles)
        elif result == GameController.PLAYER_DIED:
            print("Player killed by monster while trying to run. Welcome grim reaper.")
        elif result == GameController.ENTERED_ROOM:
            # if the room has a monster then show the monster and the stats
            if rm.has_monster == True:
                monsterfiles = ['monster01.txt']
                m = rm.monster
                Display.ascii_screen(monsterfiles)
                Display.show_stats(player=p, monster=m)
            elif rm.has_treasure == True:
                treasurefiles = ['treasure01.txt']
                Display.ascii_screen(treasurefiles)

    @staticmethod
    def fight_result(dungeon, winner):
        p = dungeon.player
        m = dungeon.monster


        # if player is the winner
        if winner == 0:
            if m.is_alive == False:
                print("Player KILLS Monster")
            else:
                print("Player inflicts damage on Monster")
        else:
            if p.is_alive == False:
                print("Monster KILLS Player")
            else:
                print("Monster inflicts damage on Player")

    @staticmethod
    def ascii_screen(filenames, delay = 1, repeats = 1):
        frames = []
        for name in filenames:
            with open(name, 'r', encoding='utf8') as f:
                frames.append(f.readlines())

        for i in range(0,repeats):
            for frame in frames:
                print("".join(frame))
                time.sleep(delay)
                #os.system('cls')       # clear screen

    @staticmethod
    def welcome(p):
        print(f'Welcome {p.name}!')
        print(f'You are about to enter a DUNGEON in which reside RANDOMLY generated MONSTERS and TREASURES')
        print('')
        print(f'Your vital statistics bestowed upon you by birth are:')
        print('--------------------------------------------------------')
        ddata = '{name:<20s} {health:<10s} {agility:<10s}'.format(name='NAME', health='HEALTH', agility='AGILITY')
        print(ddata)
        ddata = '{name:<20s} {health:<10d} {agility:<10d}'.format(name=p.name, health=p.health, agility=p.agility)
        print(ddata)
        print('--------------------------------------------------------')
        print('')
        print(f'The MONSTERS you fight will have their own health and agility')
        print(f'BUT ... sometimes ... if you are lucky .... you will be rewarded with TREASURE that will replenish your vitals')
        print(f'You can either fight or run ... but you MUST get out of this dungeon ... or DIE a watery death')
        print('')
        print('')

class GameController:
    """ Controls the flow of the game. It uses objects (such as the dungeon and the player) to determine
        the next step in the game.
    """
    # These are outcomes of all the things the player can do and are used through the file to manage the game
    PLAYER_WON = 0
    MONSTER_WON = 1
    ENTER_DUNGEON = 2
    PICK_UP_REWARD = 3
    ENTERED_ROOM = 4
    PLAYER_RAN_HURT = 5
    PLAYER_RAN_UNHURT = 6
    PLAYER_DIED = 7

    def __init__(self, dg):
        self.dungeon = dg
        self.bm = BattleManager()

    def is_game_running(self):
        return self.dungeon.player.is_alive

    def user_escaped(self, user_input):
        if user_input == 'escape':
            croom = self.dungeon.get_current_room()
            if croom.room_type == 'EXIT':
                return True
        
        return False

    def update_game_state(self, result, user_input):
        """ Called after user has input the next move
            If fight was fought it will update the dungeon and possibly end the game if player died
            If player made a choice to move to a room, it will update locations
        """
        if result == GameController.ENTER_DUNGEON:
            # user has entered the dungeon, update to the first room
            self.dungeon.player_location = 0
            return

        elif result == GameController.PICK_UP_REWARD:
            # remove the treasure and mark room as empty
            room = self.dungeon.get_current_room()
            room.has_treasure = False
            room.treasure.empty =  True
            room.treasure.health_reward = 0
            room.treasure.agility_reward = 0
            return 
        elif result == GameController.ENTERED_ROOM:
            # get the room using user input
            room = self.dungeon.find_room(user_input)
            self.dungeon.player_location = room.id
            return
        elif result == GameController.PLAYER_WON:
            # if player won the fight and monster is dead, then move player to the next room
            room = self.dungeon.get_current_room()
            
            if room.monster.is_alive == False:
                room.has_monster = False
                room.monster.agility = 0
                room.monster.health = 0
            return
        elif (result == GameController.PLAYER_RAN_HURT
            or result == GameController.PLAYER_RAN_UNHURT):
            # ran away, no action needed
            return
        elif result == GameController.PLAYER_DIED:
            # no action needed
            return


    def execute_move(self, user_input):
        """
            Returns: 0 if player wins fight, 1 if monster wins fight, GameController.ENTER_DUNGEON if enter dungeon
        """
        user_input = user_input.lower()

        if user_input == 'fight':
            # returns GameController.MONSTER_WON if player wins fight
            return self.bm.fight(self.dungeon.player, self.dungeon.monster)
        elif user_input == 'run':
            val = self.bm.run(self.dungeon.player, self.dungeon.monster)
            if val == GameController.PLAYER_DIED:
                return val

            # user escaped and entered a room
            croom = self.dungeon.get_current_room()
            next_rooms = self.dungeon.next_rooms(croom)
            room_id = next_rooms[0].id
            self.update_game_state(GameController.ENTERED_ROOM, room_id)
            return val

        elif user_input == 'enter':
            return GameController.ENTER_DUNGEON
        elif user_input == 'reward':
            return self.bm.reward_player(self.dungeon.player, self.dungeon)
        elif user_input == 'escape':
            # nothing to do
            return None
        else:
            # user chose a room (id) to enter
            room = self.dungeon.find_room(user_input)
            if room != None:
                # update the current location of the player
                self.dungeon.player_location = room.id
                return GameController.ENTERED_ROOM
            return None

    def next_move_options(self):
        """ At any point the player can either pick up the reward, fight, run or move to the next room
            Returns a list with lists of options that the player must choose between. Valid options are:
            If a living monster is in the room then:
                Fight
                Run
            If treasure is in the room:
                Reward (i.e. pick up the treasure)
            If there is no monster or treasure in the room then:
                Move to rooms (can be one or multiple rooms ahead)
            List with applicable options is returned.
            [ [fight], [run], [reward], [enter], [move, room1 id, room2 id] ] 
        """
        room = self.dungeon.get_current_room()
        connections = None
        player_options = []
        # user has not entered the dungeon
        if room == None:
            # user needs to enter dungeon
            player_options = ["enter"]
            return player_options

        # if room has monster and monster is alive, option is fight or run
        elif room.room_type == 'MONSTER':
            if room.has_monster == True:
                # either fight or run
                player_options = ["fight", "run"]
                return player_options
            # if room has monster and monster is dead, select which room is next
            elif room.has_monster == False:
                player_options = ["move"]
                connections = self.dungeon.next_rooms(room)
                for r in connections:
                    player_options.append(r.id)
                return player_options
        # if room has treasure, enjoy the reward
        elif room.room_type == 'TREASURE':

            # if treasure chest is empty (already been used)
            if room.has_treasure == False:
                player_options = ["move"]
                connections = self.dungeon.next_rooms(room)
                for r in connections:
                    player_options.append(r.id)
                return player_options

            # pick up the reward
            player_options = ["reward"]
            return player_options
        elif room.room_type == 'EXIT':
            # say goodbye and you are a free person
            player_options = ["escape"]
            return player_options
        elif room.room_type == 'ENTRY':
            # you have only one choice, enter the scary dungeon
            connections = self.dungeon.next_rooms(room)
            player_options = ["move"]
            for r in connections:
                player_options.append(r.id)
            return player_options
        else:
            # this option should never be reached, print warning
            print(f'Error: unexpected room type found, {room.room_type}')
            pass

    def validate_input(self, valid_moves, x):
        """ Compares user input """
        # take the input
        x = input("Type your move: ")
        if x == 'bye':
            return x

        if valid_moves[0] == 'move':
            valid_moves = valid_moves[1:]
        if x in valid_moves:
            return x
        elif x.isdigit():
            y = int(x)
            if y in valid_moves:
                return x

        return 'badIO'


# if user asked for help, then print the game logo and help screen and exit
if len(sys.argv) > 1:
    if sys.argv[1] == 'help':
        splashfiles = ["splash01.txt"]
        Display.ascii_screen(splashfiles, delay=0, repeats=1)
        Display.help()
        exit()
    else:
        print(f'Invalid argument {sys.argv[1]}')


# splash screen for game
splashfiles = ["splash00.txt"]
Display.ascii_screen(splashfiles, delay=2, repeats=1)

# initiate the main game objects
p = Player('Dangerous Dave')
dg = Dungeon(p)
gc = GameController(dg)

Display.welcome(p)

# game loop
while True:
    # step 1: what are the valid options to show the player?
    next_moves = gc.next_move_options()

    # show the options
    Display.show_moves(next_moves)

    x = 'badIO'
    i = 0
    # take the input
    while x == 'badIO':
        if i > 0:
            print('Please provide a valid option')
        x = gc.validate_input(next_moves, x)
        i += 1

    if x == 'bye':
        break

    # process the input
    result = gc.execute_move(x)

    # show the outcome of the fight or running away
    Display.show_result(result, dg)

    # update the state
    gc.update_game_state(result, x)

    # check if game ended
    if gc.is_game_running() == False:
        break

    if gc.user_escaped(x) == True:
        Display.show_final_screen()
        break
