import pygame
import os

pygame.init()

img_size = (150, 100)

romeo_civ_img = pygame.transform.scale(
    pygame.image.load(os.path.join("images", "RomeoCivilian.png")), img_size
)
juliet_civ_img = pygame.transform.scale(
    pygame.image.load(os.path.join("images", "JulietCivilian.png")), img_size
)
tough_civ_img = pygame.transform.scale(
    pygame.image.load(os.path.join("images", "ToughCivilian.png")), img_size
)
guard_img = pygame.transform.scale(
    pygame.image.load(os.path.join("images", "Guard.png")), img_size
)
doctor_img = pygame.transform.scale(
    pygame.image.load(os.path.join("images", "Doctor.png")), img_size
)
hero_detective_img = pygame.transform.scale(
    pygame.image.load(os.path.join("images", "HeroDetective.png")), img_size
)
psycho_img = pygame.transform.scale(
    pygame.image.load(os.path.join("images", "Psycho.png")), img_size
)
killer_img = pygame.transform.scale(
    pygame.image.load(os.path.join("images", "Killer.png")), img_size
)
super_killer_img = pygame.transform.scale(
    pygame.image.load(os.path.join("images", "SuperKiller.png")), img_size
)
psychic_killer_img = pygame.transform.scale(
    pygame.image.load(os.path.join("images", "PsychicKiller.png")), img_size
)

# img for others
guard_shield_img = pygame.transform.scale(pygame.image.load(os.path.join("images", "guard_shield.png")), (50, 50))
kill_img = pygame.image.load(os.path.join("images", "kill.png"))
qn_takedown_img = pygame.image.load(os.path.join("images", "qn_takedown.png"))
voted_img = pygame.image.load(os.path.join("images", "voted.png"))

civilian_img = pygame.image.load(os.path.join("images", "civilian.png"))
super_img = pygame.transform.scale(pygame.image.load(os.path.join("images", "super.png")), (civilian_img.get_width(), civilian_img.get_height()))

good_img = pygame.transform.scale(pygame.image.load(os.path.join("images", "good.png")), (civilian_img.get_width(), civilian_img.get_height()))
bad_img = pygame.transform.scale(pygame.image.load(os.path.join("images", "bad.png")), (civilian_img.get_width(), civilian_img.get_height()))

save_img = pygame.transform.scale(pygame.image.load(os.path.join("images", "save.png")), (50, 50))
used_save_img = pygame.transform.scale(pygame.image.load(os.path.join("images", "used_save.png")), (50, 50))
poison_img = pygame.transform.scale(pygame.image.load(os.path.join("images", "poison.png")), (50, 50))
used_poison_img = pygame.transform.scale(pygame.image.load(os.path.join("images", "used_poison.png")), (50, 50))

def lf(filename):
    pygame.mixer.music.load(os.path.join("sounds", f"{filename}.mp3"))
    pygame.mixer.music.play()
    
