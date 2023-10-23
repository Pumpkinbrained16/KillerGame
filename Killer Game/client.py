import pygame
import random
import time
import sys

from game import Game
from roles import *
from network import Network, Get
from file_loading import *
# from pyvidplayer import Video

pygame.init()

width = 900
height = 700
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Killer Game")

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
DARK_YELLOW = (89, 89, 3)
GREY = (128, 128, 128)

BG_COLOR = WHITE
PLAYER_COLOR = YELLOW

identity_to_img = {
    "Tough Civilian": tough_civ_img,
    "Romeo Civilian": romeo_civ_img,
    "Juliet Civilian": juliet_civ_img,
    "Doctor": doctor_img,
    "Hero Detective": hero_detective_img,
    "Guard": guard_img,
    "Psycho": psycho_img,
    "Killer": killer_img,
    "Psychic Killer": psychic_killer_img,
    "Super Killer": super_killer_img
}

_identity_to_read = {
    "Romeo Civilian": "Romeo",
    "Juliet Civilian": "Juliet",
    "Guard": "Guard",
    "Killer": "Killers",
    "Psychic Killer": "Killers",
    "Super Killer": "Killers",
    "Doctor": "Doctor",
    "Hero Detective": "Hero Detective"
}

ans_to_img = {
    "Good": good_img,
    "Bad": bad_img,
    "Civilian": civilian_img,
    "Super": super_img
}

SHOW_MIDDLE_TEXT = pygame.USEREVENT + 1
CONCEAL_MIDDLE_TEXT = pygame.USEREVENT + 2

SHOW_ANSWER = pygame.USEREVENT + 3
CONCEAL_ANSWER = pygame.USEREVENT + 4

CONCEAL_EXPLOSION_VID = pygame.USEREVENT + 5

CONCEAL_VOTING_RESULTS = pygame.USEREVENT + 6

wait_for_activate = False

def identity_to_read(identity, game: Game):
    if identity != "Psychic Killer":
        return _identity_to_read[identity]
    else:
        print(game.night_turn)
        if game.night_turn in (2, 4):
            return "Psychic Killer"
        else:
            return "Killers"


