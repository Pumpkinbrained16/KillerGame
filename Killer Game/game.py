import random
import time
from collections import Counter

from roles import Player, roles, ToughCivilian

uncalled_roles = roles


class Game:
    def __init__(self, gameId: int):
        self.gameId = gameId
        self.initialise()

    def initialise(self):
        random.shuffle(uncalled_roles)
        for i, role in enumerate(uncalled_roles):
            if type(role) != type:
                uncalled_roles[i] = type(role)
        
        self.roles = uncalled_roles
        self.alive_players = []
        self.dead_players = []
        self.died_last_night = []
        self.exited_playernos = []
        self.next_playerno = 0

        self.round = 1
        self.time = "Night"
        self._said = [] # [[Player(), what_is_said], [Player(), what_is_said]...]
        self.votes = dict() # {voting Player(): voted Player()}

        self.speaking_turn = 0 # index 0
        self.night_turn = 0 # if the player has alr died, then wait a fabricated amount of time
        self.speaking_sequence = []

        self.tough_civ_killed_once = False
        self.romeo_check = None
        self.juliet_check = None
        
        self.killed_person = None
        self.just_killed = False
        self.just_killed_times = 0

        self.poisoned_person = None
        self.last_guarded = None

        self.killed = []
        self.voted_out = []
        self.tookdown = []

        self.round_turnover_times = 0

        self.trigger_second_voting = False

        self.speaking = None # this is for voting, not for daytime

        self.can_start = False

    def ready(self) -> bool: # must be called as soon as all 10 players join
        if len(self.alive_players) == 10 and not self.exited_playernos:
            self.can_start = True

        return self.can_start

    def reset_just_killed(self):
        self.just_killed_times += 1

        if self.just_killed_times == 3:
            self.just_killed = False
            self.just_killed_times = 0

    def calc_next_playerno(self):
        if self.exited_playernos:
            self.next_playerno = self.exited_playernos.pop(0)
        else: # no one has exited, or players who have exited have been filled, so continue on
            self.next_playerno = len(self.alive_players) + 1

    def assign_role(self) -> Player: # if playerno is 1, access index 0
        self.calc_next_playerno()
        self.roles[self.next_playerno - 1] = self.roles[self.next_playerno - 1](self.next_playerno)
        self.alive_players.append(self.roles[self.next_playerno - 1])

        return self.roles[self.next_playerno - 1]


    def unassign_role(self, playerno): # if someone leaves, change object back into uncalled state, append to exited_playernos, but do not pop from alive players
        self.roles[playerno - 1] = type(self.roles[playerno - 1])
        # self.alive_players.pop(playerno - 1)
        self.exited_playernos.append(playerno)

    def remove_game(self) -> bool:
        return True if not self.alive_players else False

    def _say(self, player: Player, what_is_said: str):
        if self.time == "Day":
            self._said.append([player, what_is_said])

    def vote(self, your_player: Player, voted_player: Player):
        self.votes[your_player] = voted_player

    def calc_votes(self) -> list[Player]:
        all_votes_player = Counter(self.votes.values()) 

        try:
            voted_out = all_votes_player.most_common(1)[0]
            reply = [voted_out[0]]

            for voted, num in all_votes_player.items():
                if num == voted_out[1] and voted.playerno != voted_out[0].playerno:
                    reply.append(voted)
            
        except IndexError:
            reply = []
        
        return reply
        
    def who_died(self) -> list: #only works the first time ran, call when displaying who died, after that cannot use
        dead = []
        if not self.died_last_night:
            for i, player in enumerate(self.roles):
                if player.alive and isinstance(player, ToughCivilian) and self.tough_civ_killed_once:
                    self.roles[i].alive = False
                    player.alive = False

                if not self.roles[i].alive:
                    if player.playerno not in [_player.playerno for _player in self.dead_players]:
                        if isinstance(player, ToughCivilian) and not self.tough_civ_killed_once and player.playerno == self.killed_person.playerno:
                            time.sleep(0.5) # this is to make everyone wait here so that self.tough_civ_killed_once wont be True
                            self.roles[i].alive = True
                            self.tough_civ_killed_once = True
                        else:
                            dead.append(self.roles[i])
                            self.dead_players.append(self.roles[i])
                            self.alive_players.remove(self.roles[i])
                            self.killed.append(self.roles[i])

                            print(self.dead_players)
                            print("KILLLEEEEEDDDDD", player.playerno)

            self.died_last_night = dead
            return dead # if peaceful night, then dead = []
        
        else:
            return None

    def _speaking_sequence(self) -> list[Player]:
        if self.died_last_night:
            idx = self.died_last_night[-1].playerno - 1
        else:
            idx = 0
        
        correct_order = self.roles[idx:] + self.roles[:idx]
        correct_order = [p for p in correct_order if p.alive == True]
        
        if self.round % 2 == 1:
            return self.died_last_night + correct_order
        else:
            return correct_order

    def speaking_turnover(self):
        if self.speaking_turn == len(self.speaking_sequence) - 1:
            self.speaking_turn = 0 # voting after
            self.time = "Voting"
            print("time is Voting")
        else:
            self.speaking_turn += 1

    def night_sequence(self):
        if self.round != 1:
            return ["Guard", "Killers", "Psychic Killer", "Doctor", "Hero Detective"]
        else:
            return ["Romeo Civilian", "Juliet Civilian"] + ["Guard", "Killers", "Psychic Killer", "Doctor", "Hero Detective"]
    
    def night_turnover(self):
        if self.night_turn == len(self.night_sequence()) - 1:
            self.night_turn = 0 # Daytime after
            self.time = "Day"
        else:
            print("night turn incremented")
            self.night_turn += 1
    
    def round_turnover(self): # after voting
        self.round_turnover_times += 1

        if self.round_turnover_times == 10:
            print("round turnover reached 10")
            self.round += 1
            print(self.round)
            self.time = "Night"
            self.killed_person = None
            self.died_last_night = []
            self.poisoned_person = None
            self.round_turnover_times = 0
            for player in self.roles:
                if player.guarded == True:
                    self.roles[player.playerno - 1].guarded = False
    
    def instant_round_turnover(self):
        self.round += 1
        print(self.round)
        self.time = "Night"
        self.died_last_night = []
        self.killed_person = None
        self.poisoned_person = None
        for player in self.roles:
            if player.guarded == True:
                self.roles[player.playerno - 1].guarded = False

    def game_ends(self) -> bool:
        if self.winners():
            return True
        else:
            return False

    def find_role(self, playerno) -> Player:
        for role in self.roles:
            if role.playerno == playerno:
                return role #Player()

    def romeo_juliet_check(self, player: Player):
        if not self.romeo_check:
            self.romeo_check = player
        else:
            self.juliet_check = player
    
    def checked_person(self) -> Player | str | None: # when juliet passes turn, romeo client should check if there's a match
        if self.romeo_check and self.juliet_check:
            if self.romeo_check == self.juliet_check:
                return self.romeo_check # Player
            else:
                return "no match"

    def winners(self):
        killers_present = False
        civ_present = False
        super_present = False
        for player in self.alive_players:
            if player.identity[2] == "Bad":
                killers_present = True 
            elif player.identity[1] == "Super":
                super_present = True
            elif player.identity[1] == "Civilian":
                civ_present = True
        
        if not killers_present:
            return "good guys"
        elif not civ_present:
            return "killers"
        elif not super_present:
            return "killers"
        else:
            return None
    
    def reset(self):
        random.shuffle(roles)
        self.__init__(self.gameId)


