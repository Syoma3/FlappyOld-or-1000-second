import pygame
from random import choice, randrange

WIDTH = 360
HEIGHT = 640


def blitRotate(image, originPos, angle):
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


class Person(pygame.sprite.Sprite):
    def __init__(self, group, ims, im_lose, music):
        super().__init__(group)
        self.music = music
        self.im_lose = im_lose
        self.ims = ims
        self.image = ims[1]
        self.rect = ims[1].get_rect()
        self.k = -1
        self.anim = 0
        self.orientation = True
        self.rect.x = 180
        self.rect.y = 320
        self.mask = pygame.mask.from_surface(self.image)
        self.i = 0

    def motion(self, pos):
        if self.rect.x - pos[0] < 0:
            self.orientation = True
        else:
            self.orientation = False
        self.rect.x = pos[0]

    def jump(self):
        self.k = 0

    def lose(self):
        choice(self.music).play()
        if self.orientation:
            self.image = self.im_lose
        else:
            self.image = pygame.transform.flip(self.im_lose, True, False)

    def update(self, *arg):
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

    def animation(self):
        self.i += 1
        self.i %= len(self.ims)
        self.image = self.ims[self.i]
        if not self.orientation:
            self.image = pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)


class Enemies(pygame.sprite.Sprite):
    def __init__(self, all_obstacles, group, ims, x, y):
        super().__init__(group, all_obstacles)
        self.im = choice(ims)
        self.image = self.im
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move = (randrange(-3, 4, 2), randrange(-3, 4, 2))
        self.angle = -2
        self.side = 1
        self.x = x
        self.y = y
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *arg):
        if -100 < self.rect.x < WIDTH + 100 and -100 < self.rect.y < HEIGHT + 100:
            pass
        else:
            self.kill()
        self.image = blitRotate(self.im, self.rect.center, self.angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.angle -= self.side
        self.x += self.move[0]
        self.y += self.move[1]
        self.rect.x = self.x
        self.rect.y = self.y


class Timer(pygame.sprite.Sprite):
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


class GameOver(pygame.sprite.Sprite):
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
    def __init__(self, group, all_obstacles, ims):
        super().__init__(group, all_obstacles)
        self.i = 0
        self.image = ims[self.i]
        self.ims = ims
        self.rect = self.image.get_rect()
        self.work = False
        self.v = 5
        self.orientation = False
        self.rect.x = -400
        self.mask = pygame.mask.from_surface(self.image)

    def start(self):
        self.work = True

    def update(self, *args):
        if self.work and args[0] == 'stop':
            self.stop()
        elif self.work and args[0] == 'anim':
            self.anim()
        elif self.work:
            self.rect.x += self.v
            if self.rect.x == WIDTH:
                self.v = -self.v
                self.rect.y = HEIGHT - 400
                self.orientation = True
            if self.rect.x < -400:
                self.stop()

    def stop(self):
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
    def __init__(self, group, all_obstacles, ims, timer):
        super().__init__(all_obstacles, group)
        self.timer = timer
        self.image = ims
        self.rect = self.image.get_rect()
        self.rect.y = -100
        self.v = 20
        self.k = 0
        self.work = False
        self.mask = pygame.mask.from_surface(self.image)

    def start(self):
        self.work = True
        self.begin = self.timer.timer

    def stop(self):
        self.work = False
        self.rect.y = -100

    def update(self, *args):
        if self.work and ((self.timer.timer % 9 == 0 and self.timer.timer != self.begin) or args[0] == 'stop'):
            self.stop()
        elif self.work:
            if self.rect.y > HEIGHT:
                self.rect.y = -45
                self.rect.x = randrange(0, WIDTH)
                self.k += 1
            self.rect.y += self.v


class Boss3(pygame.sprite.Sprite):
    def __init__(self, all_bosses, all_obstacles, ims):
        super().__init__(all_obstacles, all_bosses)
        self.ims = ims
        self.image = self.ims[0]
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + 33
        self.rect.y = HEIGHT - 154
        self.work = False
        self.mask = pygame.mask.from_surface(self.image)

    def star(self):
        self.work = True

    def stop(self):
        self.image = self.ims[0]
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + 33
        self.rect.y = HEIGHT - 154
        self.work = False
        self.mask = pygame.mask.from_surface(self.image)
