import pygame
import os
import sys
from Sprites import Person, Enemies, GameOver, Timer, Boss1, Boss2, Boss3
from random import choice

pygame.init()
pygame.mixer.init()

WIDTH = 360
HEIGHT = 640


def load_image(name):  # загрузчик картинок
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert_alpha()
    return image


class Quit(pygame.sprite.Sprite):  # кнопка выхода
    def __init__(self, group, im):
        super().__init__(group)
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 30
        self.rect.y = 5

    def update(self, *args):
        if GAMING and self.rect.x != WIDTH:
            self.rect.x += 1
        elif not GAMING and self.rect.x != WIDTH - 30:
            self.rect.x -= 1


def terminate():
    pygame.quit()
    sys.exit()


screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)  # создание холста и необходимых групп
all_enemies = pygame.sprite.Group()
Person_group = pygame.sprite.GroupSingle()
all_obstacles = pygame.sprite.Group()
all_bosses = pygame.sprite.Group()
quit_group = pygame.sprite.GroupSingle()

person = Person(Person_group,  # сам персонаж, которым мы управляем
                (load_image(r'flappy\1.png'),
                 load_image(r'flappy\2.png'),
                 load_image(r'flappy\3.png')),
                load_image(r'flappy\lose.png'),
                (pygame.mixer.Sound(r'data\flappy\0.ogg'),
                 pygame.mixer.Sound(r'data\flappy\1.ogg'),
                 pygame.mixer.Sound(r'data\flappy\2.ogg'))
                )

clock = pygame.time.Clock()
screen.fill((255, 255, 255))
GAMING = False
f = pygame.font.Font(r'data\font.ttf', 28)
text = f.render('Нажмите кн. мыши или пробел', 0, (0, 0, 0))
fon = pygame.Surface((WIDTH, HEIGHT))
fon.fill((0, 0, 0))
fon.set_alpha(100)

QuiT = Quit(quit_group, load_image('close.png'))
close = False

SPAWN_ENEMIES = 24  # вражеские миньоны
pygame.time.set_timer(SPAWN_ENEMIES, 3000)
enemies = [load_image(r'enemies\gumball.png'),
           load_image(r'enemies\sonnik.png'),
           load_image(r'enemies\Pinky.png'),
           load_image(r'enemies\Inky.png'),
           load_image(r'enemies\Clyde.png'),
           load_image(r'enemies\Blinky.png'),
           load_image(r'enemies\sword.png'),
           load_image(r'enemies\barrel.png'),
           load_image(r'enemies\ball with thorns.png')]

lose = False  # экраны проигрышей
lose_files = [(pygame.mixer.Sound(r'data\game over\mario\0.ogg'), load_image(r'game over\mario\1.png')),
              (pygame.mixer.Sound(r'data\game over\wastedGTA5\0.ogg'), load_image(r'game over\wastedGTA5\1.png')),
              (None, load_image(r'game over\wastedSA\1.png')),
              (pygame.mixer.Sound(r'data\game over\loser\0.ogg'), (load_image(r'game over\loser\1.png'))),
              (pygame.mixer.Sound(r'data\game over\darkSouls\0.ogg'), load_image(r'game over\darkSouls\1.png')),
              (pygame.mixer.Sound(r'data\game over\GO\0.ogg'), load_image(r'game over\GO\1.png')),
              (None, load_image(r'game over\minecraft\0.png')),
              (None, load_image(r'game over\minecraft\1.png')),
              (None, load_image(r'game over\minecraft\2.png'))]
groupLose = pygame.sprite.Group()

TIMER = 25
pygame.time.set_timer(TIMER, 1000)
timer = Timer(all_obstacles)

SPAWN_BOSS = 26  # Боссы
pygame.time.set_timer(SPAWN_BOSS, 9000)
BOSSES = [Boss1(all_bosses, all_obstacles,
                (load_image(r'bosses\Pacman\0.png'),
                 load_image(r'bosses\Pacman\1.png'),
                 load_image(r'bosses\Pacman\2.png')),
                pygame.mixer.Sound(r'data\bosses\Pacman\0.ogg')),
          Boss2(all_bosses, all_obstacles, load_image(r'bosses\hail of arrows\arrow.png'), timer,
                pygame.mixer.Sound(r'data\bosses\hail of arrows\0.ogg')),
          Boss3(all_bosses, all_obstacles,
                (load_image(r'bosses\Mario\0.png'),
                 load_image(r'bosses\Mario\1.png'),
                 load_image(r'bosses\Mario\2.png')),
                (pygame.mixer.Sound(r'data\bosses\Mario\mario.ogg'),
                 pygame.mixer.Sound(r'data\bosses\Mario\mushroom.ogg')))]