class Button:
    def __init__(self):
        self.rect = None

    def draw(self, win: pygame.Surface, x, y, width, height, color, text, font_size=35, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(win, color, self.rect)
        font = pygame.font.SysFont("JetBrains Mono", font_size, True)
        text = font.render(text, 1, text_color)
        win.blit(
            text, 
            (
                x + 
                round(width/2) - 
                round(text.get_width()/2),
                y + 
                round(height/2) - 
                round(text.get_height()/2)
                )
        )
    
    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        try:
            if self.rect.x <= x1 <= self.rect.x + self.rect.width and self.rect.y <= y1 <= self.rect.y + self.rect.height:
                return True
            else:
                return False
        except AttributeError:
            pass
    
    def draw_outline(self, win: pygame.Surface, color):
        pygame.draw.rect(win, color, self.rect, 5)


class DrawnPlayer(Button):
    def __init__(self, playerno: int):
        self.playerno = playerno
        self.color = PLAYER_COLOR
        self.text_color = WHITE
        self.rect = None

    def draw(self, win: pygame.Surface, x, y, width, height, game: Game, pos, _player: Player, first=False, speaking_sequence: list[Player] | None=None): 
        player = game.find_role(self.playerno)
        self.rect = pygame.Rect(x, y, width, height)

        if game.time == "Night": # choose the color
            self.color = DARK_YELLOW
            self.text_color = WHITE
        else:
            self.color = PLAYER_COLOR
            self.text_color = BLACK

        if player.identity[2] == "Bad" and _player.identity[2] == "Bad":
            self.color = RED

        if player.playerno in [_p.playerno for _p in game.dead_players]:
            self.color = GREY
        
        pygame.draw.rect(win, self.color, self.rect) # draw the rect

        if ((self.click(pos) and game.time == "Night") or (game.time == "Voting" and self.click(pos))) and player not in game.dead_players:
            self.draw_outline(win, GREEN) # draw the outline if necessary
        
        if game.time == "Day" and speaking_sequence:
            if speaking_sequence[game.speaking_turn].playerno == player.playerno:
                self.draw_outline(win, GREEN)
        
        if game.time == "Voting" and str(player.playerno) == game.speaking:
            self.draw_outline(win, GREEN)
                
        font = pygame.font.SysFont("JetBrains Mono", 40, True) # blit the text
        text = font.render(str(self.playerno), 1, self.text_color)

        if not first:
            win.blit(
                text, 
                (
                    x + 
                    round(width/2) - 
                    round(text.get_width()/2),
                    y + 
                    round(height/2) - 
                    round(text.get_height()/2) - 
                    15
                    )   
            )

            text2 = font.render(player.username, 1, self.text_color)

            win.blit(
                text2, (
                    x + 
                    round(width/2) - 
                    round(text2.get_width()/2),
                    y + 
                    round(height/2) - 
                    round(text2.get_height()/2) +
                    15
                    )
            )

        else:
            win.blit(text, 
            (
                x + 25, 
                y + round(height / 2) - round(text.get_height()/2) - 15
                )
            )
        
            text2 = font.render(player.username, 1, self.text_color)

            win.blit(
                text2, (
                    x + 25,
                    y + 
                    round(height/2) - 
                    round(text2.get_height()/2) +
                    15
                    )
                )
    
    def display_role(self, win: pygame.Surface, player: Player):
        win.blit(identity_to_img[player.identity[0]], self.rect)

    def display_death(self, win: pygame.Surface, method_of_death="killed"):
        if method_of_death == "killed":
            self.display_killed(win)
        elif method_of_death == "voted":
            self.display_voted(win)
        elif method_of_death == "takedown":
            self.display_takedown(win)

    def display_poisoned(self, win: pygame.Surface):
        win.blit(
            pygame.transform.scale(poison_img, (self.rect.width, self.rect.height)), 
            (self.rect.x, self.rect.y)
        )

    def display_guard(self, win: pygame.Surface):
        win.blit(guard_shield_img, ((
                    self.rect.x + 
                    round(self.rect.width/2) - 
                    round(guard_shield_img.get_width()/2),
                    self.rect.y + 
                    round(self.rect.height/2) - 
                    round(guard_shield_img.get_height()/2) + 
                    40
                    )))

    def display_killed(self, win: pygame.Surface):
        win.blit(kill_img, ((
                    self.rect.x + 
                    round(self.rect.width/2) - 
                    round(kill_img.get_width()/2),
                    self.rect.y + 
                    round(self.rect.height/2) - 
                    round(kill_img.get_height()/2)
                    )))
    
    def display_voted(self, win: pygame.Surface):
        win.blit(voted_img, ((
                    self.rect.x + 
                    round(self.rect.width/2) - 
                    round(voted_img.get_width()/2),
                    self.rect.y + 
                    round(self.rect.height/2) - 
                    round(voted_img.get_height()/2)
                    )))

    def display_takedown(self, win: pygame.Surface):
        win.blit(qn_takedown_img, ((
                    self.rect.x + 
                    round(self.rect.width/2) - 
                    round(qn_takedown_img.get_width()/2),
                    self.rect.y + 
                    round(self.rect.height/2) - 
                    round(qn_takedown_img.get_height()/2)
                    )))
    
    def display_voting_results(self, win: pygame.Surface, game: Game):
        player = game.find_role(self.playerno)

        if not player.alive:
            return
        
        font = pygame.font.SysFont("JetBrains Mono", 40, True)

        if player in game.votes.keys():
            _voted = str(game.votes[player].playerno) # this is the thing we need to display
        else:
            _voted = "X"
        
        text = font.render(_voted, 1, BLACK)

        if self.rect.x == 0:
            place_to_blit = (self.rect.x + 
                    round(self.rect.width/2) - 
                    round(text.get_width()/2) + 50,
                    self.rect.y + 
                    round(self.rect.height/2) - 
                    round(text.get_height()/2))
        elif self.rect.y == 0:
            place_to_blit = (self.rect.x + 
                    round(self.rect.width/2) - 
                    round(text.get_width()/2),
                    self.rect.y + 
                    round(self.rect.height/2) - 
                    round(text.get_height()/2) + 50)
        elif self.rect.x == 750:
            place_to_blit = (self.rect.x + 
                    round(self.rect.width/2) - 
                    round(text.get_width()/2) - 50,
                    self.rect.y + 
                    round(self.rect.height/2) - 
                    round(text.get_height()/2))
        elif self.rect.y == 600:
            place_to_blit = (self.rect.x + 
                    round(self.rect.width/2) - 
                    round(text.get_width()/2) + 125,
                    self.rect.y + 
                    round(self.rect.height/2) - 
                    round(text.get_height()/2) - 75)
        
        win.blit(text, place_to_blit)


drawn_players = [DrawnPlayer(1), DrawnPlayer(2), DrawnPlayer(3), DrawnPlayer(4), DrawnPlayer(5), DrawnPlayer(6), DrawnPlayer(7), DrawnPlayer(8), DrawnPlayer(9), DrawnPlayer(10)]
yes_btn = Button()
no_btn = Button()
pass_btn = Button() # after speaking part, code the voting and win condition, then code takedown
activate_button = Button()

middle_text_font = pygame.font.SysFont("Roboto", 30)
middle_text = "" # middle_text will never be set to False, once it's set at least once. Instead, it will not be blit
displayed_rj_result = False
blit_middle_text = False
done = False # done will be the variable that checks if a player has finished what they're supposed to do, then will show "close ur eyes"
answer = ""
blit_ans = False
ask_heal = False
ask_poison = False
voted = None
voted_out = []
dispute = []
dispute_turn = 0
second_vote = None
once = False

waiting_for = None
can_activate = False
# blit_explosion_vid = False
# e_vid_pos = ()

_show_voting_results = False

def draw_players(win: pygame.Surface, player: Player, game: Game, pos, speaking_sequence: list[Player] | None):
    global drawn_players, once
    playerno = player.playerno
    if drawn_players[0].playerno == 1 and player.playerno != 1:
        once = False
    
    if not once:
        drawn_players = drawn_players[playerno - 1:] + drawn_players[:playerno - 1]
        once = True
    
    drawn_players[0].draw(win, 180, 600, 300, 100, game, pos, player, True, speaking_sequence) # draw the current player
    # if y == 600, y -= 75

    drawn_players[1].draw(win, 0, 487.5, 150, 150, game, pos, player, False, speaking_sequence) # if x == 0, x + 100
    drawn_players[2].draw(win, 0, 275, 150, 150, game, pos, player, False, speaking_sequence)
    drawn_players[3].draw(win, 0, 62.5, 150, 150, game, pos, player, False, speaking_sequence)

    drawn_players[4].draw(win, 175, 0, 150, 150, game, pos, player, False, speaking_sequence) # if y == 0, y + 100
    drawn_players[5].draw(win, 375, 0, 150, 150, game, pos, player, False, speaking_sequence)
    drawn_players[6].draw(win, 575, 0, 150, 150, game, pos, player, False, speaking_sequence)

    drawn_players[7].draw(win, 750, 62.5, 150, 150, game, pos, player, False, speaking_sequence) # if x == 750, x - 100
    drawn_players[8].draw(win, 750, 275, 150, 150, game, pos, player, False, speaking_sequence)
    drawn_players[9].draw(win, 750, 487.5, 150, 150, game, pos, player, False, speaking_sequence)

    for drawn_player in drawn_players:
        _player = game.find_role(drawn_player.playerno)
        if isinstance(player, Guard) and game.time == "Night":
            if _player.guarded:
                drawn_player.display_guard(win)
        elif player.identity[2] == "Bad" and _player == game.killed_person and game.time == "Night":
            drawn_player.display_killed(win)
        elif isinstance(player, Doctor) and game.time == "Night" and game.poisoned_person:
            try:
                if _player.playerno == game.poisoned_person.playerno:
                    drawn_player.display_poisoned(win)
            except AttributeError:
                pass # this means Doctor hasn't poisoned
        
        if _player.playerno in [_p.playerno for _p in game.dead_players]:
            if _player in game.voted_out:
                drawn_player.display_death(win, "voted")
            elif _player in game.tookdown:
                drawn_player.display_death(win, "takedown")
            else:
                drawn_player.display_death(win, "killed")

"""explosion_vid = Video("explosion.mp4")
explosion_vid.set_size((200, 100))

explosion2_vid = Video("explosion2.mp4")
explosion2_vid.set_size((200, 100))

xl_video = Video("XL! Video!.mp4")
xl_video.set_size((100, 100))

explosion3_vid = Video("explosion3.mp4")
explosion3_vid.set_size((200, 100))"""

def redraw_window(win: pygame.Surface, game: Game, player: Player, pos, n: Network, events=None, speaking_sequence=None): # blit_explosion_vid, e_vid_pos, 
    global width, height, displayed_rj_result, middle_text, middle_text_font, blit_middle_text, done, blit_ans, answer, ask_heal, ask_poison, BG_COLOR, dispute, dispute_turn, second_vote, waiting_for, identity_to_read, can_activate, voted_out, _show_voting_results

    if not game.ready(): # waiting screen
        win.fill(GREY)
        font = pygame.font.SysFont("Jetbrains Mono", 80)
        text = font.render("Waiting for player...", 1, RED)
        win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))

        if not events:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        
        # explosion_vid.draw(win, (100, 100))
        # explosion2_vid.draw(win, (500, 100))
        # xl_video.draw(win, (100, 100))
        # explosion3_vid.draw(win, (400, 400))
        pygame.display.update()
        return

    pygame.draw.rect(win, BG_COLOR, (0, 0, width, height)) # draw bg

    draw_players(win, player, game, pos, speaking_sequence) # draw players, guarded, and killed

    role_img = identity_to_img[player.identity[0]]
    win.blit(role_img, (255, 500, 150, 100)) # draw role

    can_activate = False

    if isinstance(player, SuperKiller):
        if game.time == "Day":
            if player.playerno not in [p.playerno for p in game.dead_players]:
                activate_button.draw(win, 500, 600, 200, 100, RED, "ACTIVATE") # draw ACTIVATE
                can_activate = True
            if player.playerno in [p.playerno for p in game.died_last_night] and speaking_sequence[game.speaking_turn].playerno == player.playerno:
                activate_button.draw(win, 500, 600, 200, 100, RED, "ACTIVATE") # draw ACTIVATE
                can_activate = True

        elif game.time == "Voting":
            if player.playerno in [p.playerno for p in game.died_last_night] and game.speaking == str(player.playerno) and player.playerno in [p.playerno for p in voted_out]:
                activate_button.draw(win, 500, 600, 200, 100, RED, "ACTIVATE") # draw ACTIVATE
                can_activate = True
    
    if isinstance(player, HeroDetective): 
        if game.time == "Day":
            if player.playerno not in [p.playerno for p in game.dead_players]:
                activate_button.draw(win, 500, 600, 200, 100, RED, "ACTIVATE") # draw ACTIVATE
                can_activate = True

    if isinstance(player, Psycho):
        if game.time == "Day":
            if player.playerno in [p.playerno for p in game.died_last_night] and speaking_sequence[game.speaking_turn].playerno == player.playerno:
                activate_button.draw(win, 500, 600, 200, 100, RED, "ACTIVATE") # draw ACTIVATE
                can_activate = True
        
        if game.time == "Voting":
            if game.speaking == str(player.playerno) and player.playerno in [p.playerno for p in voted_out]:
                activate_button.draw(win, 500, 600, 200, 100, RED, "ACTIVATE") # draw ACTIVATE
                can_activate = True
    
    if can_activate:
        if wait_for_activate:
            activate_button.draw_outline(win, GREEN)

    if isinstance(player, Doctor) and player not in game.dead_players:
        save_status_img = save_img if player.heal_unused else used_save_img
        poison_status_img = poison_img if player.poison_unused else used_poison_img
        win.blit(save_status_img, (10, 487.5 + 150 + 10))
        win.blit(poison_status_img, (10 + save_status_img.get_width() + 10, 487.5 + 150 + 10))

    if game.time == "Night":
        BG_COLOR = BLACK
        if not displayed_rj_result and isinstance(player, (RomeoCivilian, JulietCivilian)) and game.checked_person() and not done: # change middle_text to rj_result
            if type(game.checked_person()) == str:
                middle_text = "There is no match! :("
            else:
                middle_text = "It's a match! {}, the person you checked is a {}".format("Romeo" if isinstance(player, RomeoCivilian) else "Juliet", game.checked_person().identity[0])
            
            blit_middle_text = True
            pygame.time.set_timer(CONCEAL_MIDDLE_TEXT, 3500)
            displayed_rj_result = True

        if game.just_killed and player.identity[2] == "Bad":
            print("ok1")
            waiting_for = None
            done = True
            if isinstance(player, PsychicKiller):
                print("ok2")
                time.sleep(0.5)
                game.just_killed = False
                n.send(game)
            else:
                time.sleep(0.5)

        if ask_heal and isinstance(player, Doctor):
            if player.heal_unused:
                yes_btn.draw(win, width/2 - 150 - 25, height/2 + 35/2 + 10, 150, 100, GREEN, "YES")
                no_btn.draw(win, width/2 + 25, height/2 + 35/2 + 10, 150, 100, RED, "NO")

        if ask_poison and isinstance(player, Doctor):
            no_btn.draw(win, width/2 - 150/2, height/2 + 35/2 + 10, 150, 100, RED, "NO")

    elif game.time == "Day":
        BG_COLOR = WHITE
        if speaking_sequence and not blit_middle_text:
            if speaking_sequence[game.speaking_turn].playerno == player.playerno:
                pass_btn.draw(win, width/2 - 200/2, height/2 - 100/2, 200, 100, RED, "PASS")
    
    elif game.time == "Voting":
        if game.speaking == str(player.playerno) and not blit_middle_text:
            pass_btn.draw(win, width/2 - 200/2, height/2 - 100/2, 200, 100, RED, "PASS")

    for event in events:
        if event.type == SHOW_MIDDLE_TEXT: 
            blit_middle_text = True
        
        if event.type == CONCEAL_MIDDLE_TEXT:
            pygame.time.set_timer(CONCEAL_MIDDLE_TEXT, 0)
            blit_middle_text = False

            if game.game_ends():
                text = middle_text_font.render("The game ends, the {} have won!".format(game.winners()), 1, BLACK)
                win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
                for drawn_player in drawn_players:
                    drawn_player.display_role(win, game.find_role(drawn_player.playerno))
                
                pygame.display.update()
                pygame.time.delay(10000)
                return "ends"

            if game.time == "Night":
                if "match" in middle_text and isinstance(player, JulietCivilian):
                    game.night_turnover()
                    n.send(game)

                if "save" in middle_text and ask_heal and isinstance(player, Doctor):
                    if not player.heal_unused and player.poison_unused:
                        ask_heal = False
                        show_middle_text("Would you like to poison anyone?")
                        ask_poison = True
                
                if "close your eyes" in middle_text and "Nightfall" not in middle_text and not isinstance(player, (JulietCivilian, SuperKiller, Killer)):
                    game.night_turnover()
                    game = n.send(game)
                    print("ok")

            elif game.time == "Voting":
                if "No last words" in middle_text and game.time == "Voting" and not wait_for_activate: # that means that if psycho is voted off with no last words, they have the 3.5s to activate, if not, they will not be able to activate
                    game.instant_round_turnover()
                    n.send(game)
                    
                if "Second tied vote!" == middle_text:
                    print("round turnover!")
                    game.instant_round_turnover()
                    print(game.round)

                if "Voting begins" in middle_text:
                    show_voting_results()
        
        if event.type == SHOW_ANSWER:
            blit_ans = True
        
        if event.type == CONCEAL_ANSWER:
            pygame.time.set_timer(CONCEAL_ANSWER, 0)
            blit_ans = False

        if event.type == CONCEAL_EXPLOSION_VID:
            # explosion_vid.close()
            # blit_explosion_vid = False
            pygame.time.set_timer(CONCEAL_EXPLOSION_VID, 0)
            if isinstance(player, HeroDetective) or (isinstance(player, SuperKiller) and player not in game.died_last_night):
                game.instant_round_turnover()
                game.speaking_turn = 0
                n.send(game)
            
            if game.game_ends():
                text = middle_text_font.render("The game ends, the {} have won!".format(game.winners()), 1, BLACK)
                win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
                for drawn_player in drawn_players:
                    drawn_player.display_role(win, game.find_role(drawn_player.playerno))
                
                pygame.display.update()
                pygame.time.delay(10000)
                return "ends"
        
        if event.type == CONCEAL_VOTING_RESULTS:
            pygame.time.set_timer(CONCEAL_VOTING_RESULTS, 0)
            _show_voting_results = False
            voted = None
            voted_out = game.calc_votes()
            to_say = ""

            if len(voted_out) == 1:
                to_say = "Player {} has been voted out. ".format(voted_out[0].playerno)
                if game.round % 2 == 1: 
                    to_say = to_say + "Any last words?" # takedown
                    game.speaking = str(voted_out[0].playerno)
                else:
                    to_say = to_say + "No last words." # takedown
                
                if game.roles[voted_out[0].playerno - 1] not in game.dead_players and game.roles[voted_out[0].playerno - 1] not in game.voted_out and game.roles[voted_out[0].playerno - 1] in game.alive_players:
                    game.roles[voted_out[0].playerno - 1].alive = False
                    game.alive_players.remove(game.roles[voted_out[0].playerno - 1])
                    game.dead_players.append(game.roles[voted_out[0].playerno - 1])
                    game.voted_out.append(game.roles[voted_out[0].playerno - 1])
                    game.died_last_night.append(game.roles[voted_out[0].playerno - 1])
                
                n.send(game)

                show_middle_text(to_say)

            elif len(voted_out) == 0 and game.time == "Voting": # all no vote
                game.instant_round_turnover()
            
            elif len(voted_out) > 1:
                if second_vote and game.trigger_second_voting:
                    print("got second tie")
                    show_middle_text("Second tied vote!")
                else:
                    dispute = [str(player.playerno) for player in voted_out]
                    to_say = "Tied vote between players {}. Dispute!".format(", ".join(dispute))

                    show_middle_text(to_say)
                    game.speaking = dispute[dispute_turn]
                    voted_out = []
                    n.send(game)
                    second_vote = True
                    
            print(second_vote, game.trigger_second_voting)
            if second_vote and game.trigger_second_voting:
                second_vote = False
                game.trigger_second_voting = False
                time.sleep(1)
                n.send(game)
                # print("second voteeeeeeee", second_vote, "!!!!!")
            
            time.sleep(0.5)
            game.votes = dict()
            n.send(game)

    if done:
        middle_text = "{}, close your eyes".format(identity_to_read(player.identity[0], game))
        done = False
        blit_middle_text = True
        pygame.time.set_timer(CONCEAL_MIDDLE_TEXT, 3500)

    if blit_middle_text: # draw middle text
        if game.time == "Night":
            text = middle_text_font.render(middle_text, 1, WHITE)
        else:
            text = middle_text_font.render(middle_text, 1, BLACK)
        
        win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
    
    if blit_ans:
        to_blit = ans_to_img[answer]
        
        win.blit(to_blit, (width/2 - to_blit.get_width()/2, height/2 + 35/2 + 10))
    
    if _show_voting_results:
        for drawn_player in drawn_players:
            drawn_player.display_voting_results(win, game)

    """if blit_explosion_vid:
        pass
        # print("blitting explosion vid...")
        # explosion_vid.draw(win, e_vid_pos)"""

    pygame.display.update()


