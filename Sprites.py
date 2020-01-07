import pygame
from random import choice, randrange

WIDTH = 360
HEIGHT = 640


def blitRotate(image, originPos, angle):    # поворот изображения
    w, h = image.get_size()
    box = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]
    min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])
    pivot = pygame.math.Vector2(originPos[0], -originPos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move = pivot_rotate - pivot
    rotated_image = pygame.transform.rotate(image, angle)
    return rotated_image


class Person(pygame.sprite.Sprite):     # персонаж
    def __init__(self, group, ims, im_lose, sounds):
        super().__init__(group)
        self.sounds = sounds                                # звуки умирания
        self.im_lose = im_lose                              # избражение при проигрыше
        self.ims = ims                                      # изображения
        self.image = ims[1]
        self.rect = ims[1].get_rect()
        self.k = -1                                         # переменная для прыжка
        self.anim = 0
        self.orientation = True                             # орентация (вправо, влево)
        self.rect.x = 180
        self.rect.y = 320
        self.mask = pygame.mask.from_surface(self.image)
        self.i = 0                                          # переменная для анмации

    def motion(self, pos):   # движение по горизонтали
        if self.rect.x - pos[0] < 0:
            self.orientation = True
        else:
            self.orientation = False
        self.rect.x = pos[0]

    def jump(self):         # задаём, что прыжок начат
        self.k = 0

    def lose(self):         # функция для проигрыша
        choice(self.sounds).play()                          # выбор звука при проигрыше
        if self.orientation:
            self.image = self.im_lose
        else:
            self.image = pygame.transform.flip(self.im_lose, True, False)

    def update(self, *arg):  # прыжок и падение
        if 0 <= self.k <= 24:
            self.k += 2
            self.rect.y -= 2
        elif 24 <= self.k <= 32:
            self.k += 1
            self.rect.y -= 2
        else:
            self.k = -1
        if self.k == -1:
            self.rect.y += 1
        self.mask = pygame.mask.from_surface(self.image)

    def animation(self):  # анимация
        self.i += 1
        self.i %= len(self.ims)
        self.image = self.ims[self.i]
        if not self.orientation:
            self.image = pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)


class Enemies(pygame.sprite.Sprite):    # миньон
    def __init__(self, all_obstacles, group, ims, x, y):
        super().__init__(group, all_obstacles)
        self.im = choice(ims)
        self.image = self.im
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move = (randrange(-3, 4, 2), randrange(-3, 4, 2))  # скорость
        self.angle = -2
        self.x = x
        self.y = y
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *arg):
        if -100 < self.rect.x < WIDTH + 100 and -100 < self.rect.y < HEIGHT + 100:
            pass
        else:
            self.kill()
        self.image = blitRotate(self.im, self.rect.center, self.angle)  # поворот картинки
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.angle -= 1
        self.x += self.move[0]
        self.y += self.move[1]
        self.rect.x = self.x
        self.rect.y = self.y


class Timer(pygame.sprite.Sprite):  # таймер
    def __init__(self, group):
        super().__init__(group)
        self.timer = 0
        line = str(self.timer).rjust(3, '0')
        self.font = pygame.font.Font(r'data\font.ttf', 50)
        number = self.font.render(line, 0, (0, 0, 0))
        self.image = number
        self.rect = self.image.get_rect()
        self.rect.x = 160
        self.rect.y = 0
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):
        self.timer += 1
        line = str(self.timer).rjust(3, '0')
        number = self.font.render(line, 0, (0, 0, 0))
        self.image = number
        self.mask = pygame.mask.from_surface(self.image)

    def again(self):
        self.timer = 0


class GameOver(pygame.sprite.Sprite):   # экран поражения
    def __init__(self, group, files):
        super().__init__(group)
        self.image = files[1]
        self.rect = self.image.get_rect()
        self.rect.y = 214
        self.music = files[0]
        if self.music is not None:
            self.music.play()

    def update(self, *args):
        if self.music is not None:
            self.music.stop()
        self.kill()


class Boss1(pygame.sprite.Sprite):  # Pacman
    def __init__(self, group, all_obstacles, ims, sounds):      # Как устроенны боссы сложно понять, но возможно:
        super().__init__(group, all_obstacles)                  # В главном фаиле я создал список, в котором 3 класса
        self.i = 0                                              # спрайтов. Они существуют сразу же после запуска игры,
        self.sounds = sounds                                    # но начанают работать только каждые 9 секунд.
        self.image = ims[self.i]                                # в каждом есть функции: анимация, запуск, остановка и
        self.ims = ims                                          # и update
        self.rect = self.image.get_rect()
        self.work = False
        self.v = 5
        self.orientation = False
        self.rect.x = -400
        self.mask = pygame.mask.from_surface(self.image)

    def start(self):
        self.work = True
        self.sounds.play()

    def update(self, *args):
        if self.work:
            if args[0] == 'stop':
                self.stop()
            elif args[0] == 'anim':
                self.anim()
            else:
                self.rect.x += self.v
                if self.rect.x == WIDTH:
                    self.v = -self.v
                    self.rect.y = HEIGHT - 400
                    self.sounds.play()
                    self.orientation = True
                if self.rect.x < -400:
                    self.stop()

    def stop(self):
        self.sounds.stop()
        self.work = False
        self.v = 5
        self.orientation = False
        self.rect.x = -400
        self.rect.y = 0

    def anim(self):
        self.i += 1
        self.i %= len(self.ims)
        self.image = self.ims[self.i]
        self.image = pygame.transform.flip(self.image, self.orientation, False)
        self.mask = pygame.mask.from_surface(self.image)