boss = None

ANIMATION = 27  # анимация
pygame.time.set_timer(ANIMATION, 200)

MUSIC = 28  # музыка
pygame.mixer.music.set_endevent(MUSIC)
music = [r'data\music0.mp3', r'data\music1.mp3']
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.load(music[0])
pygame.mixer.music.play()
i_music = 0

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:               # выход
            terminate()
        elif event.type == MUSIC:                   # запуск музыки повторно
            i_music += 1
            i_music %= len(music)
            pygame.mixer.music.load(music[i_music])
            pygame.mixer.music.play()
        if GAMING:                                  # эвенты если игра идёт
            if event.type == pygame.MOUSEMOTION:    # движение персонажа по горизонтали
                person.motion(event.pos)
            elif event.type == ANIMATION:           # анимация
                person.animation()
                all_bosses.update('anim')
            elif event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                person.jump()                       # прыжок
            elif event.type == SPAWN_ENEMIES:       # спавн миньонов
                for x in range(0, WIDTH, 80):
                    Enemies(all_obstacles, all_enemies, enemies, x, HEIGHT)
                for x in range(0, WIDTH, 80):
                    Enemies(all_obstacles, all_enemies, enemies, x, -50)
                for y in range(0, HEIGHT, 80):
                    Enemies(all_obstacles, all_enemies, enemies, -50, y)
                for y in range(0, HEIGHT, 80):
                    Enemies(all_obstacles, all_enemies, enemies, WIDTH, y)
            elif event.type == TIMER:
                timer.update()
                if timer.timer == 999:              # при достижении 999 секунд вы проигрываете
                    pygame.mixer.music.pause()
                    lose = True
                    GameOver(groupLose, choice(lose_files))
                    person.lose()
                    pygame.mouse.set_visible(True)
                    GAMING = False
                if timer.timer % 9 == 0 and timer.timer != 0:  # спавн босса
                    boss = choice(BOSSES)
                    boss.start()
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and QuiT.rect.collidepoint(event.pos):
                close = True        # проверка, что вы нажали на выход
            elif event.type == pygame.MOUSEBUTTONUP and QuiT.rect.collidepoint(event.pos) and close:
                terminate()         # проверка, что вы отпустили кнопку выход
            elif event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                pygame.mixer.music.unpause()
                pygame.mouse.set_visible(False)         # запуск игры заново
                GAMING = True
                lose = False
                timer.again()
                for spr in all_enemies:
                    spr.kill()
                groupLose.update()
                all_bosses.update('stop')
                person.rect.y = 320
                person.rect.x = 180
                pygame.mouse.set_pos(180, 320)
    screen.fill((255, 255, 255))
    Person_group.draw(screen)
    all_obstacles.draw(screen)
    if GAMING:
        if pygame.sprite.spritecollideany(person, all_obstacles):   # проверка столкновения персонажа со всеми объектами
            for spr in pygame.sprite.spritecollide(person, all_obstacles, False):
                if pygame.sprite.collide_mask(person, spr):
                    GAMING = False
        elif person.rect.y > HEIGHT - 32 or person.rect.y < 0:      # проверка, что персонаж не вылетел за поле
            GAMING = False
        if boss is not None:                                        # уничтожение миньёнов, столкнувшихся с боссом
            for spr in pygame.sprite.spritecollide(boss, all_enemies, False):
                if pygame.sprite.collide_mask(boss, spr):
                    spr.kill()
        all_enemies.update()
        person.update()
        all_bosses.update(0)
        if not GAMING:  # проигрыш
            pygame.mixer.music.pause()
            lose = True
            GameOver(groupLose, choice(lose_files))
            person.lose()
            pygame.mouse.set_visible(True)
    else:
        screen.blit(fon, (0, 0))            # рисование фона, текста, проигрыша
        screen.blit(text, (35, 580))
        if lose:
            groupLose.draw(screen)
    quit_group.update()
    quit_group.draw(screen)
    pygame.display.flip()
    clock.tick(50)