def show_middle_text(text: str):
    global middle_text
    middle_text = text
    pygame.event.post(pygame.event.Event(SHOW_MIDDLE_TEXT))
    pygame.time.set_timer(CONCEAL_MIDDLE_TEXT, 3500)

def show_answer(ans: str): # answer is good, bad, civilian, or super
    global answer
    answer = ans
    pygame.event.post(pygame.event.Event(SHOW_ANSWER))
    pygame.time.set_timer(CONCEAL_ANSWER, 3500)

def show_explosion_vid(pos):
    # global blit_explosion_vid, e_vid_pos
    pygame.time.set_timer(CONCEAL_EXPLOSION_VID, 3200)
    # blit_explosion_vid = True
    # e_vid_pos = pos

def show_voting_results():
    global _show_voting_results
    _show_voting_results = True
    pygame.time.set_timer(CONCEAL_VOTING_RESULTS, 3000)


def main(username):
    global middle_text, done, ask_heal, ask_poison, voted, dispute, dispute_turn, second_vote, waiting_for, wait_for_activate
    run = True
    clock = pygame.time.Clock()
    n = Network()
    player = n.get_player()
    print("You are player", player.playerno)
    print("Your role is", player.identity[0])

    game = n.send(Get())
    game.roles[player.playerno - 1].username = username
    n.send(game)

    print(game)
    done_rounds_nightfall = []
    done_rounds_who_died = []
    done_rounds_voting = []

    current_night_turn = -1

    while run:
        clock.tick(60)
        pos = pygame.mouse.get_pos()
        events = None

        try:
            game = n.send(Get())
            player = game.roles[player.playerno - 1]
        except:
            run = False
            print("Couldn't get game")
            break
        
        
        if game.ready():

            alive_killers = [p for p in game.roles if p.identity[2] == "Bad" and p not in game.dead_players]

            if game.time == "Night":
                if not blit_middle_text and not game.speaking and game.round not in done_rounds_nightfall:
                    show_middle_text("Nightfall, everyone close your eyes")
                    lf("Nightfall, everyone close your eyes")
                    done_rounds_nightfall.append(game.round)
                    print("said nightfall")
                else:
                    if game.night_sequence()[game.night_turn] == player.identity[0] and not blit_middle_text and not done: #Superpower/romeo/juliet
                        if player not in game.dead_players:
                            if isinstance(player, Guard) and waiting_for != "Guard":
                                show_middle_text("Guard, open your eyes. Guard, who would you like to guard?")
                                waiting_for = "Guard"
                            elif isinstance(player, PsychicKiller) and waiting_for != "Psychic Killer":
                                show_middle_text("Psychic Killer, open your eyes. Psychic Killer, who would you like to check?")
                                waiting_for = "Psychic Killer"
                            elif isinstance(player, Doctor) and not ask_heal and waiting_for != "Doctor":
                                if player.heal_unused or player.poison_unused:
                                    show_middle_text("Doctor, open your eyes. Doctor, player {} has died. Would you like to save them?".format(game.killed_person.playerno))
                                    ask_heal = True
                                    waiting_for = "Doctor"
                                else:
                                    game.night_turnover()
                                    n.send(game)
                            elif isinstance(player, HeroDetective) and waiting_for != "Hero Detective":
                                show_middle_text("Hero Detective, open your eyes. Hero Detective, who would you like to check?")
                                waiting_for = "Hero Detective"
                            elif isinstance(player, RomeoCivilian) and waiting_for != "Romeo Civilian":
                                show_middle_text("Romeo, open your eyes. Romeo, who would you like to check?")
                                waiting_for = "Romeo Civilian"
                            elif isinstance(player, JulietCivilian) and waiting_for != "Juliet Civilian":
                                show_middle_text("Juliet, open your eyes. Juliet, who would you like to check?")
                                waiting_for = "Juliet Civilian"
                        else:
                            # say() 
                            pygame.time.delay(random.randint(3000, 10000))
                            game.night_turnover()
                            n.send(game)

                            to_read = game.night_sequence[game.night_turn]
                            lf(f"{to_read}, close your eyes")

                    elif game.night_sequence()[game.night_turn] == "Killers" and player.identity[2] == "Bad" and waiting_for != "Killers" and not blit_middle_text: #Killers
                        show_middle_text("Killers, open your eyes. Killers, who would you like to kill?")
                        waiting_for = "Killers"
                    
                    if current_night_turn != game.night_turn and not blit_middle_text and not done:
                        to_read = game.night_sequence()[game.night_turn]
                        if "Civilian" in to_read:
                            to_read = to_read[:-9]
                        lf(f"{to_read}, open your eyes")
                        current_night_turn = game.night_turn

            elif game.time == "Day":
                if not blit_middle_text and game.round not in done_rounds_who_died:
                    to_say = "Daytime, everyone open your eyes. "
                    who_died = game.who_died()
                    game.speaking_sequence = game._speaking_sequence()

                    if not game.died_last_night:
                        to_say = to_say + "Last night was a peaceful night. No one has died"
                    else:
                        if len(game.died_last_night) == 1:
                            to_say = to_say + "Last night, player {} has died. ".format(game.died_last_night[0].playerno)
                        elif len(game.died_last_night) == 2:
                            to_say = to_say + "Last night, player {}, player {} has died. ".format(game.died_last_night[0].playerno, game.died_last_night[1].playerno)
                        else:
                            to_say = to_say + "Last night, player {}, player {} and player {} has died. ".format(game.died_last_night[0].playerno, game.died_last_night[1].playerno, game.died_last_night[2].playerno)

                        if game.round % 2 == 1:
                            to_say = to_say + "Any last words?"
                        else:
                            to_say = to_say + "No last words."
        
                    show_middle_text(to_say)

                    done_rounds_who_died.append(game.round)

                    n.send(game)
            
            elif game.time == "Voting":
                if not second_vote:
                    print(done_rounds_voting)
                    if not blit_middle_text and game.round not in done_rounds_voting:
                        show_middle_text("Voting begins! 3...2...1...")
                        print("said voting, round:", game.round)
                        done_rounds_voting.append(game.round)
                        print("done_rounds_voting:", done_rounds_voting)
                else:
                    if game.trigger_second_voting and not blit_middle_text:
                        print("said voting 2, round:", game.round)
                        show_middle_text("Voting begins! 3...2...1...")
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print("Clicked!")
                    if game.time == "Night":
                        if waiting_for == "Guard" and isinstance(player, Guard):
                            for drawn_player in drawn_players:
                                if drawn_player.click(pos):
                                    if game.find_role(drawn_player.playerno) != game.last_guarded:
                                        if drawn_player.playerno not in [p.playerno for p in game.dead_players]:
                                            game.roles[drawn_player.playerno - 1].guarded = True
                                            game.last_guarded = game.find_role(drawn_player.playerno)
                                    
                                            game = n.send(game)
                                            waiting_for = None
                                            done = True
                                            print(f"Guarded {drawn_player.playerno}")

                                            lf("Guard, close your eyes")

                        elif waiting_for == "Doctor" and ask_heal and isinstance(player, Doctor):
                            if yes_btn.click(pos) and player.heal_unused:
                                if not game.find_role(game.killed_person.playerno).alive:
                                    game.roles[game.killed_person.playerno - 1].alive = True
                                else:
                                    game.roles[game.killed_person.playerno - 1].alive = False # overdose
                                
                                game.roles[player.playerno - 1].heal_unused = False
                                game = n.send(game)
                                ask_heal = False
                                done = True
                                waiting_for = None
                                print("Healed!")
                            elif no_btn.click(pos) and player.poison_unused and player.heal_unused:
                                ask_heal = False
                                ask_poison = True
                                show_middle_text("Would you like to poison anyone?")
                            elif no_btn.click(pos) and not player.poison_unused and player.heal_unused:
                                done = True
                                ask_heal = False
                                waiting_for = None

                        elif waiting_for == "Doctor" and ask_poison and isinstance(player, Doctor):
                            for drawn_player in drawn_players:
                                if drawn_player.click(pos):
                                    if drawn_player.playerno not in [p.playerno for p in game.dead_players]:
                                        game.roles[drawn_player.playerno - 1].alive = False
                                        game.roles[player.playerno - 1].poison_unused = False
                                        game.poisoned_person = game.find_role(drawn_player.playerno)
                                
                                        game = n.send(game)
                                        waiting_for = None
                                        ask_poison = False
                                        done = True
                                        print(f"Poisoned {drawn_player.playerno}")
                            
                            if no_btn.click(pos):
                                waiting_for = None
                                ask_poison = False
                                done = True

                        elif waiting_for == "Psychic Killer" and isinstance(player, PsychicKiller):
                            for drawn_player in drawn_players:
                                if drawn_player.click(pos):
                                    if drawn_player.playerno not in [p.playerno for p in game.dead_players] and game.find_role(drawn_player.playerno).identity[2] != "Bad":
                                        show_answer(game.find_role(drawn_player.playerno).identity[1])
                                
                                        game = n.send(game)
                                        waiting_for = None
                                        done = True
                                        print(f"Psychic checked {drawn_player.playerno}")

                        elif waiting_for == "Hero Detective" and isinstance(player, HeroDetective):
                            for drawn_player in drawn_players:
                                if drawn_player.click(pos):
                                    if drawn_player.playerno not in [p.playerno for p in game.dead_players]:
                                        show_answer(game.find_role(drawn_player.playerno).identity[2])
                                
                                        game = n.send(game)
                                        waiting_for = None
                                        done = True

                                        print(f"Detective checked {drawn_player.playerno}")

                        elif isinstance(player, (RomeoCivilian, JulietCivilian)) and (waiting_for == "Romeo Civilian" or waiting_for == "Juliet Civilian"):
                            for drawn_player in drawn_players:
                                if drawn_player.click(pos):
                                    game.romeo_juliet_check(game.find_role(drawn_player.playerno))
                            
                                    game = n.send(game)
                                    waiting_for = None
                                    done = True

                                    lf("{}, close your eyes".format("Romeo" if isinstance(player, RomeoCivilian) else "Juliet"))
                        
                        elif waiting_for == "Killers":
                            killer_that_kills = alive_killers[0]

                            if player.playerno == killer_that_kills.playerno:
                                for drawn_player in drawn_players:
                                    if drawn_player.click(pos):
                                        if drawn_player.playerno not in [p.playerno for p in game.dead_players]:
                                            game.roles[drawn_player.playerno - 1].killed()
                                            game.killed_person = game.find_role(drawn_player.playerno)
                                            game.just_killed = True

                                            game = n.send(game)
                                            waiting_for = None

                                            print(f"Killed {drawn_player.playerno}")
                    
                    elif game.time == "Day":
                        if game.speaking_sequence[game.speaking_turn].playerno == player.playerno:
                            try:
                                if pass_btn.click(pos):
                                    game.speaking_turnover()
                                    print("speaking turnover!")
                                    n.send(game)
                            except AttributeError:
                                pass
                        
                        if can_activate:
                            if activate_button.click(pos):
                                if not wait_for_activate:
                                    wait_for_activate = True
                                else:
                                    wait_for_activate = False
                            
                            if wait_for_activate:
                                for drawn_player in drawn_players:
                                    if drawn_player.click(pos):
                                        if drawn_player.playerno not in [p.playerno for p in game.dead_players]:
                                            game.roles[drawn_player.playerno - 1].alive = False
                                            game.alive_players.remove([p for p in game.alive_players if p.playerno == drawn_player.playerno][0])
                                            game.dead_players.append(game.roles[drawn_player.playerno - 1])
                                            game.tookdown.append(game.roles[drawn_player.playerno - 1])

                                            if isinstance(player, HeroDetective) or (isinstance(player, SuperKiller) and player not in game.died_last_night): # self-sacrifice, if caused by killed or voted out, it's different 
                                                game.roles[player.playerno - 1].alive = False
                                                game.alive_players.remove([p for p in game.alive_players if p.playerno == player.playerno][0])
                                                game.dead_players.append(game.roles[player.playerno - 1])
                                                game.tookdown.append(game.roles[player.playerno - 1])
                                            else:
                                                game.speaking_sequence.remove([p for p in game.speaking_sequence if p.playerno == drawn_player.playerno][0])
                                                game.speaking_sequence.insert(game.speaking_turn + 1, game.roles[drawn_player.playerno - 1])
                                            
                                            n.send(game)

                                            show_explosion_vid((drawn_player.rect.x, drawn_player.rect.y))

                    
                    elif game.time == "Voting":
                        if can_activate:
                            if activate_button.click(pos):
                                if not wait_for_activate:
                                    wait_for_activate = True
                                else:
                                    wait_for_activate = False
                            
                            if wait_for_activate:
                                for drawn_player in drawn_players:
                                    if drawn_player.click(pos):
                                        if drawn_player.playerno not in [p.playerno for p in game.dead_players]:
                                            game.roles[drawn_player.playerno - 1].alive = False
                                            game.alive_players.remove([p for p in game.alive_players if p.playerno == drawn_player.playerno][0])
                                            game.dead_players.append(game.roles[drawn_player.playerno - 1])
                                            game.tookdown.append(game.roles[drawn_player.playerno - 1])

                                            game.speaking_sequence.remove([p for p in game.speaking_sequence if p.playerno == drawn_player.playerno][0])
                                            game.speaking_sequence.insert(game.speaking_turn + 1, game.roles[drawn_player.playerno - 1])
                                            
                                            n.send(game)

                                            show_explosion_vid((drawn_player.rect.x, drawn_player.rect.y))
                        
                        if not game.speaking:
                            for drawn_player in drawn_players:
                                if not second_vote:
                                    if drawn_player.click(pos):
                                        game.vote(player, game.find_role(drawn_player.playerno))
                                        print("voted!!!!!!!")
                                        voted = drawn_player.playerno

                                        game = n.send(game)
                                        waiting_for = None
                                else:
                                    if drawn_player.click(pos) and str(drawn_player.playerno) in dispute and str(player.playerno) not in dispute:
                                        game.vote(player, game.find_role(drawn_player.playerno))
                                        print("voted!!!!!!!")
                                        voted = drawn_player.playerno

                                        game = n.send(game)
                                        waiting_for = None
                        
                        if game.speaking == str(player.playerno):
                            if pass_btn.click(pos):
                                if dispute:
                                    dispute_turn += 1
                                    try:
                                        game.speaking = dispute[dispute_turn]
                                    except IndexError: # that means we've reached the end of the list
                                        dispute = []
                                        game.trigger_second_voting = True # this will trigger "Voting begins!"
                                        game.speaking = None
                                        n.send(game)
                                        print("reached end of list, 2nd voting")
                                else:
                                    game.instant_round_turnover()
                                    game.speaking = None
                                
                                n.send(game)
                                print(game.trigger_second_voting, "trigger second voting!!!!!")
                                print(second_vote, "second vote!!!!!!!!!!!")


        if game.time == "Day" and game.speaking_sequence:
            if redraw_window(win, game, player, pos, n, events, game.speaking_sequence) == "ends":
                run = False
                break
        else:
            if redraw_window(win, game, player, pos, n, events) == "ends":
                run = False
                break


