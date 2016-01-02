import pygame
import random
import time
import math

max_mass = 2500
screen_size = (800, 600)


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