"""game = Game(1)
Player1 = game.assign_role(1)
Player2 = game.assign_role(2)
Player3 = game.assign_role(3)
Player4 = game.assign_role(4)
Player5 = game.assign_role(5)
Player6 = game.assign_role(6)
Player7 = game.assign_role(7)
Player8 = game.assign_role(8)
Player9 = game.assign_role(9)
Player10 = game.assign_role(10)
players = [Player1, Player2, Player3, Player4, Player5, Player6, Player7, Player8, Player9, Player10]
for player in players:
    print(player)

print("------------")

for player in game.roles:
    print(player)

print("------------")

# Romeo
print(game.night_sequence()[game.night_turn])
game.romeo_juliet_check(Player10)
game.night_turnover()

# Juliet
print(game.night_sequence()[game.night_turn])
game.romeo_juliet_check(Player10)
print(game.checked_person()) # show match to both
game.night_turnover()

# Guard
print(game.night_sequence()[game.night_turn])
Player6.guard(Player2)
game.night_turnover()

# Killers
print(game.night_sequence()[game.night_turn])
Player2.killed()
game.night_turnover()

# Psychic Killer
print(game.night_sequence()[game.night_turn])
print(Player9.check(Player6))
game.night_turnover()

# Doctor
print(game.night_sequence()[game.night_turn])
Player4.heal(Player2) # die of overdose
game.night_turnover()

# Hero Detective
print(game.night_sequence()[game.night_turn])
print(Player5.check(Player10))
game.night_turnover()

print("---------")
print(game.who_died())
for player in game.roles:
    print(player.alive)

print(game.speaking_sequence())

print(game.time)"""

