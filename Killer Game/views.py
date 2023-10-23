import random
from flask import render_template, Blueprint, request, redirect
from roles import Player, ToughCivilian, RomeoCivilian, JulietCivilian, Doctor, HeroDetective, Guard, Psycho, Killer, PsychicKiller, SuperKiller

views = Blueprint(__name__, "views")

players_usernames = []
players = [] # [Player(), HeroDetective() or Doctor or...]
roles = ["Tough Civilian", "Romeo Civilian", "Juliet Civilian", "Doctor", "Hero Detective", "Guard", "Psycho", "Killer", "Psychic Killer", 
"Super Killer"]
roles_unused = roles
role_match_class = {
    "Tough Civilian": ToughCivilian, 
    "Romeo Civilian": RomeoCivilian, 
    "Juliet Civilian": JulietCivilian, 
    "Doctor": Doctor, 
    "Hero Detective": HeroDetective, 
    "Guard": Guard, 
    "Psycho": Psycho, 
    "Killer": Killer, 
    "Psychic Killer": PsychicKiller, 
    "Super Killer": SuperKiller
}

@views.route("/")
def home():
    return render_template("home.html")


@views.route("/waiting", methods=["POST"])
def waiting():
    args = request.form
    username = args.get("username")
    players_usernames.append(username)
    if len(players_usernames) < 10:
        return render_template("waiting.html", username=username)
    elif len(players_usernames) == 10:
        return redirect("/play")


@views.route("/play", methods=["POST"])
def play(): #check tough_civ_killed_once, if can "take", reset guarded in day, vote to kill, super killer immediate takedown, inducing nightfall, daytime voting
    #Counter(["1", "3", "3", "3"]).most_common(1)[0]
    for player_username in players_usernames:
        role = role_match_class[random.choice(roles_unused)] #Class
        players.append(role(player_username))
        roles_unused.remove(role)
    return render_template("play.html")
