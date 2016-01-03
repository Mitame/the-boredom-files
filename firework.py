import pygame
import random
import time
import math

from common import SpriteCounter, BaseSprite

max_mass = 2500
screen_size = (800, 600)
colours = [
    "#8e946eff",
    "#795e55ff",
    "#d8a57aff",
    "#b4d1d5ff",
    "#008fadff",
    "#354894ff",
    "#f5c4caff",
    "#df4f66ff",
    "#a04a6dff",
    "#db487eff",
    "#b35d68ff",
    "#dec8ecff",
    "#725782ff",
    "#cf734aff",
    "#fe8453ff",
    "#cf734aff",
    "#635c56ff",
    "#ae956cff",
    "#555a5dff",
    "#b5b6baff",
    "#ffe89eff",
    "#7ad3b7ff",
    "#79a1a9ff",
    "#f28e7fff"
]

def get_random_colour():
    i = random.randint(0, len(colours) - 1)
    return pygame.Color(colours[i])


class Debris(BaseSprite):
    degrade_speed = 3
    containers = []
    debris_count = 0
    explode_debris_count = 0

    def __init__(self, position, angle, speed, size=3, colour=(255, 255, 255)):
        BaseSprite.__init__(self)

        self.position = position
        self.speed = speed
        self.colour = colour

        self.set_angle(angle)

        self.rect = pygame.Rect(position, (size, size))
        self.image = pygame.Surface((size, size))
        # self.image = draw_star(5, size)
        self.image.fill(colour)
        self.size = size

    def set_angle(self, angle):
        self.angle = angle
        self.dx = self.speed * math.cos(math.radians(self.angle))
        self.dy = self.speed * math.sin(math.radians(self.angle))

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

        # apply gravity
        self.dy += 9.81*dt*75  # 75px is a meter because YOLO

        x, y = self.position
        if self.speed:
            self.dirty = 1
            x += self.dx * dt
            y += self.dy * dt
            self.rect.center = self.position = (x, y)

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

    def update_image(self):
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(self.colour)


class Emitter(BaseSprite):
    containers = []

    def __init__(self, position, angle, emit_speed_range=(100, 500)):
        BaseSprite.__init__(self)
        self.position = position
        self.angle = angle
        self.emit_speed_range = emit_speed_range

        self.image = pygame.Surface((5,5))
        self.image.fill((255,255,255))

        self.rect = self.image.get_rect(center=self.position)

    def update_dt(self, dt):
        speed = random.randint(*self.emit_speed_range)
        size = random.randint(1, 5)
        angle = self.angle + random.randint(-30, 30)
        colour = get_random_colour()

        Debris(self.position, angle, speed, size=size, colour=colour)


def main():
    pygame.init()
    screen = pygame.display.set_mode(screen_size)

    all_sprites = pygame.sprite.RenderUpdates()
    # stars = pygame.sprite.RenderUpdates()
    fworks = pygame.sprite.RenderUpdates()
    debris = pygame.sprite.RenderUpdates()

    # Star.containers = [stars, all_sprites]
    Emitter.containers = [fworks, all_sprites]
    Debris.containers = [debris, all_sprites]

    # Emitter((200,200), -90)

    counter = SpriteCounter()

    start_point = (0, 0)

    try:
        while not pygame.event.peek(pygame.QUIT):
            # pygame.event.poll()

            for event in pygame.event.get(pygame.KEYDOWN):
                if event.unicode == "s":
                    make_star()

            for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
                if event.button == 1:
                    start_point = event.pos

            for event in pygame.event.get(pygame.MOUSEBUTTONUP):
                if event.button == 1:
                    dx = event.pos[0] - start_point[0]
                    dy = event.pos[1] - start_point[1]
                    max_speed = int(math.sqrt(dy**2 + dx**2))*10
                    Emitter((start_point), math.degrees(math.atan2(dy, dx)), emit_speed_range=(max_speed//5, max_speed))


            pygame.event.clear()

            screen.fill((0, 0, 0))

            all_sprites.update()
            all_sprites.draw(screen)

            if pygame.mouse.get_pressed()[0]:
                pygame.draw.aaline(screen, (255,0,255), start_point, pygame.mouse.get_pos())

            counter.update_counts({
                "debris": len(debris),
                "stars": len(fworks),
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