play_btn = Button()

base_font = pygame.font.Font(None, 42)
user_text = ''

# create rectangle
input_rect = pygame.Rect(width/2 - 350/2 + 210, height/2 - 50/2 + 50, 200, 50)

# color_active stores color(lightskyblue3) which
# gets active when input box is clicked by user
color_active = pygame.Color('lightskyblue3')

# color_passive store color(chartreuse4) which is
# color of input box.
color_passive = pygame.Color('chartreuse4')
color = color_passive

active = False


def menu_screen():
    global width, height, play_btn, base_font, user_text, input_rect, color_active, color_passive, color, active
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        win.fill(GREY)
        font = pygame.font.SysFont("Jetbrains Mono", 90)
        text = font.render("KILLER GAME", 1, BLACK)
        win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2 - 30))

        font2 = pygame.font.SysFont("Jetbrains Mono", 50)
        text2 = font2.render("USERNAME: ", 1, BLACK)
        win.blit(text2, (width/2 - text2.get_width()/2 - 90, height/2 - text2.get_height()/2 + 50))

        play_btn.draw(win, width/2 - 300/2, height/2 - 150/2 + 190, 300, 150, RED, "PLAY", 60, WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False

                if play_btn.click(pygame.mouse.get_pos()):
                    main(user_text)
        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    if len(user_text) < 10:
                        user_text += event.unicode

        if active:
            color = color_active
        else:
            color = color_passive
            
        # draw rectangle and argument passed which should
        # be on screen
        pygame.draw.rect(win, color, input_rect)
    
        text_surface = base_font.render(user_text, True, WHITE)
        
        # render at position stated in arguments
        win.blit(text_surface, (input_rect.x+5, input_rect.y+5))
        
        # set width of textfield so that text cannot get
        # outside of user's text input
        input_rect.w = max(200, text_surface.get_width()+10)

        pygame.display.update()


while True:
    menu_screen()