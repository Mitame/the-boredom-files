import pygame
import random
import time
import math

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

def multiline_font_render(font, text, antialias=True, colour=(255,255,255), justification="left", *args, **kwargs):
    line_sizes = []

    width = 0
    height = 0
    for line in text.split("\n"):
        size = font.size(line)
        line_sizes.append(size)
        width = max(width, size[0])
        height += size[1]

    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    y = 0
    for line in text.split("\n"):
        line_surf = font.render(line, antialias, colour, *args, **kwargs)
        if justification == "left":
            line_rect = line_surf.get_rect(left=0, y=y)
        elif justification == "center":
            line_rect = line_surf.get_rect(centerx=width//2, y=y)
        elif justification == "right":
            line_rect = line_surf.get_rect(right=width, y=y)
        else:
            raise ValueError("'%s' is not a valid justification." % justification)

        surf.blit(line_surf, line_rect)

        y += line_rect.height
    return surf

class BaseSprite(pygame.sprite.DirtySprite):
    containers = []
    def __init__(self, *args, **kwargs):
        pygame.sprite.Sprite.__init__(self, self.containers, *args, **kwargs)
        self.last_update = -1

    def update(self):
        pygame.sprite.Sprite.update(self)

        cur_time = time.time()

        if self.last_update == -1:
            self.update_dt(0)
        else:
            self.update_dt(cur_time-self.last_update)

        self.last_update = cur_time

    def update_dt(self, dt):
        pass

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


class FrameCounter(BaseSprite):
    containers = []

    def __init__(self):
        BaseSprite.__init__(self)
        self.draw_times = [0]*600

        self.avg_60f = 0
        self.avg_120f = 0
        self.avg_600f = 0
        self.frame = 0

        self.font = pygame.font.SysFont("Ubuntu Mono", 12)
        self.update_image()

    def update_dt(self, dt):
        self.draw_times.append(dt)
        self.draw_times = self.draw_times[-600:-1] + [self.draw_times[-1]]

        if sum(self.draw_times[-60:-1]) == 0:
            return

        self.frame += 1
        self.avg_60f = 60/sum(self.draw_times[-60:-1] + [self.draw_times[-1]])
        self.avg_120f = 120/sum(self.draw_times[-120:-1] + [self.draw_times[-1]])
        self.avg_600f = 600/sum(self.draw_times[-600:-1] + [self.draw_times[-1]])

        self.update_image()


    def update_image(self):
        text = "%i\n%.0f/60\n%.0f/120\n%.0f/600" % (self.frame, self.avg_60f, self.avg_120f, self.avg_600f)
        # self.image = self.font.render(text, True, (255,255,255))
        self.image = multiline_font_render(self.font, text, justification="right")
        self.rect = self.image.get_rect(topright=(screen_size[0], 0))


class SpriteCounter(FrameCounter):
    def __init__(self):
        self.counts = {}
        FrameCounter.__init__(self)

    def update_counts(self, counts):
        self.counts = counts

    def update_image(self):
        text = "%i/frame\n%.0f/60\n%.0f/120\n%.0f/600" % (self.frame, self.avg_60f, self.avg_120f, self.avg_600f)
        for name, count in self.counts.items():
            text += "\n%i/%s" % (count, name)

        self.image = multiline_font_render(self.font, text, justification="right")
        self.rect = self.image.get_rect(topright=(screen_size[0], 0))


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
