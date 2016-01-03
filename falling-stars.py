import pygame
import random
import time
import math

from common import SpriteCounter, BaseSprite

max_mass = 2500
screen_size = (800, 600)


def draw_star(points, size, point_length=0.5):
    polygon = []
    for n in range(points*2):
        if n % 2 == 0:
            x = math.sin(2*math.pi*n/points/2)*size/2 + size/2 - 1
            y = math.cos(2*math.pi*n/points/2)*size/2 + size/2 - 1
        else:
            x = math.sin(2*math.pi*n/points/2)*size/2*(1-point_length) + size/2
            y = math.cos(2*math.pi*n/points/2)*size/2*(1-point_length) + size/2
            pass
        polygon.append((x, y))

    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    # surf.fill((255,0,0))
    pygame.draw.polygon(surf, (255,255,255), polygon, 0)
    return surf


class Star(BaseSprite):
    brightness_range = [63, 255]
    containers = []

    debris_count = 10 # on avg, debris emitted per second
    explode_debris_count = 20

    def __init__(self, position, angle, speed, size=3, twinkle=False):
        BaseSprite.__init__(self)

        self.position = position

        self.speed = speed
        self.twinkle = twinkle

        self.set_angle(angle)

        self.rect = pygame.Rect(position, (size, size))
        # self.image = pygame.Surface((0,0))
        self.image = draw_star(5, size)
        self.orig_size = size
        self.size = size

        # self.image.fill((255, 255, 255))
    def set_angle(self, angle):
        self.angle = angle
        self.dx = self.speed * math.cos(math.radians(self.angle))
        self.dy = self.speed * math.sin(math.radians(self.angle))

    def set_size(self, size):
        temp = self.size
        self.size = size

        self.rect.height = self.rect.width = size
        self.rect.center = self.position

        if int(self.size) != int(temp) or True:
            self.image = draw_star(5, self.size)
            # self.image.fill((255, 255, 255))

    def kill(self):
        BaseSprite.kill(self)
        if self.explode_debris_count:
            for n in range(self.explode_debris_count):
                # angle = random.randint(0, 360)
                angle = random.randint(0, 360)

                size = random.randint(1, self.orig_size//3) if self.orig_size >= 3 else 1
                speed = random.randint(100, 200)

                Debris(self.position, angle, speed, size=size, twinkle=False)

    def update_dt(self, dt):
        if dt == 0:
            return

        if self.debris_count and (dt * random.random() * self.debris_count > dt/self.debris_count):
            Debris(
                self.position,
                self.angle+random.randint(180-int(self.size)*5,180+int(self.size)*5),
                self.speed/2-10+random.random()*20,
                size=self.size/3-1+random.random()*2,
                twinkle=self.twinkle
            )
            self.set_size(self.size - 0.01)

        if self.size < 1:
            self.kill()

        x, y = self.position
        if self.speed:
            self.dirty = 1
            x += self.dx * dt
            y += self.dy * dt
            self.rect.center = self.position = (x, y)

        if self.twinkle:
            self.dirty = 1
            b = random.randint(self.brightness_range[0], self.brightness_range[1])
            self.image.fill((b, b, b))


        update_angle = False
        if (self.rect.left < 0 and self.dx < 0) \
          or (self.rect.right > screen_size[0] and self.dx > 0):
            self.dx *= -1
            update_angle = True

        if (self.rect.top < 0 and self.dy < 0) \
          or (self.rect.bottom > screen_size[1] and self.dy > 0):
            self.dy *= -1
            update_angle = True

        if update_angle:
            self.angle = math.degrees(math.atan2(self.dy, self.dx))

        # print(self.rect.center)


class Debris(Star):
    degrade_speed = 3
    containers = []
    debris_count = 0
    explode_debris_count = 0

    def __init__(self, position, angle, speed, size=3, twinkle=False):
        BaseSprite.__init__(self)

        self.position = position
        self.speed = speed
        self.twinkle = twinkle

        self.set_angle(angle)

        self.rect = pygame.Rect(position, (size, size))
        self.image = pygame.Surface((size, size))
        # self.image = draw_star(5, size)

        self.image.fill((255,255,255))
        self.size = size

    def update_dt(self, dt):
        prev_size = self.size

        self.size -= self.degrade_speed * dt
        if self.size < 1:
            self.kill()
        elif int(prev_size) != int(self.size):
            self.update_image()


        if self.speed != 0:
            self.speed -= self.degrade_speed * dt
            if self.speed < 0:
                self.speed = 0

        Star.update_dt(self, dt)

    def update_image(self):
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 255, 255))


def make_star():
    x = random.randint(0, screen_size[0])
    y = random.randint(0, screen_size[1])

    angle = random.randint(0, 360)
    # angle = math.degrees(math.atan2(y - screen_size[1]/2, x - screen_size[0]/2))

    size = random.randint(5, 20)
    speed = random.randint(100, 200)

    Star((x, y), angle, speed, size=size, twinkle=False)


def main():
    pygame.init()
    screen = pygame.display.set_mode(screen_size)

    all_sprites = pygame.sprite.RenderUpdates()
    stars = pygame.sprite.RenderUpdates()
    debris = pygame.sprite.RenderUpdates()

    Star.containers = [stars, all_sprites]
    Debris.containers = [debris, all_sprites]

    for z in range(1):
        make_star()
        # Star((200,200), 45, 0, size=200)

    counter = SpriteCounter()

    try:
        while not pygame.event.peek(pygame.QUIT):
            # pygame.event.poll()

            for event in pygame.event.get(pygame.KEYDOWN):
                if event.unicode == "s":
                    make_star()

            pygame.event.clear()

            screen.fill((0, 0, 0))

            # stars.update()
            # stars.draw(screen)
            #
            # debris.update()
            # debris.draw(screen)
            # if pygame.mouse.get_pressed()[0]:
            #     mouse_pos = pygame.mouse.get_pos()
            #     for star in stars:
            #         dx = mouse_pos[0] - star.rect.centerx
            #         dy = mouse_pos[1] - star.rect.centery
            #         angle = math.degrees(math.atan2(dy, dx))
            #         dangle = angle - star.angle
            #         star.set_angle(star.angle + dangle * 0.01)

            all_sprites.update()
            all_sprites.draw(screen)

            counter.update_counts({
                "debris": len(debris),
                "stars": len(stars),
                "all": len(all_sprites)
            })
            counter.update()

            screen.blit(counter.image, counter.rect)
            pygame.display.flip()
    except KeyboardInterrupt:
        pass

    print("Quitting...")


if __name__ == "__main__":
    main()
