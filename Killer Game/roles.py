class Player:
    def killed(self): 
        #For SuperKiller's explosion (during daytime), .alive is set to False, someone is immediately taken down
        if not self.guarded:
            self.alive = False

    def revive(self):
        if self.alive == False:
            self.alive = True
        else:
            self.alive = False # die of overdose


class ToughCivilian(Player):
    def __init__(self, playerno):
        self.playerno = playerno
        self.username = ""
        self.alive = True
        self.guarded = False
        self.lives = 2
        self.identity = ["Tough Civilian", "Civilian", "Good"]


class RomeoCivilian(Player):
    def __init__(self, playerno):
        self.playerno = playerno
        self.username = ""
        self.alive = True
        self.guarded = False
        self.identity = ["Romeo Civilian", "Civilian", "Good"]


class JulietCivilian(Player):
    def __init__(self, playerno):
        self.playerno = playerno
        self.username = ""
        self.alive = True
        self.guarded = False
        self.identity = ["Juliet Civilian", "Civilian", "Good"]


class Doctor(Player):
    def __init__(self, playerno):
        self.playerno = playerno
        self.username = ""
        self.alive = True
        self.guarded = False
        self.heal_unused = True
        self.poison_unused = True
        self.identity = ["Doctor", "Super", "Good"]


class HeroDetective(Player):
    def __init__(self, playerno):
        self.playerno = playerno
        self.username = ""
        self.alive = True
        self.guarded = False
        self.identity = ["Hero Detective", "Super", "Good"]

    def explode(self, person_to_take: Player):
        self.alive = False
        person_to_take.alive = False
    
    def check(self, person_to_check: Player):
        return person_to_check.identity[2]


class Guard(Player):
    def __init__(self, playerno):
        self.playerno = playerno
        self.username = ""
        self.alive = True
        self.guarded = False
        self.last_guarded = None
        self.identity = ["Guard", "Super", "Good"]


class Psycho(Player):
    def __init__(self, playerno):
        self.playerno = playerno
        self.username = ""
        self.alive = True
        self.guarded = False
        self.identity = ["Psycho", "Super", "Good"]


class Killer(Player):
    def __init__(self, playerno):
        self.playerno = playerno
        self.username = ""
        self.alive = True
        self.guarded = False
        self.identity = ["Killer", None, "Bad"]


class PsychicKiller(Player):
    def __init__(self, playerno):
        self.playerno = playerno
        self.username = ""
        self.alive = True
        self.guarded = False
        self.identity = ["Psychic Killer", None, "Bad"]
    
    def check(self, person_to_check: Player):
        return person_to_check.identity[1]


class SuperKiller(Player):
    def __init__(self, playerno):
        self.playerno = playerno
        self.username = ""
        self.alive = True
        self.guarded = False
        self.identity = ["Super Killer", None, "Bad"]

    def explode(self, person_to_take: Player):
        self.alive = False
        person_to_take.alive = False


roles = [SuperKiller, ToughCivilian, RomeoCivilian, JulietCivilian, Doctor, HeroDetective, Guard, Psycho, Killer, PsychicKiller]



"""
Player1 = ToughCivilian("1")
Player2  = RomeoCivilian("2")
Player3 = JulietCivilian("3")
Player4 = Doctor("4")
Player5 = HeroDetective("5")
Player6 = Guard("6")
Player7 = Psycho("7")
Player8 = Killer("8")
Player9 = PsychicKiller("9")
Player10 = SuperKiller("10")
players = [Player1, Player2, Player3, Player4, Player5, Player6, Player7, Player8, Player9, Player10]

Player6.guard(Player5) #Guard
Player2.check(Player10) #Romeo
Player3.check(Player10) #Juliet
print(romeo_juliet_check())
print(Player10.killed(False, False, True), "Kill") #Kill
print(Player9.check(Player6), "Psychic") #Psychic Killer 
print(Player5.check(Player8), "Detective") #Hero Detective 
for player in players:
    print(player.alive)

print("-------")

print(Player10.explode(Player7)) #Super Killer explode
Player8.killed(False, False, False) #Psycho takes Killer
for player in players:
    print(player.alive)

print("-------")"""