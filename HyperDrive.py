import pygame
import random
import time
import math

from common import BaseSprite, FrameCounter

max_mass = 2500
screen_size = (800, 600)


class Star(BaseSprite):
    brightness_range = [63, 255]
    containers = []

    def __init__(self, position, angle, speed, size=3, twinkle=False):
        BaseSprite.__init__(self, self.containers)

        self.position = position
        self.angle = angle
        self.speed = speed
        self.twinkle = twinkle

        self.rect = pygame.Rect(position, (size, size))
        self.image = pygame.Surface((size, size))
        self.size = size

        self.image.fill((255, 255, 255))

    def set_size(self, size):
        self.size = size

        self.rect.height = self.rect.width = size
        self.image = pygame.Surface((size, size))
        self.image.fill((255, 255, 255))

    def update_dt(self, dt):
        if dt == 0:
            return

        self.dirty = 1

        # collision = pygame.sprite.spritecollideany(self, self.containers[0])
        collision = False

        if collision:
            reflection_plane = (self.angle + collision.angle) / 2
            self.angle = reflection_plane - (self.angle - reflection_plane)
            collision.angle = reflection_plane - (collision.angle - reflection_plane)

            m_self = self.speed*self.size**2
            m_col = collision.speed * collision.size**2
            m_avg = (m_self + m_col)/2

            self.speed = m_avg / self.size**2
            collision.speed = m_avg / collision.size**2

            # combine if small enough

            if collision.size + 2 <= self.size:
                collision.kill()
                self.set_size(math.sqrt(self.size**2 + collision.size**2))


        x, y = self.position
        x += self.speed * dt * math.cos(math.radians(self.angle))
        y += self.speed * dt * math.sin(math.radians(self.angle))
        self.rect.center = self.position = (x, y)

        if self.twinkle:
            b = random.randint(self.brightness_range[0], self.brightness_range[1])
            self.image.fill((b, b, b))

        if (x < -self.size / 2 or x > screen_size[0] + self.size / 2) or \
            (y < -self.size / 2 or y > screen_size[1] + self.size / 2):
            self.kill()

        # print(self.rect.center)


class Stars(pygame.sprite.RenderUpdates):
    def get_total_mass(self):
        total_mass = 0
        for s in self.sprites():
            total_mass += s.size**2
        return total_mass


def make_star():
    x = random.randint(0, screen_size[0])
    y = random.randint(0, screen_size[1])

    # angle = random.randint(0, 360)
    angle = math.degrees(math.atan2(y - screen_size[1]/2, x - screen_size[0]/2))

    size = random.randint(1, 7)
    speed = 20*size

    Star((x, y), angle, speed, size=size, twinkle=False)


def main():
    pygame.init()
    screen = pygame.display.set_mode(screen_size)

    stars = Stars()
    Star.containers.append(stars)

    counter = FrameCounter()

    while stars.get_total_mass() < max_mass:
        make_star()

    try:
        while not pygame.event.peek(pygame.QUIT):
            pygame.event.poll()
            while stars.get_total_mass() < max_mass:
                make_star()

            screen.fill((0, 0, 0))

            stars.update()
            stars.draw(screen)

            counter.update()
            # counter.image.blit(screen, counter.rect)
            screen.blit(counter.image, counter.rect)
            pygame.display.flip()
    except KeyboardInterrupt:
        pass

    print("Quitting...")


if __name__ == "__main__":
    main()