class Boss2(pygame.sprite.Sprite):  # Стрела
    def __init__(self, group, all_obstacles, ims, timer, sounds):       # обычная стрела просто летит постоянно сверху
        super().__init__(all_obstacles, group)
        self.sounds = sounds
        self.timer = timer
        self.image = ims
        self.rect = self.image.get_rect()
        self.rect.y = -100
        self.v = 20
        self.work = False
        self.mask = pygame.mask.from_surface(self.image)

    def start(self):
        self.work = True
        self.begin = self.timer.timer
        self.sounds.play()

    def stop(self):
        self.work = False
        self.rect.y = -100

    def update(self, *args):
        if self.work:
            if (self.timer.timer % 9 == 0 and self.timer.timer != self.begin) or args[0] == 'stop':
                self.stop()
            else:
                if self.rect.y > HEIGHT:
                    self.rect.y = -45
                    self.rect.x = randrange(0, WIDTH)
                    self.sounds.play()
                self.rect.y += self.v


class Boss3(pygame.sprite.Sprite):  # Mario
    def __init__(self, all_bosses, all_obstacles, ims, sounds):     # С Марио я решил заморочиться, если вы играли,
        super().__init__(all_obstacles, all_bosses)                 # то увидели бы. Но всё равно скажу: сначала Марио
        self.sounds = sounds                                        # идёт в центр и увеличивается будто под грибами.
        self.ims = ims                                              # Потом уменьшается и уходит за карту.
        self.i = 0                                                  # У него много действий и я решил разделить его
        self.image = self.ims[self.i]                               # движение на 4 этапа(stage): прогулка до центра,
        self.rect = self.image.get_rect()                           # увеличение, уменьшение, прогулка за карту.
        self.rect.x = -32
        self.rect.y = HEIGHT - self.rect.height
        self.work = False
        self.mask = pygame.mask.from_surface(self.image)
        self.stage = -1
        self.size = 0

    def start(self):
        self.work = True
        self.stage = 0
        self.sounds[0].play()

    def stop(self):
        self.image = self.ims[0]
        self.rect = self.image.get_rect()
        self.rect.x = -32
        self.rect.y = HEIGHT - self.rect.height
        self.work = False
        self.mask = pygame.mask.from_surface(self.image)
        self.stage = -1
        self.size = 0

    def anim(self):                 # это длинная анимация не такая уж и страшная. Марио есть Марио
        if self.stage == 0:
            self.i += 1
            self.i %= len(self.ims)
            self.image = self.ims[self.i]
            x = self.rect.x
            y = self.rect.y
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.mask = pygame.mask.from_surface(self.image)
            if self.rect.x != 32 * 5:
                self.rect.x += 16
            else:
                self.stage = 1
        elif self.stage == 1:
            if self.size == 0:
                self.image = pygame.transform.scale2x(self.ims[0])
                self.rect = self.image.get_rect()
                self.rect.x = (32 * 4.5)
                self.size += 1
                self.rect.y = HEIGHT - self.rect.height
                self.mask = pygame.mask.from_surface(self.image)
                self.sounds[1].play()
            elif self.size == 1:
                self.image = pygame.transform.scale2x(self.image)
                self.rect = self.image.get_rect()
                self.rect.x = int(32 * 3.5)
                self.size += 1
                self.rect.y = HEIGHT - self.rect.height
                self.mask = pygame.mask.from_surface(self.image)
            elif self.size == 2:
                self.image = pygame.transform.scale2x(self.image)
                self.rect = self.image.get_rect()
                self.rect.x = int(32 * 1.5)
                self.size += 1
                self.rect.y = HEIGHT - self.rect.height
                self.mask = pygame.mask.from_surface(self.image)
            elif self.size == 3:
                self.image = pygame.transform.scale2x(self.image)
                self.rect = self.image.get_rect()
                self.rect.x = int(32 * -2)
                self.size += 1
                self.stage += 1
                self.rect.y = HEIGHT - self.rect.height
                self.mask = pygame.mask.from_surface(self.image)
        elif self.stage == 2:
            if self.size == 4:
                self.image = pygame.transform.scale2x(self.ims[0])
                self.image = pygame.transform.scale2x(self.image)
                self.image = pygame.transform.scale2x(self.image)
                self.rect = self.image.get_rect()
                self.rect.x = int(32 * 1.5)
                self.size -= 1
                self.rect.y = HEIGHT - self.rect.height
                self.mask = pygame.mask.from_surface(self.image)
            elif self.size == 3:
                self.image = pygame.transform.scale2x(self.ims[0])
                self.image = pygame.transform.scale2x(self.image)
                self.rect = self.image.get_rect()
                self.rect.x = int(32 * 2.5)
                self.size -= 1
                self.rect.y = HEIGHT - self.rect.height
                self.mask = pygame.mask.from_surface(self.image)
            elif self.size == 2:
                self.image = pygame.transform.scale2x(self.ims[0])
                self.rect = self.image.get_rect()
                self.rect.x = int(32 * 4.5)
                self.size -= 1
                self.rect.y = HEIGHT - self.rect.height
                self.mask = pygame.mask.from_surface(self.image)
            elif self.size == 1:
                self.image = self.ims[0]
                self.rect = self.image.get_rect()
                self.rect.x = 32 * 5
                self.rect.y = HEIGHT - self.rect.height
                self.size -= 1
                self.stage += 1
                self.mask = pygame.mask.from_surface(self.image)
        elif self.stage == 3:
            self.i += 1
            self.i %= len(self.ims)
            self.image = self.ims[self.i]
            x = self.rect.x
            y = self.rect.y
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.mask = pygame.mask.from_surface(self.image)
            if self.rect.x < WIDTH + 32:
                self.rect.x += 16
            else:
                self.stop()

    def update(self, *args):
        if self.work:
            if args[0] == 'anim':
                self.anim()
            elif args[0] == 'stop':
                self.stop()
